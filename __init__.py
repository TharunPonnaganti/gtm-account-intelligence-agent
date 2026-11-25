"""GTM Account Intelligence Agent.

An agentic application that researches a go-to-market account, grounds its
reasoning in retrieved source material (RAG), and scores its own output for
reliability before a human reviews it.
"""

from .agent import GTMAgent
from .evaluator import evaluate
from .retriever import Retriever
from .schemas import AgentResult, EvaluationResult, RetrievedChunk

__all__ = [
    "GTMAgent",
    "Retriever",
    "evaluate",
    "AgentResult",
    "EvaluationResult",
    "RetrievedChunk",
]
