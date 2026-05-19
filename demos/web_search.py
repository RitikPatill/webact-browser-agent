"""
Demo: DuckDuckGo search + snippet extraction

Navigates to DuckDuckGo, searches for "Playwright Python", and extracts
the first result's title and URL. Demonstrates navigate → type → click →
extract_text flow.

Run:
    python demos/web_search.py
"""
from agent.loop import run_agent

TASK = (
    "Go to https://duckduckgo.com, search for 'Playwright Python automation', "
    "then extract the title and URL of the first organic result."
)

if __name__ == "__main__":
    result = run_agent(TASK)
    print(result)
