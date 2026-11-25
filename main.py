"""Command-line entry point for the GTM Account Intelligence Agent.

Usage:
    python main.py --account "Acme Corp" --question "Why are they a good GTM fit?"
    python main.py --account "Acme Corp" --question "..." --sources ./sources

Put the account's source material (.txt / .md files) in the --sources directory.
Set your key first:  cp .env.example .env  &&  edit .env
"""

from __future__ import annotations

import argparse
import sys

# Allow running from the repo root without installing the package.
sys.path.insert(0, "src")

from gtm_agent import GTMAgent, Retriever, evaluate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="GTM Account Intelligence Agent")
    parser.add_argument("--account", required=True, help="Account name to research")
    parser.add_argument("--question", required=True, help="What you want to know")
    parser.add_argument(
        "--sources",
        default="sources",
        help="Directory of .txt/.md source files to ground on (default: ./sources)",
    )
    args = parser.parse_args()

    retriever = Retriever(args.sources)
    agent = GTMAgent(retriever)

    print(f"\nResearching: {args.account}\nQuestion: {args.question}\n" + "-" * 60)
    result = agent.run(args.account, args.question)
    evaluation = evaluate(result)

    print("\n=== DECISION-READY OUTPUT ===\n")
    print(result.answer)

    print("\n=== EVIDENCE USED ===\n")
    print(result.evidence_block())

    print("\n=== AGENT TRACE ===\n")
    print("\n".join(result.steps) or "(no tool calls)")

    print("\n=== RELIABILITY ===\n")
    print(evaluation.summary())
    print(f"Why: {evaluation.rationale}")
    if evaluation.unsupported_claims:
        print("Unsupported claims flagged:")
        for claim in evaluation.unsupported_claims:
            print(f"  - {claim}")

    # Non-zero exit when a human needs to look, so this is scriptable in a pipeline.
    return 1 if evaluation.needs_human_review else 0


if __name__ == "__main__":
    raise SystemExit(main())
