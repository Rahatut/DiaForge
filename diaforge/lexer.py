from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Token:
    kind: str
    value: str
    pos: int


TOKEN_RE = re.compile(
    r"""
    (?P<WS>\s+)
    |
    (?P<COMMENT>//[^\n]*|\#[^\n]*)
    |
    (?P<STRING>"(?:\\.|[^"\\])*")
    |
    (?P<ARROW><->|->|~>)
    |
    (?P<NUMBER>-?(?:\d+(?:\.\d*)?|\.\d+))
    |
    (?P<ID>[A-Za-z_][A-Za-z0-9_.-]*)
    |
    (?P<SYM>[{}:;,=\[\]\(\)])
    """,
    re.X,
)


def decode_string(value: str) -> str:
    """
    Convert a quoted source-language string into Python text.

    Example:

        "hello\\nworld"

    becomes:

        hello
        world
    """

    body = value[1:-1]

    try:
        return bytes(
            body,
            "utf-8",
        ).decode("unicode_escape")
    except UnicodeDecodeError:
        return body


def lex(text: str):
    """
    Tokenize DiaForge source code.

    Supported:

        identifiers
        strings
        numbers
        comments
        arrows
        punctuation
    """

    pos = 0
    length = len(text)

    while pos < length:

        match = TOKEN_RE.match(
            text,
            pos,
        )

        if not match:
            raise SyntaxError(
                f"Unexpected character "
                f"at position {pos}: "
                f"{text[pos]!r}"
            )

        pos = match.end()

        kind = match.lastgroup
        value = match.group()

        # Ignore whitespace and comments.
        if kind in {
            "WS",
            "COMMENT",
        }:
            continue

        if kind == "STRING":
            value = decode_string(value)

        yield Token(
            kind=kind,
            value=value,
            pos=match.start(),
        )

    yield Token(
        kind="EOF",
        value="",
        pos=pos,
    )