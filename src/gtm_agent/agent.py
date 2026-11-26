"""The agentic workflow.

The agent is given a `retrieve` tool backed by the RAG retriever. It decides,
step by step, what to look up, calls the tool, reads the grounding evidence, and
only then writes a decision-ready answer. This is the multi-step tool-use loop
rather than a single prompt.
"""

from __future__ import annotations

from .config import MAX_AGENT_STEPS, MAX_TOKENS, MODEL, get_client
from .retriever import Retriever
from .schemas import AgentResult, RetrievedChunk

SYSTEM_PROMPT = """You are a GTM (go-to-market) account-intelligence analyst.
Given an account and a question, research it in steps using the `retrieve` tool,
which returns grounded source material. Base every claim on retrieved evidence —
do not rely on prior knowledge or invent facts. When you have enough evidence,
write a concise, decision-ready answer for a sales/GTM team: key findings,
why they matter, and recommended next actions. If the evidence is thin, say so
explicitly rather than guessing."""

RETRIEVE_TOOL = {
    "name": "retrieve",
    "description": (
        "Search the account's source material for text relevant to a query. "
        "Returns the most relevant passages with their source. Call it multiple "
        "times with focused queries to gather evidence before answering."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A focused search query, e.g. 'recent funding' or 'tech stack'.",
            }
        },
        "required": ["query"],
    },
}


class GTMAgent:
    def __init__(self, retriever: Retriever) -> None:
        self.retriever = retriever
        self.client = get_client()

    def run(self, account: str, question: str) -> AgentResult:
        user_prompt = f"Account: {account}\nQuestion: {question}"
        messages: list[dict] = [{"role": "user", "content": user_prompt}]
        used_evidence: dict[str, RetrievedChunk] = {}   # dedupe by citation
        steps: list[str] = []

        for _ in range(MAX_AGENT_STEPS):
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                tools=[RETRIEVE_TOOL],
                messages=messages,
            )
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason != "tool_use":
                # The model produced a final answer.
                answer = "".join(
                    block.text for block in response.content if block.type == "text"
                ).strip()
                return AgentResult(
                    question=question,
                    answer=answer,
                    evidence=list(used_evidence.values()),
                    steps=steps,
                )

            # Handle every tool call in this turn, then feed results back.
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                query = block.input.get("query", "")
                chunks = self.retriever.retrieve(query, k=4)
                steps.append(f"retrieve('{query}') -> {len(chunks)} chunk(s)")
                for c in chunks:
                    used_evidence[c.citation()] = c
                rendered = (
                    "\n\n".join(c.citation() for c in chunks)
                    if chunks
                    else "No relevant source material found for that query."
                )
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": rendered,
                    }
                )
            messages.append({"role": "user", "content": tool_results})

        # Ran out of steps without a final answer.
        return AgentResult(
            question=question,
            answer="(The agent reached the step limit before concluding. "
            "Increase GTM_MAX_AGENT_STEPS or narrow the question.)",
            evidence=list(used_evidence.values()),
            steps=steps,
        )
