# WebAct — Vision-Guided Browser Agent

> Locally-runnable browser automation that *sees* the page instead of chasing CSS selectors.

---

## Status

**M4 — stuck detection + recovery prompt (shipped)**

| Deliverable | State |
|---|---|
| `agent/stuck.py` — `is_stuck()`: detects same URL + content hash for ≥ 2 consecutive steps | Done |
| `agent/llm.py` — `RECOVERY_ADDENDUM` constant; `recovery=` flag appends it to the system prompt | Done |
| `agent/loop.py` — calls `is_stuck(history)` before each LLM call; logs yellow warning; passes flag through | Done |
| Max-step guard — bold yellow exit message; return string updated to match spec | Done |
| `tests/test_stuck.py` — 7 unit tests covering all edge cases (empty, 1 entry, diff URL, diff text, identical, window variants) | Done |
| `tests/test_llm.py` — extended with `test_recovery_flag_includes_addendum_in_system_prompt` | Done |

**M3 — action executor (shipped)**

| Deliverable | State |
|---|---|
| `agent/executor.py` — `dispatch_action()` mapping all six action types to Playwright calls | Done |
| `click` — button → link → text locator fallback chain; element-not-found logs and continues | Done |
| `type` — label → placeholder → text locator fallback chain; error logs and continues | Done |
| `scroll` — `window.scrollBy` via `page.evaluate`, direction-aware | Done |
| `extract_text` — `page.inner_text("body")`, truncated to 4 000 characters | Done |
| `agent/loop.py` — calls `dispatch_action`; appends `{step, action, url, extracted}` to history | Done |
| `tests/test_executor.py` — 10 unit tests (mock page/console), covering fallback chains and error paths | Done |

**M2 — core agent loop + action schema (shipped)**

| Deliverable | State |
|---|---|
| `agent/schema.py` — Pydantic `Action` discriminated union (6 types) | Done |
| `agent/llm.py` — Claude claude-sonnet-4-6 vision call + retry-on-parse-error (3 retries) | Done |
| `agent/loop.py` — observe → plan → act loop, Playwright Chromium, step history | Done |
| `agent/main.py` — working CLI entry point | Done |
| `tests/test_schema.py`, `tests/test_llm.py` | Done |
| `navigate` + `done` actions fully wired | Done |

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

> Steps 1–6 are implemented through M4. M5 will add the demo scripts.

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

**Key modules (M4):**

| Module | Responsibility |
|---|---|
| `agent/schema.py` | Pydantic discriminated union for all action types; `parse_action()` validator |
| `agent/llm.py` | Builds multimodal message (image + text), calls Claude, extracts JSON from code fence, retries on parse failure; `recovery=` flag appends recovery addendum to system prompt |
| `agent/executor.py` | Maps `click`, `type`, `scroll`, `extract_text` to Playwright calls; locator fallback chains; error-log-and-continue |
| `agent/loop.py` | Launches browser, runs the observe → plan → act loop, delegates to executor, appends step history; detects stuck state and triggers recovery |
| `agent/stuck.py` | `is_stuck(history, window=2)` — returns True when the last N entries share identical URL and extracted-text hash |
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

| Action | Description | Status |
|---|---|---|
| `navigate` | Load a URL in the browser (`page.goto`) | Implemented (M2) |
| `click` | Click an element by label; tries button role → link role → text locator | Implemented (M3) |
| `type` | Fill a field by label; tries label → placeholder → text locator | Implemented (M3) |
| `scroll` | Scroll up or down by pixel amount via `window.scrollBy` | Implemented (M3) |
| `extract_text` | Read visible body text from the current page (capped at 4 000 chars) | Implemented (M3) |
| `done` | Signal task completion and return the final result to the user | Implemented (M2) |

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
| M3 | Action executor — all six action types wired to Playwright, step history | Shipped |
| M4 | Stuck detection + recovery prompt; max-step guard | Shipped |
| M5 | Demo scripts (`web_search`, `form_fill`, `data_extraction`) | Planned |

<!-- TODO: update State column as milestones ship -->

---

## License

MIT — see [LICENSE](LICENSE).
