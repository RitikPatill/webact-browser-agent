from unittest.mock import MagicMock, patch

import pytest

from agent.llm import get_next_action
from agent.schema import DoneAction, NavigateAction


def _make_client_with_replies(*reply_texts: str) -> MagicMock:
    """Build a mock Anthropic client that returns each reply in sequence."""
    client = MagicMock()
    responses = []
    for text in reply_texts:
        msg = MagicMock()
        msg.content = [MagicMock(text=text)]
        responses.append(msg)
    client.messages.create.side_effect = responses
    return client


VALID_NAVIGATE_FENCE = '```json\n{"type":"navigate","url":"https://example.com"}\n```'
VALID_DONE_FENCE = '```json\n{"type":"done","result":"The title is Example Domain"}\n```'
VALID_NAVIGATE_RAW = '{"type":"navigate","url":"https://example.com"}'

DUMMY_SCREENSHOT = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100


def test_success_json_codeblock():
    client = _make_client_with_replies(VALID_NAVIGATE_FENCE)
    action = get_next_action("go to example.com", [], DUMMY_SCREENSHOT, client)
    assert isinstance(action, NavigateAction)
    assert action.url == "https://example.com"
    assert client.messages.create.call_count == 1


def test_success_raw_json():
    client = _make_client_with_replies(VALID_NAVIGATE_RAW)
    action = get_next_action("go to example.com", [], DUMMY_SCREENSHOT, client)
    assert isinstance(action, NavigateAction)
    assert action.url == "https://example.com"


def test_retry_once_on_bad_json():
    client = _make_client_with_replies("oops, not json at all", VALID_NAVIGATE_FENCE)
    action = get_next_action(
        "go to example.com", [], DUMMY_SCREENSHOT, client, max_retries=3
    )
    assert isinstance(action, NavigateAction)
    assert client.messages.create.call_count == 2


def test_exhausted_retries_raises():
    client = _make_client_with_replies("bad", "bad", "bad")
    with pytest.raises(RuntimeError, match="Failed to get a valid action"):
        get_next_action(
            "go to example.com", [], DUMMY_SCREENSHOT, client, max_retries=3
        )
    assert client.messages.create.call_count == 3
