# Publishing the GTM Account Intelligence Agent — Step-by-Step

A runbook for pushing the GTM Account Intelligence Agent live to GitHub **without ever
exposing your Anthropic API key.** Follow the steps in order. The security gate in Step 0
and Step 4 is non-negotiable — do not skip it.

---

## THE ONE RULE (read first)

Your Anthropic API key is a **personal secret**. It must **never** go into the repo —
public *or* private.

- Code reads the key from an environment variable: `os.environ["ANTHROPIC_API_KEY"]`.
- The real key lives only in a local `.env` file, which is **gitignored**.
- The repo contains only `.env.example` (a placeholder), never `.env`.
- If the key is *ever* committed — even once, even to a private repo — **rotate it
  immediately** (Step 8). Deleting it from the latest commit is **not enough**; it stays
  in git history, and bots scan public GitHub for keys within minutes.

---

## Step 1 — Put the code and scaffolding in one folder

On your computer, create a clean project folder and place your agent code in it, alongside
the scaffolding files already generated (`README.md`, `LICENSE`, `.gitignore`,
`.env.example`, `requirements.txt`).

```bash
mkdir -p ~/projects/gtm-account-intelligence-agent
cd ~/projects/gtm-account-intelligence-agent
# copy your .py files here, plus the 5 scaffolding files
ls -a    # confirm .gitignore and .env.example are present
```

## Step 2 — Make the code read the key from the environment

Every place your code uses the key, it must pull it from the environment — never a
hard-coded string. Using `python-dotenv` (already in `requirements.txt`):

```python
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()                                   # loads .env locally; no-op in prod
client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
```

Search your code to be sure no key is hard-coded (a real Anthropic key starts with
`sk-ant-`):

```bash
grep -rn "sk-ant-" . ; echo "exit: $?"
```

Expected: **no matches** (exit 1). If anything prints, remove the literal key and replace
it with the `os.environ[...]` pattern above before continuing.

## Step 3 — Create your local `.env` (never committed)

```bash
cp .env.example .env
# open .env and paste your real key:
# ANTHROPIC_API_KEY=sk-ant-...your-real-key...
```

`.env` is already in `.gitignore`, so git will not track it. `.env.example` stays with its
placeholder value and is the only one that gets published.

## Step 4 — Pre-commit secret scan (the gate)

Run all three checks. Each must pass before you commit.

```bash
# (a) The real .env must be IGNORED by git:
git check-ignore .env            # must print: .env   (if it prints nothing, STOP)

# (b) No live key anywhere in the tree:
grep -rn "sk-ant-" . --exclude=.env ; echo "exit: $?"   # want: no matches, exit 1

# (c) Confirm what git WOULD track — .env must NOT appear:
git init 2>/dev/null; git add -A; git status --short
```

In the `git status` output, confirm **`.env` is not listed**. You should see `.env.example`
but never `.env`. If `.env` appears, it is being tracked — run `git rm --cached .env`, fix
`.gitignore`, and re-run this step.

## Step 5 — First commit

```bash
git add -A
git status --short          # final eyeball: .env absent, .env.example present
git commit -m "Initial commit: GTM Account Intelligence Agent"
```

## Step 6 — Create the GitHub repo and push

**Option A — GitHub CLI (fastest).** If you have `gh` installed and authenticated
(`gh auth status`):

```bash
gh repo create gtm-account-intelligence-agent --public --source=. --remote=origin --push
```

**Option B — Web UI.** Create an **empty** repo at github.com (name:
`gtm-account-intelligence-agent`, no README/License/`.gitignore` — you already have them),
then:

```bash
git branch -M main
git remote add origin https://github.com/TharunPonnaganti/gtm-account-intelligence-agent.git
git push -u origin main
```

## Step 7 — Post-push verification (on github.com)

Open the repo in your browser and confirm:

1. **`.env` is NOT in the file list.** `.env.example` is. (This is the most important check.)
2. The README renders correctly.
3. Click into a couple of source files — no `sk-ant-...` string anywhere.
4. Check the **commit history** — the key must not appear in any past commit or diff.

```bash
# belt-and-suspenders: scan the full history for a leaked key
git log -p | grep -n "sk-ant-" ; echo "exit: $?"   # want: no matches, exit 1
```

If all checks pass, the repo is live and clean.

## Step 8 — IF A KEY EVER LEAKED (do this immediately, no exceptions)

If any check above finds `sk-ant-...` in the repo or history:

1. Go to the **Anthropic Console → API keys**, and **revoke/delete** the exposed key now.
2. **Generate a new key**, and update your local `.env` with it.
3. Only then worry about history: the exposed key is already burned, so rotation is the
   fix — scrubbing history (`git filter-repo` / BFG) is cleanup, not a substitute for
   rotating. If the repo is brand new, it is simplest to delete it on GitHub, fix locally,
   and push a fresh one.

Treat rotation as mandatory the moment a key touches a commit — assume it is compromised.

## Step 9 — After it's live

- Update your resume project links: the GTM entry can point to the real repo
  (`github.com/TharunPonnaganti/gtm-account-intelligence-agent`) instead of the profile URL.
- Add a short "Setup" note in the README so a reviewer can run it: clone →
  `pip install -r requirements.txt` → `cp .env.example .env` → add key → run.
- Optional: pin the repo on your GitHub profile so it's the first thing a recruiter sees.

---

### Quick reference — the whole flow

```bash
cd ~/projects/gtm-account-intelligence-agent
grep -rn "sk-ant-" . --exclude=.env ; echo $?     # no matches
cp .env.example .env                               # add real key to .env
git init && git add -A
git check-ignore .env                              # prints .env
git status --short                                 # .env NOT listed
git commit -m "Initial commit: GTM Account Intelligence Agent"
gh repo create gtm-account-intelligence-agent --public --source=. --remote=origin --push
# then verify on github.com: .env absent, no sk-ant- in files or history
```
