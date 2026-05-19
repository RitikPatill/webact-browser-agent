# WebAct — Vision-Guided Browser Agent

> Locally-runnable browser automation that *sees* the page instead of chasing CSS selectors.

---

## Status

**M2 — core agent loop + action schema (shipped)**

| Deliverable | State |
|---|---|
| `agent/schema.py` — Pydantic `Action` discriminated union (6 types) | Done |
| `agent/llm.py` — Claude claude-sonnet-4-6 vision call + retry-on-parse-error (3 retries) | Done |
| `agent/loop.py` — observe → plan → act loop, Playwright Chromium, step history | Done |
| `agent/main.py` — working CLI entry point | Done |
| `tests/test_schema.py`, `tests/test_llm.py` | Done |
| `navigate` + `done` actions fully wired | Done |
| `click`, `type`, `scroll`, `extract_text` actions | Stubbed — full implementation in M3 |

**M1 — scaffold + readme (shipped)**

| Deliverable | State |
|---|---|
| Repo structure (`agent/`, `demos/`, `tests/`) | Done |
| Pinned dependencies (`requirements.txt`) | Done |
| MIT license, `.gitignore` | Done |
| Demo script stubs (`demos/`) | Done — full implementations in M5 |
| Scaffold tests (`tests/test_scaffold.py`) | Passing |

---

## What It Does

> **Target behavior** (fully implemented by M5). M3 adds browser interaction actions and the stuck detector; M4 adds Rich logging.

1. You provide a plain-English task via CLI (e.g. `"Go to Hacker News, find the top AI story, return its title and URL"`).
2. The agent launches a Playwright Chromium browser, takes a full-page screenshot, and calls Claude claude-sonnet-4-6 with the task, step history, and the screenshot encoded as base64.
3. Claude returns a **structured action** (Pydantic-validated): one of `navigate`, `click`, `type`, `scroll`, `extract_text`, or `done`.
4. The agent executes the action, screenshots again, and loops.
5. After each step a lightweight **stuck detector** checks: same URL + no new extracted content for ≥ 2 consecutive steps → fires a *recovery prompt* asking Claude to try an alternative strategy.
6. The loop exits when Claude emits `done` with a result, or a configurable max-step limit (default 20) is hit.
7. All agent reasoning, actions, URLs, and the final answer are streamed to the terminal via **Rich** with colour-coded step logs.

---

## Architecture

WebAct implements the **observe → plan → act → evaluate → recover** loop used by modern GUI agents:

```
┌──────────┐    screenshot    ┌─────────────┐
│ Playwright│ ─────────────▶ │ Claude      │
│ Browser  │ ◀───────────── │ claude-sonnet-4-6│
└──────────┘    action JSON  └─────────────┘
      │                            │
      │ execute                    │ stuck?
      ▼                            ▼
 new screenshot            recovery re-prompt
```

**Key modules (M2):**

| Module | Responsibility |
|---|---|
| `agent/schema.py` | Pydantic discriminated union for all action types; `parse_action()` validator |
| `agent/llm.py` | Builds multimodal message (image + text), calls Claude, extracts JSON from code fence, retries on parse failure |
| `agent/loop.py` | Launches browser, runs the observe → plan → act loop, dispatches actions, tracks history |
| `agent/main.py` | CLI entry point |

**Why screenshots beat CSS selectors:** Modern web UIs are dynamic, personalised, and layout-shifting. A vision model that reads pixels is immune to class-name churn, shadow DOM, and React re-renders that break recorded selectors within days. WebAct is a clean, minimal reference implementation of this paradigm — no heavyweight framework, just the core loop.

---

## Requirements

- Python ≥ 3.11
- An [Anthropic API key](https://console.anthropic.com/)

---

## Setup

```bash
git clone <repo>
cd webact-browser-agent
pip install -r requirements.txt
playwright install chromium
export ANTHROPIC_API_KEY=sk-...   # or add to a .env file
```

---

## Usage

```bash
python -m agent.main "Your task here"
```

Example:

```bash
python -m agent.main "Go to Hacker News and return the title and URL of the top story"
```

By default the browser runs headless. To watch it run:

```bash
WEBACT_HEADLESS=false python -m agent.main "Your task here"
```

---

## Demo Scripts

Located in `demos/` — each is a self-contained example task (implemented in M5):

| Script | What it demonstrates |
|---|---|
| `demos/web_search.py` | Navigate to a search engine, enter a query, extract the top result |
| `demos/form_fill.py` | Fill in a web form with structured data and submit it |
| `demos/data_extraction.py` | Scrape a structured table or list from a live webpage |

---

## Action Types

| Action | Description | M2 Status |
|---|---|---|
| `navigate` | Load a URL in the browser (`page.goto`) | Implemented |
| `click` | Click an element described by a screen coordinate or label | Stubbed |
| `type` | Type text into the currently focused or described input field | Stubbed |
| `scroll` | Scroll the page up, down, or to a position | Stubbed |
| `extract_text` | Read and return visible text from the current page | Stubbed |
| `done` | Signal task completion and return the final result to the user | Implemented |

Stubbed actions log a warning and return without browser interaction. Full implementations land in M3.

---

## Out of Scope

- Multi-tab browsing, file downloads, OAuth/login flows
- Fine-tuning, RL training, or any GPU workload
- Non-Chromium browsers
- A web UI (pure CLI tool)

---

## Roadmap

| Milestone | Description | State |
|---|---|---|
| M1 | Scaffold, README, pinned deps | Shipped |
| M2 | Agent loop — Playwright + Claude vision calls + action schema | Shipped |
| M3 | Browser interaction actions, stuck detector and recovery prompts | Planned |
| M4 | Rich terminal UI and step logging | Planned |
| M5 | Demo scripts (`web_search`, `form_fill`, `data_extraction`) | Planned |

<!-- TODO: update State column as milestones ship -->

---

## License

MIT — see [LICENSE](LICENSE).
