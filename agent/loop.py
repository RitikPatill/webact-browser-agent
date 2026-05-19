from __future__ import annotations

import os

import anthropic
from playwright.sync_api import Page, sync_playwright
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from agent.executor import dispatch_action
from agent.llm import get_next_action
from agent.stuck import is_stuck
from agent.schema import (
    DoneAction,
    NavigateAction,
)

console = Console()

_ACTION_COLORS: dict[str, str] = {
    "navigate":     "blue",
    "click":        "cyan",
    "type":         "magenta",
    "scroll":       "yellow",
    "extract_text": "green",
    "done":         "bold green",
}


def run_agent(task: str, max_steps: int = 20) -> str:
    """
    Launch Chromium, loop observe→plan→act, return result from DoneAction.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY environment variable is not set. "
            "Export your Anthropic API key before running the agent."
        )

    headless = os.environ.get("WEBACT_HEADLESS", "true").lower() != "false"
    client = anthropic.Anthropic(api_key=api_key)
    history: list[dict] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=headless)
        page = browser.new_page()

        console.print(Panel(task, title="[bold]WebAct[/bold]", subtitle=f"max_steps={max_steps}"))

        for step in range(1, max_steps + 1):
            console.rule(f"[bold]Step {step} / {max_steps}[/bold]")
            console.print(f"  [dim]URL:[/dim] {page.url}")

            screenshot_bytes = page.screenshot(full_page=True)

            recovery = is_stuck(history)
            if recovery:
                console.print("[yellow]Stuck detected (same URL + content for 2 steps) — injecting recovery prompt[/yellow]")
            console.print("[dim]Calling Claude …[/dim]")
            action = get_next_action(task, history, screenshot_bytes, client, recovery=recovery)

            action_dict = action.model_dump()
            action_type = action_dict.get("type", "")
            color = _ACTION_COLORS.get(action_type, "white")
            badge = Text(f" {action_type.upper()} ", style=f"bold white on {color}")
            detail_parts = {k: v for k, v in action_dict.items() if k != "type"}
            detail_str = " ".join(f"{k}={v!r}" for k, v in detail_parts.items())
            console.print(badge, detail_str)

            if isinstance(action, DoneAction):
                console.print(Panel(action.result, title="[bold green]Done[/bold green]", border_style="green"))
                browser.close()
                return action.result

            if isinstance(action, NavigateAction):
                page.goto(action.url, wait_until="domcontentloaded")
                extracted = ""
            else:
                extracted = dispatch_action(page, action, console)

            history.append({
                "step": step,
                "action": action.model_dump(),
                "url": page.url,
                "extracted": extracted,
            })

        console.print(Panel(
            f"Max steps ({max_steps}) reached — task did not complete.",
            title="[bold yellow]Stopped[/bold yellow]",
            border_style="yellow",
        ))
        browser.close()
        return f"Agent stopped: max {max_steps} steps reached without a done action."
