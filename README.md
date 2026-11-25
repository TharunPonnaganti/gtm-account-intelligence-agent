# GTM Account Intelligence Agent

An agentic AI application that automates go-to-market account research and turns
it into structured, decision-ready recommendations. The agent runs a multi-step
workflow, retrieves and grounds information from multiple sources
(retrieval-augmented generation), and scores its own output for reliability
before a human reviews it.

> Built with Python and the Claude API as a hands-on exploration of agentic
> workflows, RAG, and AI output evaluation.

---

## What it does

- **Agentic workflow** — breaks an account-research question into steps and
  executes them autonomously, using tool calls to gather information.
- **Retrieval-augmented generation (RAG)** — grounds the model's reasoning in
  retrieved source material instead of relying on the model alone.
- **AI output evaluation** — a dedicated evaluation pass scores generated output
  against the retrieved facts (groundedness / hallucination control) and drops
  unsupported claims.
- **Human-in-the-loop** — surfaces the evaluated output for human review before
  it is treated as final.
- **Decision-ready output** — returns a structured summary and recommendations
  rather than free-form text.

## Architecture (high level)

```
Question ─▶ Planner ─▶ Tool-using research steps ─▶ Retrieval (RAG)
                                                   │
                                                   ▼
                        Draft output ◀── Generation (Claude API)
                                                   │
                                                   ▼
                     Evaluation pass (grounded vs. retrieved facts)
                                                   │
                                                   ▼
                     Human-in-the-loop review ─▶ Final recommendation
```

<!-- TODO (Tharun): adjust the components above to match your actual modules,
     and replace this comment with a one-line description of each real file. -->

## Tech stack

- Python
- Anthropic Claude API
- Retrieval-augmented generation (RAG)

## Getting started

```bash
# 1. Clone
git clone https://github.com/TharunPonnaganti/gtm-account-intelligence-agent.git
cd gtm-account-intelligence-agent

# 2. (Recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key (never commit this file)
cp .env.example .env
#   then edit .env and set:  ANTHROPIC_API_KEY=sk-...
```

## Usage

```bash
python main.py            # <-- replace with your actual entry point
```

<!-- TODO (Tharun): replace with the real command and show a short example of
     input and the structured output the agent returns. -->

## Evaluation

The agent includes an evaluation step that checks generated claims against the
retrieved source material and flags or removes anything unsupported, so output
is measurable and defensible rather than taken on trust.

<!-- TODO (Tharun): if you logged any numbers (e.g., % of claims flagged,
     accuracy on a small test set), add them here — real metrics make this
     section much stronger. -->

## License

MIT — see [LICENSE](LICENSE).
