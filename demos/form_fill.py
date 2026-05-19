"""
Demo: Hacker News top-story lookup

Navigates to Hacker News front page and extracts the title and URL of the
#1 ranked story. Demonstrates navigate → extract_text → done flow.

Note: This file was originally scoped as a form-fill demo. During M5 it was
repurposed to the HN top-story lookup to provide a more reliable, login-free
example. The filename is intentionally kept to avoid churn in existing tests.

Run:
    python demos/form_fill.py
"""
from agent.loop import run_agent

TASK = (
    "Go to https://news.ycombinator.com and find the #1 ranked story "
    "(the first item in the list). Return its title and URL."
)

if __name__ == "__main__":
    result = run_agent(TASK)
    print(result)
