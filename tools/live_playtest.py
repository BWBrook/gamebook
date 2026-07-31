from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import shutil
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


def _validated_names(names: Sequence[str], label: str) -> list[str]:
    """Return stripped, case-insensitively unique names."""
    result: list[str] = []
    seen: set[str] = set()
    for name in names:
        if not isinstance(name, str) or not name.strip():
            raise HarnessError(f"{label} names must be non-empty")
        cleaned = name.strip()
        key = cleaned.casefold()
        if key in seen:
            raise HarnessError(f"duplicate {label} name {cleaned!r}")
        seen.add(key)
        result.append(cleaned)
    return result


def build_initial_state(
    attributes: dict[str, int],
    resources: dict[str, tuple[int, int]],
    pressure: tuple[str, int, int],
    possessions: Sequence[str],
    story_marks: Sequence[str],
    start_passage: str,
) -> JSONDict:
    """Validate and construct the complete version-1 active-session state."""
    if not isinstance(attributes, dict) or not attributes:
        raise HarnessError("at least one attribute is required")
    attribute_names = _validated_names(list(attributes), "attribute")
    validated_attributes: JSONDict = {}
    for original_name, name in zip(attributes, attribute_names, strict=True):
        value = attributes[original_name]
        if type(value) is not int or not 0 <= value <= 20:
            raise HarnessError(f"attribute {name} must be an integer from 0 through 20")
        validated_attributes[name] = value

    if not isinstance(resources, dict):
        raise HarnessError("resources must be a mapping")
    resource_names = _validated_names(list(resources), "resource")
    resource_lookup = {
        name.casefold(): resources[original_name]
        for original_name, name in zip(resources, resource_names, strict=True)
    }
    if set(resource_lookup) != {"fortune", "stamina"}:
        raise HarnessError("resources must contain exactly Fortune and Stamina")
    validated_resources: JSONDict = {}
    for canonical_name in ("Fortune", "Stamina"):
        values = resource_lookup[canonical_name.casefold()]
        if not isinstance(values, tuple) or len(values) != 2:
            raise HarnessError(
                f"resource {canonical_name} must be a CURRENT/MAXIMUM pair"
            )
        current, maximum = values
        if type(current) is not int or type(maximum) is not int or not 0 <= current <= maximum:
            raise HarnessError(
                f"resource {canonical_name} must satisfy 0 <= current <= maximum"
            )
        validated_resources[canonical_name] = {
            "current": current,
            "maximum": maximum,
        }

    if not isinstance(pressure, tuple) or len(pressure) != 3:
        raise HarnessError("pressure must be a NAME/CURRENT/MAXIMUM tuple")
    pressure_name, pressure_current, pressure_maximum = pressure
    if not isinstance(pressure_name, str) or not pressure_name.strip():
        raise HarnessError("pressure name must be non-empty")
    if (
        type(pressure_current) is not int
        or type(pressure_maximum) is not int
        or not 0 <= pressure_current <= pressure_maximum
    ):
        raise HarnessError("pressure must satisfy 0 <= current <= maximum")

    if not isinstance(start_passage, str) or re.fullmatch(r"[SE]\d{2}", start_passage) is None:
        raise HarnessError("start passage must match [SE]\\d{2}")

    return {
        "attributes": copy.deepcopy(validated_attributes),
        "resources": copy.deepcopy(validated_resources),
        "pressure": {
            "name": pressure_name.strip(),
            "current": pressure_current,
            "maximum": pressure_maximum,
        },
        "possessions": _validated_names(possessions, "possession"),
        "story_marks": _validated_names(story_marks, "story mark"),
        "current_passage": start_passage,
        "status": "active",
    }


def _validate_initial_state(state: JSONDict) -> JSONDict:
    expected_keys = {
        "attributes",
        "resources",
        "pressure",
        "possessions",
        "story_marks",
        "current_passage",
        "status",
    }
    if not isinstance(state, dict) or set(state) != expected_keys:
        raise HarnessError("initial state is not a version-1 state")
    resources = state["resources"]
    pressure = state["pressure"]
    if not isinstance(resources, dict) or not isinstance(pressure, dict):
        raise HarnessError("initial state is not a version-1 state")
    try:
        rebuilt = build_initial_state(
            attributes=state["attributes"],
            resources={
                name: (values["current"], values["maximum"])
                for name, values in resources.items()
                if isinstance(values, dict)
            },
            pressure=(
                pressure["name"],
                pressure["current"],
                pressure["maximum"],
            ),
            possessions=state["possessions"],
            story_marks=state["story_marks"],
            start_passage=state["current_passage"],
        )
    except (KeyError, TypeError, HarnessError) as error:
        raise HarnessError("initial state is not a version-1 state") from error
    if state.get("status") != "active" or state != rebuilt:
        raise HarnessError("initial state is not a version-1 state")
    return copy.deepcopy(rebuilt)


def _snapshot(state: JSONDict, workflow: JSONDict) -> JSONDict:
    return {
        "state": copy.deepcopy(state),
        "workflow": copy.deepcopy(workflow),
    }


def _atomic_write_json(path: Path, payload: JSONDict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def _append_json_line(path: Path, payload: JSONDict) -> None:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(encoded + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _validate_session_id(session_id: str) -> None:
    if not isinstance(session_id, str) or SESSION_ID.fullmatch(session_id) is None:
        raise HarnessError(f"invalid session identifier {session_id!r}")


def _reader_file_record(path: Path) -> JSONDict:
    resolved = path.expanduser().resolve()
    return {"path": str(resolved), "sha256": sha256_file(resolved)}


def start_session(
    sessions_dir: Path,
    session_id: str,
    story_path: Path,
    rules_path: Path,
    sheet_path: Path,
    purpose: str,
    hypothesis: str | None,
    initial_state: JSONDict,
    clock: Clock = utc_now,
) -> LoadedSession:
    """Start an atomically-created session with its first authoritative event."""
    _validate_session_id(session_id)
    if not isinstance(purpose, str) or not purpose.strip():
        raise HarnessError("session purpose must be non-empty")
    if hypothesis is not None and (not isinstance(hypothesis, str) or not hypothesis.strip()):
        raise HarnessError("session hypothesis must be non-empty when supplied")

    sessions_path = Path(sessions_dir)
    directory = sessions_path / session_id
    if directory.exists():
        raise HarnessError(f"session {session_id!r} already exists")

    state = _validate_initial_state(initial_state)
    resolved_story = Path(story_path).expanduser().resolve()
    resolved_rules = Path(rules_path).expanduser().resolve()
    resolved_sheet = Path(sheet_path).expanduser().resolve()
    passages = index_passages(resolved_story)
    index_rule_sections(resolved_rules)
    if state["current_passage"] not in passages:
        raise HarnessError(
            f"undefined start passage {state['current_passage']}"
        )
    reader_files = {
        "story": _reader_file_record(resolved_story),
        "rules": _reader_file_record(resolved_rules),
        "sheet": _reader_file_record(resolved_sheet),
    }
    workflow: JSONDict = {"choice": None, "roll": None}
    timestamp = clock()
    event: JSONDict = {
        "number": 1,
        "type": "session_started",
        "timestamp": timestamp,
        "passage": state["current_passage"],
        "data": {
            "purpose": purpose,
            "hypothesis": hypothesis,
            "reader_files": copy.deepcopy(reader_files),
            "dice_mode": "physical",
            "observer_mode": "neutral",
        },
        "before": None,
        "after": _snapshot(state, workflow),
    }
    document: JSONDict = {
        "format_version": FORMAT_VERSION,
        "harness_version": HARNESS_VERSION,
        "session_id": session_id,
        "purpose": purpose,
        "hypothesis": hypothesis,
        "reader_files": copy.deepcopy(reader_files),
        "dice_mode": "physical",
        "observer_mode": "neutral",
        "initial_state": copy.deepcopy(state),
        "current_state": copy.deepcopy(state),
        "workflow": copy.deepcopy(workflow),
        "last_event": 1,
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    sessions_path.mkdir(parents=True, exist_ok=True)
    temporary_directory = Path(
        tempfile.mkdtemp(prefix=f".{session_id}.", dir=sessions_path)
    )
    try:
        _append_json_line(temporary_directory / "events.jsonl", event)
        _atomic_write_json(temporary_directory / "session.json", document)
        if directory.exists():
            raise HarnessError(f"session {session_id!r} already exists")
        os.rename(temporary_directory, directory)
    except BaseException:
        shutil.rmtree(temporary_directory, ignore_errors=True)
        raise

    return LoadedSession(
        directory=directory,
        document=copy.deepcopy(document),
        events=[copy.deepcopy(event)],
        state=copy.deepcopy(state),
        workflow=copy.deepcopy(workflow),
    )


def read_events(path: Path) -> list[JSONDict]:
    events: list[JSONDict] = []
    try:
        with path.open("r", encoding="utf-8", newline=None) as handle:
            for line_number, line in enumerate(handle, start=1):
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as error:
                    raise HarnessError(
                        f"invalid JSON event at line {line_number}: {error.msg}"
                    ) from error
                if not isinstance(event, dict):
                    raise HarnessError(f"event at line {line_number} is not an object")
                events.append(event)
    except (OSError, UnicodeError) as error:
        raise HarnessError(f"cannot read event log {path}: {error}") from error
    return events


def replay_events(events: Sequence[JSONDict]) -> JSONDict:
    if not events:
        raise HarnessError("event log is empty")

    previous: JSONDict | None = None
    for expected_number, event in enumerate(events, start=1):
        if event.get("number") != expected_number:
            raise HarnessError(
                f"event number mismatch: expected {expected_number}, "
                f"received {event.get('number')!r}"
            )
        if expected_number == 1:
            if event.get("type") != "session_started" or event.get("before") is not None:
                raise HarnessError("event 1 must be session_started with before null")
        elif event.get("before") != previous:
            raise HarnessError(
                f"event {expected_number} before snapshot does not match event "
                f"{expected_number - 1}"
            )
        after = event.get("after")
        if not isinstance(after, dict) or set(after) != {"state", "workflow"}:
            raise HarnessError(f"event {expected_number} has an invalid after snapshot")
        previous = after

    return copy.deepcopy(previous)


def _read_json_document(path: Path) -> JSONDict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise HarnessError(f"cannot read session cache {path}: {error}") from error
    if not isinstance(payload, dict):
        raise HarnessError(f"session cache {path} is not an object")
    return payload


def _verify_reader_hashes(document: JSONDict) -> None:
    reader_files = document.get("reader_files")
    if not isinstance(reader_files, dict) or set(reader_files) != {"story", "rules", "sheet"}:
        raise HarnessError("session cache has invalid reader files")
    for label in ("story", "rules", "sheet"):
        record = reader_files[label]
        if not isinstance(record, dict) or set(record) != {"path", "sha256"}:
            raise HarnessError(f"session cache has invalid {label} reader record")
        stored_path = record["path"]
        stored_hash = record["sha256"]
        if not isinstance(stored_path, str) or not isinstance(stored_hash, str):
            raise HarnessError(f"session cache has invalid {label} reader record")
        path = Path(stored_path)
        if not path.is_absolute():
            raise HarnessError(f"session cache has non-absolute {label} reader path")
        if sha256_file(path) != stored_hash:
            raise HarnessError(f"reader file changed: {label}")


def load_session(
    sessions_dir: Path,
    session_id: str,
    *,
    verify_hashes: bool = True,
    verify_cache: bool = True,
) -> LoadedSession:
    _validate_session_id(session_id)
    directory = Path(sessions_dir) / session_id
    document = _read_json_document(directory / "session.json")
    if document.get("format_version") != FORMAT_VERSION:
        raise HarnessError("unsupported session format version")
    if document.get("harness_version") != HARNESS_VERSION:
        raise HarnessError("unsupported harness version")
    if verify_hashes:
        _verify_reader_hashes(document)
    events = read_events(directory / "events.jsonl")
    snapshot = replay_events(events)
    if verify_cache and (
        document.get("current_state") != snapshot["state"]
        or document.get("workflow") != snapshot["workflow"]
        or document.get("last_event") != len(events)
    ):
        raise HarnessError(
            "session cache does not match the event log; run recover-cache"
        )
    return LoadedSession(
        directory=directory,
        document=document,
        events=events,
        state=copy.deepcopy(snapshot["state"]),
        workflow=copy.deepcopy(snapshot["workflow"]),
    )


def append_event(
    loaded: LoadedSession,
    event_type: str,
    data: JSONDict,
    new_state: JSONDict,
    new_workflow: JSONDict,
    clock: Clock = utc_now,
) -> JSONDict:
    """Persist a new event before atomically updating the derived cache."""
    before = _snapshot(loaded.state, loaded.workflow)
    after = _snapshot(new_state, new_workflow)
    number = loaded.document["last_event"] + 1
    timestamp = clock()
    event: JSONDict = {
        "number": number,
        "type": event_type,
        "timestamp": timestamp,
        "passage": loaded.state["current_passage"],
        "data": copy.deepcopy(data),
        "before": before,
        "after": after,
    }
    document = copy.deepcopy(loaded.document)
    document["current_state"] = copy.deepcopy(after["state"])
    document["workflow"] = copy.deepcopy(after["workflow"])
    document["last_event"] = number
    document["updated_at"] = timestamp
    _append_json_line(loaded.directory / "events.jsonl", event)
    _atomic_write_json(loaded.directory / "session.json", document)

    loaded.document = document
    loaded.events.append(copy.deepcopy(event))
    loaded.state = copy.deepcopy(after["state"])
    loaded.workflow = copy.deepcopy(after["workflow"])
    return copy.deepcopy(event)


def recover_cache(
    sessions_dir: Path,
    session_id: str,
    clock: Clock = utc_now,
) -> LoadedSession:
    loaded = load_session(sessions_dir, session_id, verify_cache=False)
    document = copy.deepcopy(loaded.document)
    document["current_state"] = copy.deepcopy(loaded.state)
    document["workflow"] = copy.deepcopy(loaded.workflow)
    document["last_event"] = len(loaded.events)
    document["updated_at"] = clock()
    _atomic_write_json(loaded.directory / "session.json", document)
    loaded.document = document
    return loaded
