from agent.stuck import is_stuck


def _entry(url: str, extracted: str, step: int = 1) -> dict:
    return {"step": step, "action": {}, "url": url, "extracted": extracted}


def test_is_stuck_empty_history():
    assert is_stuck([]) is False


def test_is_stuck_one_entry():
    assert is_stuck([_entry("https://example.com", "hello")]) is False


def test_is_stuck_different_urls():
    history = [
        _entry("https://a.com", "same text", step=1),
        _entry("https://b.com", "same text", step=2),
    ]
    assert is_stuck(history) is False


def test_is_stuck_different_extracted():
    history = [
        _entry("https://example.com", "page content A", step=1),
        _entry("https://example.com", "page content B", step=2),
    ]
    assert is_stuck(history) is False


def test_is_stuck_identical_entries():
    history = [
        _entry("https://example.com", "same content", step=1),
        _entry("https://example.com", "same content", step=2),
    ]
    assert is_stuck(history) is True


def test_is_stuck_three_identical():
    history = [
        _entry("https://example.com", "same content", step=1),
        _entry("https://example.com", "same content", step=2),
        _entry("https://example.com", "same content", step=3),
    ]
    # window=2 (default): only last 2 checked → still stuck
    assert is_stuck(history) is True


def test_is_stuck_custom_window():
    two_identical = [
        _entry("https://example.com", "same content", step=1),
        _entry("https://example.com", "same content", step=2),
    ]
    # window=3 but only 2 entries → not enough
    assert is_stuck(two_identical, window=3) is False

    three_identical = two_identical + [_entry("https://example.com", "same content", step=3)]
    assert is_stuck(three_identical, window=3) is True
