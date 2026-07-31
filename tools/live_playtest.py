from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FORMAT_VERSION = 1
HARNESS_VERSION = "0.1.0"
PASSAGE_HEADING = re.compile(
    r"^## (?P<identifier>[SE]\d{2}) — (?P<title>\S.*)$"
)
H2_HEADING = re.compile(r"^## (?P<title>\S.*)$")
SESSION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")

JSONDict = dict[str, Any]
Clock = Callable[[], str]


class HarnessError(ValueError):
    pass


@dataclass
class LoadedSession:
    directory: Path
    document: JSONDict
    events: list[JSONDict]
    state: JSONDict
    workflow: JSONDict


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    try:
        payload = path.read_bytes()
    except OSError as error:
        raise HarnessError(f"cannot read {path}: {error}") from error
    return hashlib.sha256(payload).hexdigest()


def _markdown_lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        raise HarnessError(f"cannot read UTF-8 Markdown {path}: {error}") from error


def _blocks(
    lines: Sequence[str],
    starts: Sequence[int],
) -> list[tuple[str, str]]:
    blocks: list[tuple[str, str]] = []
    for position, start in enumerate(starts):
        end = starts[position + 1] if position + 1 < len(starts) else len(lines)
        text = "\n".join(lines[start:end]).rstrip() + "\n"
        blocks.append((lines[start], text))
    return blocks


def index_passages(path: Path) -> dict[str, str]:
    lines = _markdown_lines(path)
    starts = [
        index
        for index, line in enumerate(lines)
        if PASSAGE_HEADING.fullmatch(line) is not None
    ]
    passages: dict[str, str] = {}
    for heading, block in _blocks(lines, starts):
        match = PASSAGE_HEADING.fullmatch(heading)
        if match is None:
            raise HarnessError(f"internal passage-index error at {heading!r}")
        identifier = match.group("identifier")
        if identifier in passages:
            raise HarnessError(f"duplicate passage {identifier} in {path}")
        passages[identifier] = block
    if not passages:
        raise HarnessError(f"no passage headings found in {path}")
    return passages


def index_rule_sections(path: Path) -> dict[str, str]:
    lines = _markdown_lines(path)
    starts = [
        index
        for index, line in enumerate(lines)
        if H2_HEADING.fullmatch(line) is not None
    ]
    sections: dict[str, str] = {}
    for heading, block in _blocks(lines, starts):
        match = H2_HEADING.fullmatch(heading)
        if match is None:
            raise HarnessError(f"internal rules-index error at {heading!r}")
        key = match.group("title").casefold()
        if key in sections:
            raise HarnessError(f"duplicate rules section {match.group('title')} in {path}")
        sections[key] = block
    if not sections:
        raise HarnessError(f"no rules sections found in {path}")
    return sections


def parse_named_integer(value: str) -> tuple[str, int]:
    match = re.fullmatch(r"([^=]+)=(-?\d+)", value)
    if match is None:
        raise HarnessError(f"expected NAME=VALUE, received {value!r}")
    return match.group(1).strip(), int(match.group(2))


def parse_named_bound(value: str) -> tuple[str, int, int]:
    match = re.fullmatch(r"([^=]+)=(-?\d+)/(-?\d+)", value)
    if match is None:
        raise HarnessError(
            f"expected NAME=CURRENT/MAXIMUM, received {value!r}"
        )
    return match.group(1).strip(), int(match.group(2)), int(match.group(3))
