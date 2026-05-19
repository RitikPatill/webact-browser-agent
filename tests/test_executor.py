from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from agent.executor import dispatch_action
from agent.schema import ClickAction, ExtractTextAction, ScrollAction, TypeAction


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _page() -> MagicMock:
    return MagicMock()


def _console() -> MagicMock:
    return MagicMock()


# ---------------------------------------------------------------------------
# ClickAction
# ---------------------------------------------------------------------------

def test_click_uses_button_role():
    page = _page()
    console = _console()
    action = ClickAction(type="click", label="Submit")

    result = dispatch_action(page, action, console)

    page.get_by_role.assert_any_call("button", name="Submit")
    page.get_by_role.return_value.first.click.assert_called_with(timeout=5000)
    assert result == ""


def test_click_fallback_to_text():
    page = _page()
    console = _console()
    action = ClickAction(type="click", label="Submit")

    # button role raises, link role raises, text succeeds
    button_locator = MagicMock()
    button_locator.click.side_effect = PlaywrightTimeoutError("timeout")
    link_locator = MagicMock()
    link_locator.click.side_effect = PlaywrightTimeoutError("timeout")
    text_locator = MagicMock()

    def get_by_role_side_effect(role, name=None):
        m = MagicMock()
        if role == "button":
            m.first = button_locator
        else:
            m.first = link_locator
        return m

    page.get_by_role.side_effect = get_by_role_side_effect
    page.get_by_text.return_value.first = text_locator

    result = dispatch_action(page, action, console)

    text_locator.click.assert_called_once_with(timeout=5000)
    assert result == ""


def test_click_all_fail_logs_and_continues():
    page = _page()
    console = _console()
    action = ClickAction(type="click", label="Ghost")

    # All locators raise
    failing = MagicMock()
    failing.click.side_effect = PlaywrightError("not found")
    page.get_by_role.return_value.first = failing
    page.get_by_text.return_value.first = failing

    result = dispatch_action(page, action, console)

    assert result == ""
    console.print.assert_called()


# ---------------------------------------------------------------------------
# TypeAction
# ---------------------------------------------------------------------------

def test_type_uses_label():
    page = _page()
    console = _console()
    action = TypeAction(type="type", label="Email", text="user@example.com")

    result = dispatch_action(page, action, console)

    page.get_by_label.assert_called_with("Email")
    page.get_by_label.return_value.first.fill.assert_called_once_with(
        "user@example.com", timeout=5000
    )
    assert result == ""


def test_type_fallback_to_placeholder():
    page = _page()
    console = _console()
    action = TypeAction(type="type", label="Email", text="user@example.com")

    label_locator = MagicMock()
    label_locator.fill.side_effect = PlaywrightTimeoutError("timeout")
    page.get_by_label.return_value.first = label_locator

    placeholder_locator = MagicMock()
    page.get_by_placeholder.return_value.first = placeholder_locator

    result = dispatch_action(page, action, console)

    placeholder_locator.fill.assert_called_once_with("user@example.com", timeout=5000)
    assert result == ""


def test_type_error_logs_and_continues():
    page = _page()
    console = _console()
    action = TypeAction(type="type", label="Ghost", text="data")

    failing = MagicMock()
    failing.fill.side_effect = PlaywrightError("not found")
    page.get_by_label.return_value.first = failing
    page.get_by_placeholder.return_value.first = failing
    page.get_by_text.return_value.first = failing

    result = dispatch_action(page, action, console)

    assert result == ""
    console.print.assert_called()


# ---------------------------------------------------------------------------
# ScrollAction
# ---------------------------------------------------------------------------

def test_scroll_down():
    page = _page()
    console = _console()
    action = ScrollAction(type="scroll", direction="down", amount=300)

    result = dispatch_action(page, action, console)

    page.evaluate.assert_called_once_with("window.scrollBy(0, 300)")
    assert result == ""


def test_scroll_up():
    page = _page()
    console = _console()
    action = ScrollAction(type="scroll", direction="up", amount=150)

    result = dispatch_action(page, action, console)

    page.evaluate.assert_called_once_with("window.scrollBy(0, -150)")
    assert result == ""


# ---------------------------------------------------------------------------
# ExtractTextAction
# ---------------------------------------------------------------------------

def test_extract_text_returns_body():
    page = _page()
    console = _console()
    action = ExtractTextAction(type="extract_text", description="all text")
    page.inner_text.return_value = "Hello world"

    result = dispatch_action(page, action, console)

    page.inner_text.assert_called_once_with("body", timeout=5000)
    assert result == "Hello world"


def test_extract_text_truncates_at_4000():
    page = _page()
    console = _console()
    action = ExtractTextAction(type="extract_text", description="long page")
    page.inner_text.return_value = "x" * 5000

    result = dispatch_action(page, action, console)

    assert len(result) == 4000


def test_extract_text_error_returns_empty():
    page = _page()
    console = _console()
    action = ExtractTextAction(type="extract_text", description="broken")
    page.inner_text.side_effect = PlaywrightError("frame detached")

    result = dispatch_action(page, action, console)

    assert result == ""
    console.print.assert_called()
