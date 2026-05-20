# WebAct: Self-Correcting Browser Agent


> **Video walkthrough:** https://youtu.be/_lWN_2jGIUM
> **60-second overview:** https://youtu.be/Adbi4MXKI54

> A Python agent that uses vision-LLMs to autonomously navigate browsers, self-evaluate progress, and recover when stuck.

<!-- TODO: replace with a 5-10 second demo gif. Record with ScreenToGif on
     Windows or peek on macOS. Save to docs/demo.gif and update path here. -->
![demo](docs/demo.gif)

## What it is

WebAct is a locally-runnable browser automation agent built around the **observe → plan → act → evaluate → recover** loop used by modern GUI-agent research. You give it a plain-English task; it launches a Playwright Chromium browser, feeds live screenshots to Claude claude-sonnet-4-6 (vision), receives a structured next action, executes it, and loops until it has an answer or reaches the step limit.

The key design choice is perception through pixels rather than CSS selectors. Modern web UIs are dynamic, personalised, and layout-shifting — a vision model that reads what the browser renders is immune to class-name churn, shadow DOM, and React re-renders that break recorded selectors within days. WebAct is a minimal reference implementation of that paradigm: no heavyweight framework, just the core agentic loop in roughly 300 lines of Python.

## Quickstart

```bash
git clone https://github.com/RitikPatill/webact-browser-agent.git
cd webact-browser-agent
pip install -r requirements.txt
playwright install chromium
export ANTHROPIC_API_KEY=sk-ant-...   # from console.anthropic.com
python -m agent.main "Go to Hacker News and return the title and URL of the top story"
```

## Usage

Pass any plain-English task as a positional argument:

```bash
python -m agent.main "Search DuckDuckGo for 'playwright python' and return the first result URL"
```

To cap the number of steps (default is 20):

```bash
python -m agent.main --max-steps 10 "Your task here"
```

To watch the browser run visibly instead of headless:

```bash
WEBACT_HEADLESS=false python -m agent.main "Your task here"
```

Three self-contained demo scripts are in `demos/` — run any directly with `python demos/web_search.py`, `python demos/form_fill.py`, or `python demos/data_extraction.py`.

## Architecture

```
User task (CLI)
      │
      ▼
 agent/loop.py ──── screenshot (base64) ────▶ agent/llm.py
      │                                              │ Claude claude-sonnet-4-6
      │◀─────────── structured action (JSON) ────────┘
      │
 agent/executor.py ──▶ Playwright Chromium (navigate / click / type / scroll / extract)
      │
 agent/stuck.py ── same URL + same content hash for ≥ 2 steps?
      └── yes ──▶ recovery re-prompt ──▶ agent/llm.py (alternative strategy)
```

## Project structure

```
webact-browser-agent/
├── agent/           # Core package: loop, LLM client, executor, action schema, stuck detector
├── demos/           # Three runnable examples: web search, form fill, data extraction
├── tests/           # pytest unit tests for every module (~26 tests total)
├── requirements.txt # Pinned: anthropic, playwright, pydantic, rich, pytest
└── LICENSE          # MIT
```

## Roadmap

- [ ] Optional local VLM backend (e.g. LLaVA via Ollama) to remove the Anthropic API dependency
- [ ] Multi-tab support and cross-tab navigation actions
- [ ] Headless video recording of each run for post-hoc debugging
- [ ] A replay mode that re-executes a saved action trace without calling the LLM
- [ ] Firefox and WebKit support via Playwright's other browser engines

## License

MIT — see [LICENSE](LICENSE).

---

Built autonomously by [autodev](https://github.com/RitikPatill/autodev),
a multi-agent orchestrator I designed. Each commit in this repo was
authored by me; the implementation work was performed by Sonnet under
the orchestrator's control. Read the orchestrator's README to see how.
