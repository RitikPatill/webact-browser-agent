from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import Field, TypeAdapter
from pydantic import BaseModel


class NavigateAction(BaseModel):
    type: Literal["navigate"]
    url: str


class ClickAction(BaseModel):
    type: Literal["click"]
    label: str


class TypeAction(BaseModel):
    type: Literal["type"]
    label: str
    text: str


class ScrollAction(BaseModel):
    type: Literal["scroll"]
    direction: Literal["up", "down"]
    amount: int = 300


class ExtractTextAction(BaseModel):
    type: Literal["extract_text"]
    description: str


class DoneAction(BaseModel):
    type: Literal["done"]
    result: str


Action = Annotated[
    Union[
        NavigateAction,
        ClickAction,
        TypeAction,
        ScrollAction,
        ExtractTextAction,
        DoneAction,
    ],
    Field(discriminator="type"),
]

_adapter: TypeAdapter[Action] = TypeAdapter(Action)


def parse_action(data: dict) -> Action:
    """Validate a raw dict from Claude into a typed Action."""
    return _adapter.validate_python(data)
