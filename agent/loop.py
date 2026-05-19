from __future__ import annotations

import os

import anthropic
from playwright.sync_api import Page, sync_playwright
from rich.console import Console

from agent.executor import dispatch_action
from agent.llm import get_next_action
from agent.stuck import is_stuck
from agent.schema import (
    DoneAction,
    NavigateAction,
)

console = Console()


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

        console.print(f"[bold green]WebAct[/bold green] starting task: {task!r}")
        console.print(f"[dim]max_steps={max_steps}, headless={headless}[/dim]")

        for step in range(1, max_steps + 1):
            console.print(f"\n[bold]Step {step}[/bold] — capturing screenshot …")
            screenshot_bytes = page.screenshot(full_page=True)

            recovery = is_stuck(history)
            if recovery:
                console.print("[yellow]Stuck detected (same URL + content for 2 steps) — injecting recovery prompt[/yellow]")
            console.print("[dim]Calling Claude …[/dim]")
            action = get_next_action(task, history, screenshot_bytes, client, recovery=recovery)

            console.print(f"[cyan]Action:[/cyan] {action.model_dump()}")

            if isinstance(action, DoneAction):
                console.print(f"\n[bold green]Done![/bold green] Result: {action.result}")
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

        console.print(
            f"\n[bold yellow]Max steps ({max_steps}) reached — task did not complete.[/bold yellow]"
        )
        browser.close()
        return f"Agent stopped: max {max_steps} steps reached without a done action."
