from __future__ import annotations

import os

import anthropic
from playwright.sync_api import Page, sync_playwright
from rich.console import Console

from agent.llm import get_next_action
from agent.schema import (
    Action,
    ClickAction,
    DoneAction,
    ExtractTextAction,
    NavigateAction,
    ScrollAction,
    TypeAction,
)

console = Console()


def dispatch_action(page: Page, action: Action) -> str:
    """
    Execute action on the Playwright page.
    Returns extracted text for extract_text, empty string otherwise.
    M2 stubs: click/type/scroll print a warning and return "".
    """
    if isinstance(action, NavigateAction):
        page.goto(action.url, wait_until="domcontentloaded")
        return ""
    elif isinstance(action, ClickAction):
        console.print(f"[yellow]STUB[/yellow] click: {action.label!r} (not yet implemented)")
        return ""
    elif isinstance(action, TypeAction):
        console.print(f"[yellow]STUB[/yellow] type: {action.label!r} = {action.text!r} (not yet implemented)")
        return ""
    elif isinstance(action, ScrollAction):
        console.print(f"[yellow]STUB[/yellow] scroll {action.direction} {action.amount}px (not yet implemented)")
        return ""
    elif isinstance(action, ExtractTextAction):
        console.print(f"[yellow]STUB[/yellow] extract_text: {action.description!r} (not yet implemented)")
        return ""
    else:
        console.print(f"[red]Unknown action type: {type(action).__name__}[/red]")
        return ""


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

            console.print("[dim]Calling Claude …[/dim]")
            action = get_next_action(task, history, screenshot_bytes, client)

            console.print(f"[cyan]Action:[/cyan] {action.model_dump()}")

            if isinstance(action, DoneAction):
                console.print(f"\n[bold green]Done![/bold green] Result: {action.result}")
                browser.close()
                return action.result

            extracted = dispatch_action(page, action)

            history.append({
                "step": step,
                "action": action.model_dump(),
                "url": page.url,
                "extracted": extracted,
            })

        console.print(
            f"\n[yellow]Max steps ({max_steps}) reached without a done action.[/yellow]"
        )
        browser.close()
        return f"Agent stopped after {max_steps} steps without completing the task."
