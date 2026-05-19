from __future__ import annotations

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from rich.console import Console

from agent.schema import Action, ClickAction, ExtractTextAction, ScrollAction, TypeAction


def dispatch_action(page: Page, action: Action, console: Console) -> str:
    """
    Execute a content-interaction action on the Playwright page.
    Returns extracted text for ExtractTextAction, empty string otherwise.
    NavigateAction and DoneAction are handled upstream in loop.py.
    """
    if isinstance(action, ClickAction):
        try:
            for locator in [
                page.get_by_role("button", name=action.label).first,
                page.get_by_role("link", name=action.label).first,
                page.get_by_text(action.label, exact=False).first,
            ]:
                try:
                    locator.click(timeout=5000)
                    return ""
                except (PlaywrightTimeoutError, PlaywrightError):
                    continue
            console.print(f"[red]Click failed: no element found for label {action.label!r}[/red]")
        except Exception as exc:
            console.print(f"[red]Click error: {exc}[/red]")
        return ""

    elif isinstance(action, TypeAction):
        try:
            for locator in [
                page.get_by_label(action.label).first,
                page.get_by_placeholder(action.label).first,
                page.get_by_text(action.label, exact=False).first,
            ]:
                try:
                    locator.fill(action.text, timeout=5000)
                    return ""
                except (PlaywrightTimeoutError, PlaywrightError):
                    continue
            console.print(f"[red]Type failed: no element found for label {action.label!r}[/red]")
        except Exception as exc:
            console.print(f"[red]Type error: {exc}[/red]")
        return ""

    elif isinstance(action, ScrollAction):
        delta = action.amount if action.direction == "down" else -action.amount
        page.evaluate(f"window.scrollBy(0, {delta})")
        return ""

    elif isinstance(action, ExtractTextAction):
        try:
            text = page.inner_text("body", timeout=5000)
            return text[:4000]
        except (PlaywrightTimeoutError, PlaywrightError) as exc:
            console.print(f"[red]ExtractText error: {exc}[/red]")
            return ""

    else:
        console.print(f"[red]executor: unhandled action type {type(action).__name__}[/red]")
        return ""
