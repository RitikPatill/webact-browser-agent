from __future__ import annotations

import base64
import json
import re
from typing import TYPE_CHECKING

import anthropic

from agent.schema import Action, parse_action

if TYPE_CHECKING:
    pass

SYSTEM_PROMPT = """\
You control a web browser. For each step you receive a screenshot of the current \
browser state and must output exactly one JSON action inside a ```json code fence. \
Never add prose outside the fence. Never output multiple actions.

Supported actions:
{"type":"navigate","url":"<absolute URL>"}
{"type":"click","label":"<visible text or aria-label of element>"}
{"type":"type","label":"<element description>","text":"<text to type>"}
{"type":"scroll","direction":"up"|"down","amount":<pixels, default 300>}
{"type":"extract_text","description":"<what to extract>"}
{"type":"done","result":"<final answer string>"}

Rules:
- Use "navigate" to go to a URL directly.
- Use "click" with the visible label or aria-label of the target element.
- Use "type" to fill in an input; provide the element label and the text to enter.
- Use "scroll" to move the viewport up or down by a pixel amount.
- Use "extract_text" to read specific content from the current page.
- Use "done" when the task is complete; put the final answer in "result".
- Prefer "extract_text" before "done" so you have the data in history.
- Output ONLY the JSON code fence — no explanation, no markdown outside the fence.
"""

RECOVERY_ADDENDUM = (
    "\n\n---\n"
    "RECOVERY MODE: The URL and page content have not changed for the last 2 steps — "
    "you are stuck. Briefly reason about what has not worked, then choose a DIFFERENT "
    "action (different type or different target). Do not repeat the immediately preceding action."
)

_JSON_FENCE_RE = re.compile(r"```json\s*(.*?)\s*```", re.DOTALL)


def _extract_json(text: str) -> dict:
    """Extract a JSON object from a code-fenced reply or raw JSON string."""
    match = _JSON_FENCE_RE.search(text)
    if match:
        return json.loads(match.group(1))
    # Fall back to stripping and parsing the whole text
    return json.loads(text.strip())


def build_user_message(
    task: str,
    history: list[dict],
    screenshot_bytes: bytes,
) -> list[dict]:
    """Return the content list for the user turn (image + text)."""
    image_b64 = base64.b64encode(screenshot_bytes).decode()
    history_text = ""
    if history:
        history_lines = [
            f"Step {h['step']}: {json.dumps(h['action'])} @ {h['url']}"
            for h in history
        ]
        history_text = "Previous steps:\n" + "\n".join(history_lines) + "\n\n"

    return [
        {
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": image_b64,
            },
        },
        {
            "type": "text",
            "text": (
                f"{history_text}"
                f"Current task: {task}\n\n"
                "What is the next action?"
            ),
        },
    ]


def get_next_action(
    task: str,
    history: list[dict],
    screenshot_bytes: bytes,
    client: anthropic.Anthropic,
    max_retries: int = 3,
    recovery: bool = False,
) -> Action:
    """
    Call Claude claude-sonnet-4-6, extract JSON, parse to Action.
    Retries up to max_retries times on parse/validation errors.
    Raises RuntimeError if all retries are exhausted.
    """
    system = SYSTEM_PROMPT + RECOVERY_ADDENDUM if recovery else SYSTEM_PROMPT
    messages: list[dict] = [
        {
            "role": "user",
            "content": build_user_message(task, history, screenshot_bytes),
        }
    ]

    last_error: Exception | None = None
    for attempt in range(max_retries):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system=system,
            messages=messages,
        )
        reply_text = response.content[0].text

        # Append assistant reply to local message list for retry context
        messages.append({"role": "assistant", "content": reply_text})

        try:
            raw = _extract_json(reply_text)
            action = parse_action(raw)
            return action
        except (json.JSONDecodeError, ValueError, Exception) as exc:
            last_error = exc
            error_feedback = (
                f"Your previous response could not be parsed: {exc}. "
                "Please respond with ONLY a valid JSON code fence containing one action."
            )
            messages.append({"role": "user", "content": error_feedback})

    raise RuntimeError(
        f"Failed to get a valid action after {max_retries} attempts. "
        f"Last error: {last_error}"
    )
