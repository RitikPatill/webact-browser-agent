import pytest
from pydantic import ValidationError

from agent.schema import parse_action


def test_navigate_valid():
    action = parse_action({"type": "navigate", "url": "https://example.com"})
    assert action.type == "navigate"
    assert action.url == "https://example.com"


def test_click_valid():
    action = parse_action({"type": "click", "label": "Submit button"})
    assert action.type == "click"
    assert action.label == "Submit button"


def test_type_valid():
    action = parse_action({"type": "type", "label": "Search box", "text": "foo"})
    assert action.type == "type"
    assert action.label == "Search box"
    assert action.text == "foo"


def test_scroll_valid_with_amount():
    action = parse_action({"type": "scroll", "direction": "down", "amount": 500})
    assert action.type == "scroll"
    assert action.direction == "down"
    assert action.amount == 500


def test_scroll_valid_default_amount():
    action = parse_action({"type": "scroll", "direction": "up"})
    assert action.type == "scroll"
    assert action.direction == "up"
    assert action.amount == 300


def test_extract_text_valid():
    action = parse_action({"type": "extract_text", "description": "page title"})
    assert action.type == "extract_text"
    assert action.description == "page title"


def test_done_valid():
    action = parse_action({"type": "done", "result": "The title is Example Domain"})
    assert action.type == "done"
    assert action.result == "The title is Example Domain"


def test_unknown_type_raises():
    with pytest.raises(ValidationError):
        parse_action({"type": "hover", "label": "some element"})


def test_missing_field_raises():
    with pytest.raises(ValidationError):
        parse_action({"type": "navigate"})  # url is required
