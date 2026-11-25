"""AI output evaluation.

A dedicated pass that scores the agent's answer for faithfulness to the retrieved
evidence (is every claim grounded?), independent of the agent that produced it.
Low scores are flagged for human review. This is the reliability control that
keeps the agent trustworthy for real GTM decisions.
"""

from __future__ import annotations

import json
import re

from .config import EVAL_MODEL, REVIEW_THRESHOLD, get_client
from .schemas import AgentResult, EvaluationResult

EVAL_SYSTEM = """You are a strict evaluator of AI-generated analysis. You are given
a QUESTION, an ANSWER, and the EVIDENCE the answer was supposed to be grounded in.
Judge only whether the answer is faithful to the evidence — not whether it sounds
good. A claim is unsupported if it is not backed by the evidence, even if it is
plausibly true. Respond with ONLY a JSON object of this exact shape:
{"score": <float 0..1>, "rationale": "<one or two sentences>",
 "unsupported_claims": ["<claim>", ...]}
score 1.0 = every claim is grounded; 0.0 = little or nothing is grounded."""


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of the model's reply, defensively."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"Evaluator did not return JSON: {text!r}")
    return json.loads(match.group(0))


def evaluate(result: AgentResult) -> EvaluationResult:
    client = get_client()
    prompt = (
        f"QUESTION:\n{result.question}\n\n"
        f"ANSWER:\n{result.answer}\n\n"
        f"EVIDENCE:\n{result.evidence_block()}"
    )
    response = client.messages.create(
        model=EVAL_MODEL,
        max_tokens=600,
        system=EVAL_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = "".join(b.text for b in response.content if b.type == "text")

    try:
        data = _extract_json(raw)
        score = max(0.0, min(1.0, float(data.get("score", 0.0))))
        rationale = str(data.get("rationale", "")).strip()
        unsupported = [str(c) for c in data.get("unsupported_claims", [])]
    except (ValueError, json.JSONDecodeError) as exc:
        # Fail closed: if we can't parse a judgment, force human review.
        return EvaluationResult(
            score=0.0,
            rationale=f"Could not parse evaluator output ({exc}). Forcing review.",
            needs_human_review=True,
        )

    return EvaluationResult(
        score=score,
        rationale=rationale,
        unsupported_claims=unsupported,
        needs_human_review=score < REVIEW_THRESHOLD or bool(unsupported),
    )
