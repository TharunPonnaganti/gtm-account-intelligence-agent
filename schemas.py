"""Typed data structures passed between the retriever, agent, and evaluator."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RetrievedChunk:
    """A single piece of grounding evidence returned by the retriever."""

    source: str          # where it came from (filename, URL, etc.)
    text: str            # the chunk content
    score: float         # retrieval relevance score (higher = more relevant)

    def citation(self) -> str:
        snippet = self.text.strip().replace("\n", " ")
        if len(snippet) > 160:
            snippet = snippet[:157] + "..."
        return f"[{self.source}] {snippet}"


@dataclass
class AgentResult:
    """The agent's grounded answer plus the evidence and steps behind it."""

    question: str
    answer: str
    evidence: list[RetrievedChunk] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)   # a trace of what the agent did

    def evidence_block(self) -> str:
        if not self.evidence:
            return "(no evidence retrieved)"
        return "\n".join(f"- {c.citation()}" for c in self.evidence)


@dataclass
class EvaluationResult:
    """The evaluator's reliability judgment of an AgentResult."""

    score: float                     # 0.0–1.0 grounding/faithfulness score
    rationale: str                   # why the evaluator gave that score
    unsupported_claims: list[str] = field(default_factory=list)
    needs_human_review: bool = True

    def summary(self) -> str:
        flag = "NEEDS HUMAN REVIEW" if self.needs_human_review else "OK to proceed"
        return f"Reliability: {self.score:.2f} — {flag}"
