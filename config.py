"""Configuration and the shared Anthropic client.

The API key is read from the environment only. It is never hard-coded and never
committed. Locally it is loaded from a gitignored `.env` file.
"""

from __future__ import annotations

import os
from functools import lru_cache

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # loads .env when present; a no-op in deployed environments

# Model IDs evolve over time. Pin the current one in your .env via ANTHROPIC_MODEL;
# this default is only a fallback. See https://docs.claude.com for current IDs.
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")

# The evaluator can use a cheaper/faster model than the agent if you want.
EVAL_MODEL = os.environ.get("ANTHROPIC_EVAL_MODEL", MODEL)

MAX_TOKENS = int(os.environ.get("GTM_MAX_TOKENS", "1500"))
MAX_AGENT_STEPS = int(os.environ.get("GTM_MAX_AGENT_STEPS", "6"))

# Reliability threshold below which output is flagged for human review (0.0–1.0).
REVIEW_THRESHOLD = float(os.environ.get("GTM_REVIEW_THRESHOLD", "0.7"))


@lru_cache(maxsize=1)
def get_client() -> Anthropic:
    """Return a cached Anthropic client.

    Raises a clear error if the key is missing, rather than failing deep in an
    API call.
    """
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and add your "
            "key, or export it in your shell. Never commit the real key."
        )
    return Anthropic(api_key=key)
