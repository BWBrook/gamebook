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


def resolve_roll(
    attribute: str,
    target: int,
    mode: str,
    dice: Sequence[int],
) -> JSONDict:
    """Resolve reported physical d20 faces without generating any randomness."""
    expected_count = {"standard": 1, "advantage": 2, "disadvantage": 2}
    if mode not in expected_count:
        raise HarnessError(f"unknown roll mode {mode!r}")
    if len(dice) != expected_count[mode]:
        dice_label = "one die" if expected_count[mode] == 1 else "two dice"
        raise HarnessError(
            f"{mode} requires {dice_label}, received {len(dice)}"
        )
    if any(type(face) is not int or not 1 <= face <= 20 for face in dice):
        raise HarnessError(
            f"d20 faces must be integers from 1 through 20: {list(dice)}"
        )

    if mode == "advantage":
        selected_die = min(dice)
    elif mode == "disadvantage":
        selected_die = max(dice)
    else:
        selected_die = dice[0]
    selected_index = list(dice).index(selected_die)
    natural = selected_die if selected_die in {1, 20} else None
    margin = target - selected_die

    return {
        "attribute": attribute,
        "target": target,
        "mode": mode,
        "dice": list(dice),
        "selected_die": selected_die,
        "selected_index": selected_index,
        "natural": natural,
        "provisional_margin": margin,
        "margin_is_resolution_inert": natural is not None,
        "fortune_status": "forbidden" if natural is not None else "pending",
        "fortune_spent": 0 if natural is not None else None,
        "final_die": selected_die if natural is not None else None,
        "final_margin": margin if natural is not None else None,
        "success": selected_die == 1 if natural is not None else None,
    }


def apply_fortune(roll: JSONDict, spend: int, available_fortune: int) -> JSONDict:
    """Return an ordinary roll finalised after an explicit Fortune decision."""
    if type(spend) is not int or spend < 0:
        raise HarnessError("Fortune spend must be a non-negative integer")
    if roll.get("natural") is not None or roll.get("fortune_status") == "forbidden":
        raise HarnessError("cannot spend Fortune on a locked natural")
    if type(available_fortune) is not int or available_fortune < 0:
        raise HarnessError("available Fortune must be a non-negative integer")
    if spend > available_fortune:
        raise HarnessError(
            f"cannot spend {spend} Fortune; only {available_fortune} Fortune available"
        )

    result = copy.deepcopy(roll)
    result["fortune_status"] = "decided"
    result["fortune_spent"] = spend
    result["final_die"] = result["selected_die"] - spend
    result["final_margin"] = result["target"] - result["final_die"]
    result["success"] = result["final_die"] <= result["target"]
    return result


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
    if pressure_name.strip() != "Exposure" or pressure_maximum != 5:
        raise HarnessError("pressure must be Exposure on the exact 0/5 track")

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


def _verify_start_metadata(document: JSONDict, events: Sequence[JSONDict]) -> JSONDict:
    start_event = events[0]
    data = start_event.get("data")
    if not isinstance(data, dict):
        raise HarnessError("event 1 has invalid session-start metadata")
    for field in (
        "purpose",
        "hypothesis",
        "reader_files",
        "dice_mode",
        "observer_mode",
    ):
        if field not in data or document.get(field) != data[field]:
            raise HarnessError(
                "session cache differs from authoritative session-start metadata"
            )
    start_state = start_event["after"]["state"]
    if document.get("initial_state") != start_state:
        raise HarnessError(
            "session cache differs from authoritative session-start metadata"
        )
    return data


def _verify_identity_metadata(
    document: JSONDict,
    events: Sequence[JSONDict],
    session_id: str,
) -> None:
    if (
        document.get("session_id") != session_id
        or not events
        or document.get("created_at") != events[0].get("timestamp")
    ):
        raise HarnessError(
            "session cache differs from authoritative identity metadata"
        )


def _verify_reader_hashes(reader_files: JSONDict) -> None:
    if not isinstance(reader_files, dict) or set(reader_files) != {"story", "rules", "sheet"}:
        raise HarnessError("session-start metadata has invalid reader files")
    for label in ("story", "rules", "sheet"):
        record = reader_files[label]
        if not isinstance(record, dict) or set(record) != {"path", "sha256"}:
            raise HarnessError(f"session-start metadata has invalid {label} reader record")
        stored_path = record["path"]
        stored_hash = record["sha256"]
        if not isinstance(stored_path, str) or not isinstance(stored_hash, str):
            raise HarnessError(f"session-start metadata has invalid {label} reader record")
        path = Path(stored_path)
        if not path.is_absolute():
            raise HarnessError(f"session-start metadata has non-absolute {label} reader path")
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
    events = read_events(directory / "events.jsonl")
    snapshot = replay_events(events)
    start_metadata = _verify_start_metadata(document, events)
    if verify_hashes:
        _verify_reader_hashes(start_metadata["reader_files"])
    if verify_cache:
        _verify_identity_metadata(document, events, session_id)
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
    authoritative_events = read_events(loaded.directory / "events.jsonl")
    start_metadata = _verify_start_metadata(loaded.document, authoritative_events)
    _verify_reader_hashes(start_metadata["reader_files"])
    _append_json_line(loaded.directory / "events.jsonl", event)
    _atomic_write_json(loaded.directory / "session.json", document)

    loaded.document = document
    loaded.events.append(copy.deepcopy(event))
    loaded.state = copy.deepcopy(after["state"])
    loaded.workflow = copy.deepcopy(after["workflow"])
    return copy.deepcopy(event)


def _require_active(loaded: LoadedSession, operation: str) -> None:
    status = loaded.state["status"]
    if status != "active":
        raise HarnessError(
            f"cannot {operation} while session status is {status}"
        )


def _require_status(
    loaded: LoadedSession,
    expected_status: str,
    operation: str,
) -> None:
    status = loaded.state["status"]
    if status != expected_status:
        raise HarnessError(
            f"cannot {operation} while session status is {status}"
        )


def _non_empty_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise HarnessError(f"{label} must be non-empty")
    return value.strip()


def _resource_name(loaded: LoadedSession, requested_name: Any) -> str:
    cleaned = _non_empty_text(requested_name, "resource name")
    names = {name.casefold(): name for name in loaded.state["resources"]}
    try:
        return names[cleaned.casefold()]
    except KeyError as error:
        raise HarnessError(f"unknown resource {requested_name!r}") from error


def _collection_item_index(items: Sequence[str], name: str) -> int | None:
    requested = name.casefold()
    for index, item in enumerate(items):
        if item.casefold() == requested:
            return index
    return None


def change_resource(
    loaded: LoadedSession,
    name: str,
    delta: int,
    reason: str,
    clock: Clock = utc_now,
) -> JSONDict:
    """Record a bounded resource change as an authoritative event."""
    _require_active(loaded, "change resource")
    canonical_name = _resource_name(loaded, name)
    if type(delta) is not int:
        raise HarnessError("resource delta must be an integer")
    _non_empty_text(reason, "resource change reason")
    resource = loaded.state["resources"][canonical_name]
    current = resource["current"]
    maximum = resource["maximum"]
    after = current + delta
    if not 0 <= after <= maximum:
        raise HarnessError(
            f"resource {canonical_name} change result {after} is outside 0/{maximum}"
        )
    state = copy.deepcopy(loaded.state)
    state["resources"][canonical_name]["current"] = after
    return append_event(
        loaded,
        "resource_changed",
        {
            "name": canonical_name,
            "delta": delta,
            "before": current,
            "after": after,
            "reason": reason,
        },
        state,
        loaded.workflow,
        clock,
    )


def change_pressure(
    loaded: LoadedSession,
    delta: int,
    reason: str,
    clock: Clock = utc_now,
) -> JSONDict:
    """Record a bounded pressure change, saturating positive increases."""
    _require_active(loaded, "change pressure")
    if type(delta) is not int:
        raise HarnessError("pressure delta must be an integer")
    _non_empty_text(reason, "pressure change reason")
    pressure = loaded.state["pressure"]
    current = pressure["current"]
    if (
        pressure.get("name") != "Exposure"
        or pressure.get("maximum") != 5
        or type(current) is not int
        or not 0 <= current <= 5
    ):
        raise HarnessError("pressure must be Exposure on the exact 0/5 track")
    requested_after = current + delta
    if requested_after < 0:
        raise HarnessError("pressure change result is below 0")
    after = min(5, requested_after)
    applied_delta = after - current
    state = copy.deepcopy(loaded.state)
    state["pressure"]["current"] = after
    return append_event(
        loaded,
        "pressure_changed",
        {
            "name": pressure["name"],
            "requested_delta": delta,
            "applied_delta": applied_delta,
            "before": current,
            "after": after,
            "reason": reason,
        },
        state,
        loaded.workflow,
        clock,
    )


def change_collection(
    loaded: LoadedSession,
    collection: str,
    action: str,
    name: str,
    reason: str,
    *,
    allow_duplicate: bool = False,
    clock: Clock = utc_now,
) -> JSONDict:
    """Record an ordered possession or story-mark change without rewriting history."""
    _require_active(loaded, "change collection")
    if collection not in {"possessions", "story_marks"}:
        raise HarnessError(f"unknown collection {collection!r}")
    if action not in {"add", "consume", "remove"}:
        raise HarnessError(f"unknown collection action {action!r}")
    cleaned_name = _non_empty_text(name, "collection item name")
    _non_empty_text(reason, "collection change reason")
    if type(allow_duplicate) is not bool:
        raise HarnessError("allow_duplicate must be a boolean")
    items = loaded.state[collection]
    matching_index = _collection_item_index(items, cleaned_name)
    if action == "add":
        if matching_index is not None and not allow_duplicate:
            raise HarnessError(f"{collection[:-1]} {cleaned_name!r} is already present")
    elif matching_index is None:
        raise HarnessError(f"{collection[:-1]} {cleaned_name!r} is not present")

    state = copy.deepcopy(loaded.state)
    updated_items = state[collection]
    if action == "add":
        updated_items.append(cleaned_name)
    else:
        assert matching_index is not None
        del updated_items[matching_index]
    event_type = "possession_changed" if collection == "possessions" else "story_mark_changed"
    return append_event(
        loaded,
        event_type,
        {
            "action": action,
            "name": cleaned_name,
            "reason": reason,
            "allow_duplicate": allow_duplicate,
        },
        state,
        loaded.workflow,
        clock,
    )


def pause_session(
    loaded: LoadedSession,
    reason: str,
    clock: Clock = utc_now,
) -> JSONDict:
    _require_active(loaded, "pause")
    _non_empty_text(reason, "pause reason")
    state = copy.deepcopy(loaded.state)
    state["status"] = "paused"
    return append_event(
        loaded,
        "session_paused",
        {"reason": reason},
        state,
        loaded.workflow,
        clock,
    )


def resume_session(
    loaded: LoadedSession,
    clock: Clock = utc_now,
) -> JSONDict:
    """Resume a freshly verified paused session, rechecking reader hashes."""
    _require_status(loaded, "paused", "resume")
    session_id = loaded.document.get("session_id")
    if not isinstance(session_id, str):
        raise HarnessError("session cache has invalid session identifier")
    verified = load_session(loaded.directory.parent, session_id)
    if (
        verified.document != loaded.document
        or verified.events != loaded.events
        or verified.state != loaded.state
        or verified.workflow != loaded.workflow
    ):
        raise HarnessError("session must be freshly verified before resuming")
    state = copy.deepcopy(loaded.state)
    state["status"] = "active"
    return append_event(
        loaded,
        "session_resumed",
        {},
        state,
        loaded.workflow,
        clock,
    )


def finish_session(
    loaded: LoadedSession,
    outcome: str,
    clock: Clock = utc_now,
) -> JSONDict:
    _require_active(loaded, "finish")
    _non_empty_text(outcome, "outcome")
    state = copy.deepcopy(loaded.state)
    state["status"] = "finished"
    return append_event(
        loaded,
        "session_finished",
        {"outcome": outcome},
        state,
        loaded.workflow,
        clock,
    )


def _correction_arguments(
    *,
    name: str | None,
    value: Any,
    replacement_text: str | None,
) -> JSONDict:
    return {
        key: argument
        for key, argument in (
            ("name", name),
            ("value", value),
            ("replacement_text", replacement_text),
        )
        if argument is not None
    }


def _require_no_correction_extras(
    *,
    name: str | None,
    value: Any,
    replacement_text: str | None,
) -> None:
    if name is not None or value is not None or replacement_text is not None:
        raise HarnessError("correction operation received unsupported arguments")


def correct_session(
    loaded: LoadedSession,
    target_event: int,
    reason: str,
    operation: str,
    *,
    name: str | None = None,
    value: Any = None,
    replacement_text: str | None = None,
    clock: Clock = utc_now,
) -> JSONDict:
    """Append a compensating correction while preserving every earlier event."""
    _require_active(loaded, "correct session")
    if type(target_event) is not int or not any(
        event["number"] == target_event for event in loaded.events
    ):
        raise HarnessError(f"correction target event {target_event!r} does not exist")
    _non_empty_text(reason, "correction reason")
    if operation not in {
        "annotate",
        "set-resource",
        "set-pressure",
        "add-possession",
        "remove-possession",
        "add-mark",
        "remove-mark",
        "set-passage",
        "clear-workflow",
    }:
        raise HarnessError(f"unknown correction operation {operation!r}")

    state = copy.deepcopy(loaded.state)
    workflow = copy.deepcopy(loaded.workflow)
    arguments = _correction_arguments(
        name=name,
        value=value,
        replacement_text=replacement_text,
    )
    if operation == "annotate":
        replacement = _non_empty_text(replacement_text, "replacement text")
        if name is not None or value is not None:
            raise HarnessError("annotate correction received unsupported arguments")
        compensation = "recorded corrected wording"
    elif operation == "set-resource":
        if replacement_text is not None:
            raise HarnessError("set-resource correction received unsupported arguments")
        canonical_name = _resource_name(loaded, name)
        resource = state["resources"][canonical_name]
        if type(value) is not int or not 0 <= value <= resource["maximum"]:
            raise HarnessError(
                f"resource {canonical_name} correction value is outside 0/{resource['maximum']}"
            )
        state["resources"][canonical_name]["current"] = value
        arguments["name"] = canonical_name
        compensation = f"set {canonical_name} to {value}"
    elif operation == "set-pressure":
        if name is not None or replacement_text is not None:
            raise HarnessError("set-pressure correction received unsupported arguments")
        if type(value) is not int or not 0 <= value <= 5:
            raise HarnessError("pressure correction value is outside 0/5")
        state["pressure"]["current"] = value
        compensation = f"set {state['pressure']['name']} to {value}"
    elif operation in {"add-possession", "remove-possession", "add-mark", "remove-mark"}:
        if value is not None or replacement_text is not None:
            raise HarnessError(f"{operation} correction received unsupported arguments")
        cleaned_name = _non_empty_text(name, "collection item name")
        collection = "possessions" if operation.endswith("possession") else "story_marks"
        item_index = _collection_item_index(state[collection], cleaned_name)
        adding = operation.startswith("add-")
        if adding:
            if item_index is not None:
                raise HarnessError(f"{collection[:-1]} {cleaned_name!r} is already present")
            state[collection].append(cleaned_name)
            compensation = f"added {cleaned_name} to {collection}"
        else:
            if item_index is None:
                raise HarnessError(f"{collection[:-1]} {cleaned_name!r} is not present")
            del state[collection][item_index]
            compensation = f"removed {cleaned_name} from {collection}"
    elif operation == "set-passage":
        if name is not None or replacement_text is not None:
            raise HarnessError("set-passage correction received unsupported arguments")
        if not isinstance(value, str):
            raise HarnessError("passage correction value must be a passage identifier")
        passages = index_passages(_reader_path(loaded, "story"))
        if value not in passages:
            raise HarnessError(f"undefined passage {value}")
        state["current_passage"] = value
        compensation = f"set current passage to {value}"
    else:
        _require_no_correction_extras(
            name=name,
            value=value,
            replacement_text=replacement_text,
        )
        workflow = {"choice": None, "roll": None}
        compensation = "cleared pending choice and roll workflow"

    return append_event(
        loaded,
        "correction",
        {
            "target_event": target_event,
            "reason": reason,
            "operation": operation,
            "arguments": arguments,
            "compensation": compensation,
        },
        state,
        workflow,
        clock,
    )


def _reader_path(loaded: LoadedSession, label: str) -> Path:
    return Path(loaded.document["reader_files"][label]["path"])


def show_current_passage(
    loaded: LoadedSession,
    clock: Clock = utc_now,
) -> str:
    _require_active(loaded, "show passage")
    passage = loaded.state["current_passage"]
    passages = index_passages(_reader_path(loaded, "story"))
    try:
        shown = passages[passage]
    except KeyError as error:
        raise HarnessError(f"undefined passage {passage}") from error
    append_event(
        loaded,
        "passage_shown",
        {},
        loaded.state,
        loaded.workflow,
        clock,
    )
    return shown


def format_state(state: JSONDict) -> str:
    attributes = " | ".join(
        f"{name} {value}"
        for name, value in sorted(state["attributes"].items())
    )
    resources = [
        f"{name}: {values['current']}/{values['maximum']}"
        for name, values in sorted(state["resources"].items())
    ]
    pressure = state["pressure"]
    possessions = " | ".join(state["possessions"]) or "—"
    story_marks = " | ".join(state["story_marks"]) or "—"
    return "\n".join(
        [
            f"Passage: {state['current_passage']}",
            f"Status: {state['status']}",
            f"Attributes: {attributes}",
            *resources,
            (
                f"{pressure['name']}: {pressure['current']}/"
                f"{pressure['maximum']}"
            ),
            f"Possessions: {possessions}",
            f"Story marks: {story_marks}",
        ]
    )


def record_note(
    loaded: LoadedSession,
    kind: str,
    text: str,
    clock: Clock = utc_now,
) -> JSONDict:
    _require_active(loaded, "record note")
    event_types = {
        "player": "player_note",
        "operator": "operator_note",
        "rules-question": "rules_question",
    }
    if kind not in event_types:
        raise HarnessError(f"unknown note kind {kind!r}")
    if not isinstance(text, str) or not text.strip():
        raise HarnessError("note text must be non-empty")
    return append_event(
        loaded,
        event_types[kind],
        {"kind": kind, "text": text},
        loaded.state,
        loaded.workflow,
        clock,
    )


def record_rules_lookup(
    loaded: LoadedSession,
    section: str,
    clock: Clock = utc_now,
) -> str:
    _require_active(loaded, "look up rules")
    if not isinstance(section, str):
        raise HarnessError(f"unknown rules heading {section!r}")
    sections = index_rule_sections(_reader_path(loaded, "rules"))
    try:
        found = sections[section.casefold()]
    except KeyError as error:
        raise HarnessError(f"unknown rules heading {section!r}") from error
    match = H2_HEADING.fullmatch(found.splitlines()[0])
    if match is None:
        raise HarnessError("internal rules lookup error")
    canonical_heading = match.group("title")
    digest = hashlib.sha256(found.encode("utf-8")).hexdigest()
    append_event(
        loaded,
        "rules_lookup",
        {"section": canonical_heading, "sha256": digest},
        loaded.state,
        loaded.workflow,
        clock,
    )
    return found


def record_choice(
    loaded: LoadedSession,
    text: str,
    method: str | None,
    intended_destination: str | None,
    clock: Clock = utc_now,
) -> JSONDict:
    _require_active(loaded, "record choice")
    if not isinstance(text, str) or not text.strip():
        raise HarnessError("choice text must be non-empty")
    if loaded.workflow["choice"] is not None:
        raise HarnessError("cannot record a second unresolved choice")
    if (
        intended_destination is not None
        and (
            not isinstance(intended_destination, str)
            or re.fullmatch(r"[SE]\d{2}", intended_destination) is None
        )
    ):
        raise HarnessError("intended destination must match [SE]\\d{2}")

    choice_event = loaded.document["last_event"] + 1
    workflow = copy.deepcopy(loaded.workflow)
    workflow["choice"] = {
        "text": text,
        "method": method,
        "destination": intended_destination,
        "event": choice_event,
    }
    return append_event(
        loaded,
        "choice_committed",
        {
            "text": text,
            "method": method,
            "destination": intended_destination,
        },
        loaded.state,
        workflow,
        clock,
    )


def record_roll(
    loaded: LoadedSession,
    attribute: str,
    mode: str,
    dice: Sequence[int],
    clock: Clock = utc_now,
) -> JSONDict:
    """Record a reported physical roll against its target at this instant."""
    _require_active(loaded, "record roll")
    choice = loaded.workflow["choice"]
    if not isinstance(choice, dict):
        raise HarnessError("cannot record a roll without a committed choice")
    if loaded.workflow["roll"] is not None:
        raise HarnessError("cannot record a roll while an existing roll awaits transition")
    if not isinstance(attribute, str):
        raise HarnessError(f"unknown roll attribute {attribute!r}")

    requested_name = attribute.casefold()
    attributes = loaded.state["attributes"]
    attribute_names = {
        name.casefold(): name
        for name in attributes
    }
    resource_names = {
        name.casefold(): name
        for name in loaded.state["resources"]
    }
    if requested_name == "fortune":
        canonical_name = "Fortune"
        target = loaded.state["resources"][canonical_name]["current"]
    elif requested_name in attribute_names:
        canonical_name = attribute_names[requested_name]
        target = attributes[canonical_name]
    elif requested_name in resource_names:
        raise HarnessError(
            f"resource {resource_names[requested_name]!r} cannot be a roll target"
        )
    else:
        raise HarnessError(f"unknown roll attribute {attribute!r}")

    roll = resolve_roll(canonical_name, target, mode, dice)
    roll["choice_event"] = choice.get("event")
    workflow = copy.deepcopy(loaded.workflow)
    workflow["roll"] = copy.deepcopy(roll)
    return append_event(
        loaded,
        "roll_recorded",
        {"roll": roll},
        loaded.state,
        workflow,
        clock,
    )


def record_fortune(
    loaded: LoadedSession,
    spend: int,
    clock: Clock = utc_now,
) -> JSONDict:
    """Finalise the current ordinary roll with an explicit Fortune spend."""
    _require_active(loaded, "record Fortune decision")
    roll = loaded.workflow["roll"]
    if not isinstance(roll, dict):
        raise HarnessError("cannot decide Fortune without a pending ordinary roll")
    if roll.get("fortune_status") == "forbidden":
        raise HarnessError("cannot spend Fortune on a locked natural")
    if roll.get("fortune_status") != "pending":
        raise HarnessError("cannot decide Fortune without a pending ordinary roll")

    fortune = loaded.state["resources"].get("Fortune")
    if not isinstance(fortune, dict):
        raise HarnessError("Fortune resource is invalid")
    current = fortune.get("current")
    maximum = fortune.get("maximum")
    if (
        type(current) is not int
        or type(maximum) is not int
        or not 0 <= current <= maximum
    ):
        raise HarnessError("Fortune resource is invalid")

    final_roll = apply_fortune(roll, spend, current)
    new_current = current - spend
    if type(new_current) is not int or not 0 <= new_current <= maximum:
        raise HarnessError("Fortune resource is invalid")
    state = copy.deepcopy(loaded.state)
    state["resources"]["Fortune"]["current"] = new_current
    workflow = copy.deepcopy(loaded.workflow)
    workflow["roll"] = copy.deepcopy(final_roll)
    return append_event(
        loaded,
        "fortune_decided",
        {"spend": spend, "roll": final_roll},
        state,
        workflow,
        clock,
    )


def goto_passage(
    loaded: LoadedSession,
    destination: str,
    clock: Clock = utc_now,
) -> JSONDict:
    _require_active(loaded, "transition")
    choice = loaded.workflow["choice"]
    if not isinstance(choice, dict):
        raise HarnessError("cannot transition without a committed choice")
    roll = loaded.workflow["roll"]
    if isinstance(roll, dict) and roll.get("fortune_status") == "pending":
        raise HarnessError("cannot transition before the Fortune decision")

    passages = index_passages(_reader_path(loaded, "story"))
    if not isinstance(destination, str) or destination not in passages:
        raise HarnessError(f"undefined passage {destination}")
    current = loaded.state["current_passage"]
    _, _, passage_body = passages[current].partition("\n")
    if re.search(
        rf"(?<![A-Za-z0-9_]){re.escape(destination)}(?![A-Za-z0-9_])",
        passage_body,
    ) is None:
        raise HarnessError(
            f"destination {destination} is not referenced in passage {current}"
        )
    intended_destination = choice.get("destination")
    if intended_destination is not None and intended_destination != destination:
        raise HarnessError(
            f"destination {destination} does not match committed choice "
            f"destination {intended_destination}"
        )

    state = copy.deepcopy(loaded.state)
    state["current_passage"] = destination
    choice_event = choice.get("event")
    return append_event(
        loaded,
        "passage_transition",
        {"from": current, "to": destination, "choice_event": choice_event},
        state,
        {"choice": None, "roll": None},
        clock,
    )


def _report_cell(value: Any) -> str:
    """Return a value that is safe and readable in a Markdown table cell."""
    if value is None:
        text = "—"
    elif isinstance(value, bool):
        text = "yes" if value else "no"
    elif isinstance(value, (list, tuple)):
        text = ", ".join(str(item) for item in value)
    else:
        text = str(value)
    return text.replace("|", r"\|").replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")


def _report_table(headers: Sequence[str], rows: Sequence[Sequence[Any]]) -> list[str]:
    if not rows:
        return ["None recorded."]
    return [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *[
            "| " + " | ".join(_report_cell(value) for value in row) + " |"
            for row in rows
        ],
    ]


def _report_state(snapshot: Any) -> str:
    if not isinstance(snapshot, dict) or not isinstance(snapshot.get("state"), dict):
        return "—"
    return format_state(snapshot["state"])


def _state_change_reason(event: JSONDict) -> str:
    data = event.get("data")
    if not isinstance(data, dict):
        return "—"
    if data.get("reason") is not None:
        return str(data["reason"])
    if event.get("type") == "fortune_decided":
        return f"Fortune spend {data.get('spend', '—')}"
    if event.get("type") == "session_finished":
        return str(data.get("outcome", "—"))
    return "—"


def _state_change_action(event: JSONDict) -> str:
    data = event.get("data")
    if isinstance(data, dict) and data.get("action") is not None:
        return f"{event.get('type')} ({data['action']})"
    return str(event.get("type", "—"))


def _parse_report_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _format_interval(start: Any, end: Any) -> str:
    start_time = _parse_report_timestamp(start)
    end_time = _parse_report_timestamp(end)
    if start_time is None or end_time is None:
        return "Unavailable: unparseable timestamp"
    return f"{(end_time - start_time).total_seconds():.3f} seconds"


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def render_report(document: JSONDict, events: Sequence[JSONDict]) -> str:
    """Render a deterministic report using only stored session metadata and events."""
    event_list = list(events)
    reader_files = document.get("reader_files", {})
    if not isinstance(reader_files, dict):
        reader_files = {}

    lines = ["# Live Playtest Report", "", "## Session"]
    session_rows: list[tuple[str, Any]] = [
        ("ID", document.get("session_id")),
        ("Purpose", document.get("purpose")),
        ("Hypothesis", document.get("hypothesis") or "None recorded."),
        ("Dice mode", document.get("dice_mode")),
        ("Observer mode", document.get("observer_mode")),
        ("Created", document.get("created_at")),
    ]
    for label in ("story", "rules", "sheet"):
        record = reader_files.get(label, {})
        if isinstance(record, dict):
            session_rows.append((f"{label.title()} reader path", record.get("path")))
            session_rows.append((f"{label.title()} reader SHA-256", record.get("sha256")))
    lines.extend(_report_table(("Field", "Stored value"), session_rows))

    lines.extend(["", "## Route"])
    route_rows: list[tuple[Any, ...]] = []
    for event in event_list:
        event_type = event.get("type")
        data = event.get("data", {})
        if event_type == "passage_shown":
            route_rows.append((event.get("number"), event.get("timestamp"), "shown", event.get("passage"), "—"))
        elif event_type == "passage_transition" and isinstance(data, dict):
            route_rows.append((event.get("number"), event.get("timestamp"), "transition", data.get("from"), data.get("to")))
    lines.extend(_report_table(("Event", "Timestamp", "Action", "From", "To"), route_rows))

    lines.extend(["", "## Player narration"])
    player_rows = [
        (event.get("number"), event.get("timestamp"), event.get("data", {}).get("text"))
        for event in event_list
        if event.get("type") == "player_note" and isinstance(event.get("data"), dict)
    ]
    lines.extend(_report_table(("Event", "Timestamp", "Received text"), player_rows))

    lines.extend(["", "## Operator observations"])
    operator_rows = [
        (event.get("number"), event.get("timestamp"), event.get("data", {}).get("text"))
        for event in event_list
        if event.get("type") == "operator_note" and isinstance(event.get("data"), dict)
    ]
    lines.extend(_report_table(("Event", "Timestamp", "Observed text"), operator_rows))

    lines.extend(["", "## Choices and tests"])
    choices: dict[Any, JSONDict] = {}
    rolls: dict[Any, JSONDict] = {}
    for event in event_list:
        data = event.get("data", {})
        if not isinstance(data, dict):
            continue
        if event.get("type") == "choice_committed":
            choices[event.get("number")] = event
        elif event.get("type") == "roll_recorded" and isinstance(data.get("roll"), dict):
            rolls[data["roll"].get("choice_event")] = data["roll"]
        elif event.get("type") == "fortune_decided" and isinstance(data.get("roll"), dict):
            rolls[data["roll"].get("choice_event")] = data["roll"]
    choice_rows: list[tuple[Any, ...]] = []
    for number, event in choices.items():
        data = event["data"]
        roll = rolls.get(number, {})
        choice_rows.append(
            (
                number,
                data.get("text"),
                data.get("method"),
                data.get("destination"),
                roll.get("attribute"),
                roll.get("mode"),
                roll.get("dice"),
                roll.get("selected_index"),
                roll.get("selected_die"),
                roll.get("target"),
                roll.get("provisional_margin"),
                roll.get("natural"),
                roll.get("margin_is_resolution_inert"),
                roll.get("fortune_status"),
                roll.get("fortune_spent"),
                roll.get("final_die"),
                roll.get("final_margin"),
                roll.get("success"),
            )
        )
    lines.extend(
        _report_table(
            (
                "Choice event",
                "Choice text",
                "Method",
                "Destination",
                "Attribute",
                "Mode",
                "Dice",
                "Selected index",
                "Selected face",
                "Target",
                "Provisional margin",
                "Natural",
                "Margin resolution-inert",
                "Fortune decision",
                "Fortune spent",
                "Final die",
                "Final margin",
                "Success",
            ),
            choice_rows,
        )
    )

    lines.extend(["", "## State history"])
    state_rows: list[tuple[Any, ...]] = []
    for event in event_list:
        before = event.get("before")
        after = event.get("after")
        before_state = before.get("state") if isinstance(before, dict) else None
        after_state = after.get("state") if isinstance(after, dict) else None
        if before_state != after_state:
            state_rows.append(
                (
                    event.get("number"),
                    event.get("timestamp"),
                    _state_change_action(event),
                    _state_change_reason(event),
                    _report_state(before),
                    _report_state(after),
                )
            )
    lines.extend(_report_table(("Event", "Timestamp", "Activity", "Reason", "Before", "After"), state_rows))

    lines.extend(["", "## Rules activity"])
    rules_rows: list[tuple[Any, ...]] = []
    for event in event_list:
        data = event.get("data", {})
        if not isinstance(data, dict):
            continue
        if event.get("type") == "rules_question":
            rules_rows.append((event.get("number"), event.get("timestamp"), "question", data.get("text"), "—"))
        elif event.get("type") == "rules_lookup":
            rules_rows.append((event.get("number"), event.get("timestamp"), "lookup", data.get("section"), data.get("sha256")))
    lines.extend(_report_table(("Event", "Timestamp", "Activity", "Detail", "Stored SHA-256"), rules_rows))

    lines.extend(["", "## Corrections and pauses"])
    correction_rows: list[tuple[Any, ...]] = []
    for event in event_list:
        data = event.get("data", {})
        if not isinstance(data, dict):
            continue
        if event.get("type") == "correction":
            correction_rows.append((event.get("number"), event.get("timestamp"), "correction", data.get("target_event"), data.get("reason"), data.get("compensation")))
        elif event.get("type") == "session_paused":
            correction_rows.append((event.get("number"), event.get("timestamp"), "pause", "—", data.get("reason"), "—"))
        elif event.get("type") == "session_resumed":
            correction_rows.append((event.get("number"), event.get("timestamp"), "resume", "—", "—", "—"))
    lines.extend(_report_table(("Event", "Timestamp", "Activity", "Target", "Reason", "Compensation"), correction_rows))

    lines.extend(["", "## Timing"])
    timing_rows = [
        (event.get("number"), event.get("timestamp"), event.get("type"))
        for event in event_list
    ]
    lines.extend(_report_table(("Event", "Recorded timestamp", "Event type"), timing_rows))
    intervals: list[tuple[Any, ...]] = []
    for index, event in enumerate(event_list):
        if event.get("type") != "passage_shown":
            continue
        choice = next((candidate for candidate in event_list[index + 1:] if candidate.get("type") == "choice_committed"), None)
        if choice is not None:
            intervals.append((event.get("number"), choice.get("number"), _format_interval(event.get("timestamp"), choice.get("timestamp"))))
    lines.append("")
    lines.extend(_report_table(("Passage shown", "Next choice", "Interaction interval"), intervals))

    lines.extend(["", "## Final state"])
    final_state = event_list[-1].get("after", {}).get("state") if event_list else None
    if isinstance(final_state, dict):
        lines.extend(["```text", format_state(final_state), "```"])
    else:
        lines.append("None recorded.")
    finished = next((event for event in reversed(event_list) if event.get("type") == "session_finished"), None)
    if isinstance(finished, dict) and isinstance(finished.get("data"), dict):
        lines.append(f"Outcome: {finished['data'].get('outcome', '—')}")
    else:
        lines.append("Session unfinished")

    lines.extend(
        [
            "",
            "## Limitations",
            "- raw audio was not retained.",
            "- Voice-derived text is stored as received.",
            "- Codex was not blind to unread material.",
            "- This was not a blind or controlled experiment.",
            "- Timing includes network, tool, and transcription delay.",
            "- One player cannot establish general behaviour.",
            "",
        ]
    )
    return "\n".join(lines).replace("\r\n", "\n").replace("\r", "\n")


def write_report(loaded: LoadedSession) -> Path:
    """Atomically replace this session's derived report without recording activity."""
    _verify_identity_metadata(loaded.document, loaded.events, loaded.directory.name)
    path = loaded.directory / "report.md"
    _atomic_write_text(path, render_report(loaded.document, loaded.events))
    return path


def recover_cache(
    sessions_dir: Path,
    session_id: str,
    clock: Clock = utc_now,
) -> LoadedSession:
    loaded = load_session(sessions_dir, session_id, verify_cache=False)
    document = copy.deepcopy(loaded.document)
    document["session_id"] = session_id
    document["created_at"] = loaded.events[0]["timestamp"]
    document["current_state"] = copy.deepcopy(loaded.state)
    document["workflow"] = copy.deepcopy(loaded.workflow)
    document["last_event"] = len(loaded.events)
    document["updated_at"] = clock()
    _atomic_write_json(loaded.directory / "session.json", document)
    loaded.document = document
    return loaded


class _HarnessArgumentParser(argparse.ArgumentParser):
    """Convert command-line input errors into the harness's public error type."""

    def error(self, message: str) -> None:
        raise HarnessError(message)


def _command_parser(
    commands: argparse._SubParsersAction[argparse.ArgumentParser],
    name: str,
) -> argparse.ArgumentParser:
    parser = commands.add_parser(name)
    parser.add_argument("session_id")
    return parser


def build_parser() -> argparse.ArgumentParser:
    """Build the locked, explicit operator command surface."""
    parser = _HarnessArgumentParser()
    parser.add_argument(
        "--sessions-dir",
        type=Path,
        default=Path(".playtest/sessions"),
    )
    commands = parser.add_subparsers(dest="command", required=True)

    start = commands.add_parser("start")
    start.add_argument("session_id")
    start.add_argument("--story", type=Path, required=True)
    start.add_argument("--rules", type=Path, required=True)
    start.add_argument("--sheet", type=Path, required=True)
    start.add_argument("--purpose", required=True)
    start.add_argument("--hypothesis")
    start.add_argument("--start-passage", default="S01")
    start.add_argument("--attribute", action="append", required=True)
    start.add_argument("--resource", action="append", required=True)
    start.add_argument("--pressure", required=True)
    start.add_argument("--possession", action="append", default=[])
    start.add_argument("--mark", action="append", default=[])

    _command_parser(commands, "show")
    _command_parser(commands, "state")

    note = _command_parser(commands, "note")
    note.add_argument("--kind", choices=("player", "operator", "rules-question"), required=True)
    note.add_argument("--text", required=True)

    lookup = _command_parser(commands, "lookup")
    lookup.add_argument("--section", required=True)

    choose = _command_parser(commands, "choose")
    choose.add_argument("--text", required=True)
    choose.add_argument("--method")
    choose.add_argument("--destination")

    roll = _command_parser(commands, "roll")
    roll.add_argument("--attribute", required=True)
    roll.add_argument("--mode", choices=("standard", "advantage", "disadvantage"), required=True)
    roll.add_argument("--die", type=int, action="append", required=True)

    fortune = _command_parser(commands, "fortune")
    fortune.add_argument("--spend", type=int, required=True)

    apply = commands.add_parser("apply")
    apply_commands = apply.add_subparsers(dest="apply_command", required=True)
    resource = _command_parser(apply_commands, "resource")
    resource.add_argument("name")
    resource.add_argument("--delta", type=int, required=True)
    resource.add_argument("--reason", required=True)
    pressure = _command_parser(apply_commands, "pressure")
    pressure.add_argument("--delta", type=int, required=True)
    pressure.add_argument("--reason", required=True)
    for collection in ("possession", "mark"):
        collection_parser = _command_parser(apply_commands, collection)
        collection_parser.add_argument("action", choices=("add", "consume", "remove"))
        collection_parser.add_argument("name")
        collection_parser.add_argument("--reason", required=True)
        collection_parser.add_argument("--allow-duplicate", action="store_true")

    goto = _command_parser(commands, "goto")
    goto.add_argument("destination")

    correct = _command_parser(commands, "correct")
    correct.add_argument("--target-event", type=int, required=True)
    correct.add_argument("--reason", required=True)
    correction = correct.add_mutually_exclusive_group(required=True)
    correction.add_argument("--annotate")
    correction.add_argument("--set-resource")
    correction.add_argument("--set-pressure", type=int)
    correction.add_argument("--add-possession")
    correction.add_argument("--remove-possession")
    correction.add_argument("--add-mark")
    correction.add_argument("--remove-mark")
    correction.add_argument("--set-passage")
    correction.add_argument("--clear-workflow", action="store_true")

    _command_parser(commands, "recover-cache")
    pause = _command_parser(commands, "pause")
    pause.add_argument("--reason", required=True)
    _command_parser(commands, "resume")
    finish = _command_parser(commands, "finish")
    finish.add_argument("--outcome", required=True)
    _command_parser(commands, "report")
    return parser


def _named_values(
    raw_values: Sequence[str],
    parser: Callable[[str], tuple[Any, ...]],
    label: str,
) -> dict[str, Any]:
    values: dict[str, Any] = {}
    names: set[str] = set()
    for raw_value in raw_values:
        parsed = parser(raw_value)
        name = parsed[0]
        value: Any = parsed[1] if len(parsed) == 2 else parsed[1:]
        normalized = name.strip().casefold()
        if normalized in names:
            raise HarnessError(f"duplicate {label} name {name.strip()!r}")
        names.add(normalized)
        values[name] = value
    return values


def _print_event(loaded: LoadedSession, event: JSONDict) -> None:
    print(
        json.dumps(
            {"event": event, "state": loaded.state},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )


def _correction_from_arguments(arguments: argparse.Namespace) -> tuple[str, JSONDict]:
    if arguments.annotate is not None:
        return "annotate", {"replacement_text": arguments.annotate}
    if arguments.set_resource is not None:
        name, value = parse_named_integer(arguments.set_resource)
        return "set-resource", {"name": name, "value": value}
    if arguments.set_pressure is not None:
        return "set-pressure", {"value": arguments.set_pressure}
    if arguments.add_possession is not None:
        return "add-possession", {"name": arguments.add_possession}
    if arguments.remove_possession is not None:
        return "remove-possession", {"name": arguments.remove_possession}
    if arguments.add_mark is not None:
        return "add-mark", {"name": arguments.add_mark}
    if arguments.remove_mark is not None:
        return "remove-mark", {"name": arguments.remove_mark}
    if arguments.set_passage is not None:
        return "set-passage", {"value": arguments.set_passage}
    if arguments.clear_workflow:
        return "clear-workflow", {}
    raise HarnessError("a correction operation is required")


def main(argv: Sequence[str] | None = None) -> int:
    """Run one explicit operator command, preserving programming failures visibly."""
    try:
        arguments = build_parser().parse_args(argv)
        sessions_dir: Path = arguments.sessions_dir
        if arguments.command == "start":
            attributes = _named_values(arguments.attribute, parse_named_integer, "attribute")
            resources = _named_values(arguments.resource, parse_named_bound, "resource")
            state = build_initial_state(
                attributes=attributes,
                resources=resources,
                pressure=parse_named_bound(arguments.pressure),
                possessions=arguments.possession,
                story_marks=arguments.mark,
                start_passage=arguments.start_passage,
            )
            loaded = start_session(
                sessions_dir,
                arguments.session_id,
                arguments.story,
                arguments.rules,
                arguments.sheet,
                arguments.purpose,
                arguments.hypothesis,
                state,
            )
            _print_event(loaded, loaded.events[-1])
            return 0

        if arguments.command == "recover-cache":
            loaded = recover_cache(sessions_dir, arguments.session_id)
            print(json.dumps(loaded.state, ensure_ascii=False, indent=2, sort_keys=True))
            return 0

        loaded = load_session(sessions_dir, arguments.session_id)
        if arguments.command == "show":
            print(show_current_passage(loaded), end="")
        elif arguments.command == "state":
            print(format_state(loaded.state))
        elif arguments.command == "note":
            _print_event(loaded, record_note(loaded, arguments.kind, arguments.text))
        elif arguments.command == "lookup":
            print(record_rules_lookup(loaded, arguments.section), end="")
        elif arguments.command == "choose":
            _print_event(
                loaded,
                record_choice(
                    loaded,
                    arguments.text,
                    arguments.method,
                    arguments.destination,
                ),
            )
        elif arguments.command == "roll":
            _print_event(
                loaded,
                record_roll(loaded, arguments.attribute, arguments.mode, arguments.die),
            )
        elif arguments.command == "fortune":
            _print_event(loaded, record_fortune(loaded, arguments.spend))
        elif arguments.command == "apply":
            if arguments.apply_command == "resource":
                event = change_resource(loaded, arguments.name, arguments.delta, arguments.reason)
            elif arguments.apply_command == "pressure":
                event = change_pressure(loaded, arguments.delta, arguments.reason)
            else:
                collection = "possessions" if arguments.apply_command == "possession" else "story_marks"
                event = change_collection(
                    loaded,
                    collection,
                    arguments.action,
                    arguments.name,
                    arguments.reason,
                    allow_duplicate=arguments.allow_duplicate,
                )
            _print_event(loaded, event)
        elif arguments.command == "goto":
            _print_event(loaded, goto_passage(loaded, arguments.destination))
        elif arguments.command == "correct":
            operation, values = _correction_from_arguments(arguments)
            _print_event(
                loaded,
                correct_session(
                    loaded,
                    arguments.target_event,
                    arguments.reason,
                    operation,
                    **values,
                ),
            )
        elif arguments.command == "pause":
            _print_event(loaded, pause_session(loaded, arguments.reason))
        elif arguments.command == "resume":
            _print_event(loaded, resume_session(loaded))
        elif arguments.command == "finish":
            _print_event(loaded, finish_session(loaded, arguments.outcome))
        elif arguments.command == "report":
            print(write_report(loaded))
        else:
            raise HarnessError(f"unknown command {arguments.command!r}")
        return 0
    except HarnessError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
