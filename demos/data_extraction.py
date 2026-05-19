"""
Demo: Wikipedia infobox scrape

Navigates to the Python (programming language) Wikipedia article and
extracts key infobox facts: creator, first appeared, and stable release.
Demonstrates navigate → scroll → extract_text → done flow.

Run:
    python demos/data_extraction.py
"""
from agent.loop import run_agent

TASK = (
    "Go to https://en.wikipedia.org/wiki/Python_(programming_language). "
    "Extract the creator, year first appeared, and latest stable release "
    "from the infobox on the right side of the page."
)

if __name__ == "__main__":
    result = run_agent(TASK)
    print(result)
