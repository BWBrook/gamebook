"""Explicit mechanics for the current Tower outer-wall slice.

The authored Markdown remains the reading source. This small deterministic
adapter neither interprets prose nor rolls dice, and writes no story prose of
its own: METHOD_ANCHORS point at the authored method whose printed result the
reader displays. Changed text requires review of the mapping and its content
fingerprint before a new session can start.
"""
from __future__ import annotations

import copy
import hashlib
import json
from typing import Any

from tools.live_playtest import apply_fortune, resolve_roll

CONTENT_SHA256 = "c65e1f7289278edbdce55b6e211f58a646bb91cfe678d0c00490ffb54dc353d0"
WARNED = "Warned by the silence"
READ = "Read the strangling"
SPEAR = "Guard's spear"
ENDINGS = {"S14", "E01", "E02", "E03"}
PASSAGES = {f"S{number:02}" for number in range(1, 15)} | ENDINGS
METHOD_ANCHORS = {
    "stalk": "- Stalk him.",
    "spear": "- **Brace the guard's spear.**",
    "sword": "- **Meet the leap with your sword.**",
    "evade": "- **Slip aside and cut as it passes.**",
}
RESULT_LABELS = {"success": "Success", "failure": "Failure",
                 "natural 1": "Natural 1", "natural 20": "Natural 20"}


class ReaderError(ValueError):
    """An action cannot be performed in the current reader state."""


def validate_content(passages: dict[str, str]) -> None:
    encoded = json.dumps(passages, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":")).encode("utf-8")
    if hashlib.sha256(encoded).hexdigest() != CONTENT_SHA256:
        raise ReaderError("The adventure text has changed. Review the reader mechanics before starting a new session.")


def initial_state() -> dict[str, Any]:
    return {"passage": "S01", "previous": None, "fortune": 10, "stamina": 6,
            "exposure": 0, "possessions": ["Sword"], "marks": [],
            "phase": "choice", "pending": None, "result": None, "history": ["S01"]}


def _choice(identifier: str, label: str, *, enabled: bool = True,
            reason: str = "", roll: dict | None = None, hint: str = "") -> dict:
    return {"id": identifier, "label": label, "enabled": enabled,
            "reason": reason, "roll": roll, "hint": hint}


def _s13_destination(state: dict) -> str:
    return "E03" if state["stamina"] == 0 else "E02" if state["exposure"] >= 5 else "S14"


def _roll(attribute: str, target: int, advantage: bool = False) -> dict:
    return {"attribute": attribute, "target": target,
            "mode": "advantage" if advantage else "standard"}


def choices(state: dict) -> list[dict]:
    """Return only authored actions, with current requirements and dice mode."""
    if state["phase"] != "choice":
        return []
    passage = state["passage"]
    if passage == "S01":
        return [_choice("climb", "Climb now"),
                _choice("wait", "Wait for the guard to pass again", hint="+1 Exposure")]
    if passage == "S02":
        return [_choice("climb", "Leap for the coping")]
    if passage == "S03":
        return [_choice("pursue", "Go after the mover now"), _choice("examine", "Spend a moment on the corpse")]
    if passage == "S04":
        return [_choice("take_spear", "Take the guard’s spear"), _choice("read_body", "Leave the spear and read the body")]
    if passage == "S05":
        if READ in state["marks"]:
            return [_choice("recognise", "Name him softly for what he is: a thief")]
        advantage = WARNED in state["marks"] or state["previous"] == "S03"
        return [_choice("call", "Call low from the edge of the shrubs", hint="+1 Exposure"),
                _choice("stalk", "Stalk him through the leaves", roll=_roll("Cunning", 12, advantage))]
    if passage == "S07":
        return [_choice("accept", "Accept Taurus as an ally"), _choice("leave", "Leave this theft to Taurus")]
    if passage == "S11":
        has_spear = SPEAR in state["possessions"]
        return [_choice("spear", "Brace the guard’s spear", enabled=has_spear,
                        reason="" if has_spear else "Requires the guard’s spear", roll=_roll("Brawn", 13, True)),
                _choice("sword", "Meet the leap with your sword", roll=_roll("Brawn", 13)),
                _choice("evade", "Slip aside and cut as it passes", roll=_roll("Agility", 12))]
    if passage == "S13":
        label = {"E03": "Stamina 0: turn to E03", "E02": "Exposure 5: turn to E02",
                 "S14": "Ready your sword and give Taurus room"}[_s13_destination(state)]
        return [_choice("continue", label)]
    labels = {"S06": "Hear Taurus’s offer", "S08": "Drop down after Taurus",
              "S09": "Hold where Taurus put you", "S10": "Follow him to the tower",
              "S12": "Give Taurus room to finish the cast"}
    if passage in labels:
        return [_choice("continue", labels[passage])]
    return []


def _advance(state: dict, destination: str, changes: list[str]) -> None:
    state["previous"] = state["passage"]
    state["passage"] = destination
    state["history"].append(destination)
    state["phase"] = "ended" if destination in ENDINGS else "choice"
    state["pending"] = None
    state["result"] = None
    if destination == "S02":
        state["marks"].append(WARNED)
        changes.append(f"Story mark gained: {WARNED}")


def _change(state: dict, key: str, delta: int, changes: list[str]) -> None:
    old = state[key]
    maximum = {"fortune": 10, "stamina": 6, "exposure": 5}[key]
    state[key] = min(maximum, max(0, old + delta))
    changes.append(f"{key.title()} {state[key] - old:+d} ({old} → {state[key]})")


def _finish_roll(state: dict, changes: list[str]) -> None:
    pending = state["pending"]
    roll = pending["resolved"]
    natural = roll["natural"]
    outcome = f"natural {natural}" if natural else ("success" if roll["success"] else "failure")
    identifier = pending["choice_id"]
    if identifier == "stalk":
        destination = "S06"
        if natural == 20:
            _change(state, "stamina", -2, changes)
            _change(state, "exposure", 2, changes)
        elif not roll["success"]:
            _change(state, "stamina", -1, changes)
            _change(state, "exposure", 1, changes)
    else:
        if natural == 20:
            destination = "E03"
        elif roll["success"]:
            destination = "S12"
        else:
            evasion = identifier == "evade"
            _change(state, "stamina", -1 if evasion else -2, changes)
            _change(state, "exposure", 2 if evasion else 1, changes)
            destination = "S13"
    if state["stamina"] == 0:
        destination = "E03"
    state["result"] = {"outcome": outcome, "method": identifier,
                       "destination": destination, "changes": list(changes)}
    state["phase"] = "result"


def act(state: dict, action: str, payload: dict) -> tuple[dict, dict]:
    """Apply a legal action to a copy; return state and an auditable event.

    The server owns the state. Clients supply actions and physical dice only.
    Each pending test is committed before dice entry and resolved exactly once.
    """
    if not isinstance(payload, dict):
        raise ReaderError("Action payload must be an object")
    allowed = {"choose": {"choice_id"}, "roll": {"dice"},
               "fortune": {"spend"}, "continue": set()}
    if not isinstance(action, str) or action not in allowed:
        raise ReaderError("Unknown reader action")
    if set(payload) != allowed[action]:
        raise ReaderError("Unexpected or missing action fields")
    required_phase = {"choose": "choice", "roll": "dice", "fortune": "fortune", "continue": "result"}[action]
    if state["phase"] != required_phase:
        raise ReaderError(f"Cannot {action} during {state['phase']}")
    updated = copy.deepcopy(state)
    changes: list[str] = []
    event = {"action": action, "passage": state["passage"], "payload": copy.deepcopy(payload), "changes": changes}
    if action == "choose":
        selected = next((choice for choice in choices(state) if choice["id"] == payload["choice_id"]), None)
        if selected is None or not selected["enabled"]:
            raise ReaderError("That choice is unavailable")
        identifier = selected["id"]
        event["label"] = selected["label"]
        passage = state["passage"]
        if selected["roll"]:
            if identifier == "spear":
                updated["possessions"].remove(SPEAR)
                changes.append(f"Possession consumed: {SPEAR}")
            elif identifier == "stalk" and WARNED in updated["marks"]:
                updated["marks"].remove(WARNED)
                changes.append(f"Story mark consumed: {WARNED}")
            updated["pending"] = {"choice_id": identifier, "label": selected["label"], "roll": selected["roll"]}
            updated["phase"] = "dice"
        else:
            destinations = {("S01", "climb"): "S03", ("S01", "wait"): "S02",
                            ("S02", "climb"): "S03", ("S03", "pursue"): "S05",
                            ("S03", "examine"): "S04", ("S04", "take_spear"): "S05",
                            ("S04", "read_body"): "S05", ("S05", "recognise"): "S06",
                            ("S05", "call"): "S06", ("S06", "continue"): "S07",
                            ("S07", "accept"): "S08", ("S07", "leave"): "E01",
                            ("S08", "continue"): "S09", ("S09", "continue"): "S10",
                            ("S10", "continue"): "S11", ("S12", "continue"): "S14"}
            if identifier in {"wait", "call"}:
                _change(updated, "exposure", 1, changes)
            if identifier == "take_spear":
                updated["possessions"].append(SPEAR)
                changes.append(f"Possession gained: {SPEAR}")
            elif identifier == "read_body":
                updated["marks"].append(READ)
                changes.append(f"Story mark gained: {READ}")
            elif identifier == "recognise":
                updated["marks"].remove(READ)
                changes.append(f"Story mark consumed: {READ}")
            if passage == "S13":
                destination = _s13_destination(updated)
            else:
                destination = destinations[(passage, identifier)]
            _advance(updated, destination, changes)
    elif action == "roll":
        dice = payload["dice"]
        if not isinstance(dice, list):
            raise ReaderError("Enter physical dice as a list of whole numbers")
        try:
            resolved = resolve_roll(**updated["pending"]["roll"], dice=dice)
        except ValueError as error:
            raise ReaderError(str(error)) from error
        updated["pending"]["resolved"] = resolved
        event["roll"] = copy.deepcopy(resolved)
        if resolved["natural"] is not None:
            _finish_roll(updated, changes)
        else:
            updated["phase"] = "fortune"
    elif action == "fortune":
        try:
            resolved = apply_fortune(updated["pending"]["resolved"], payload["spend"], updated["fortune"])
        except ValueError as error:
            raise ReaderError(str(error)) from error
        updated["pending"]["resolved"] = resolved
        event["roll"] = copy.deepcopy(resolved)
        if payload["spend"]:
            _change(updated, "fortune", -payload["spend"], changes)
        _finish_roll(updated, changes)
    else:
        _advance(updated, updated["result"]["destination"], changes)
    event["destination"] = updated["passage"]
    if updated["result"] is not None:
        event["result"] = copy.deepcopy(updated["result"])
    return updated, event
