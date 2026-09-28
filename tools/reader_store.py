"""Local, atomic session storage for the browser reader (separate from calibrations)."""
from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import os
import re
import tempfile
import threading
import uuid
from contextlib import contextmanager
from html.parser import HTMLParser
from pathlib import Path

import mistune

from tools import reader_engine as engine
from tools.live_playtest import index_passages, utc_now

ROOT = Path(__file__).resolve().parents[1]
TOWER = ROOT / "stories/public_domain/howard/tower_of_the_elephant/playtest"
markdown = mistune.create_markdown(escape=True, plugins=["table"])


class StoreError(ValueError):
    pass


class Conflict(StoreError):
    pass


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)

    def handle_starttag(self, tag, attrs):
        if tag in {"p", "li", "br", "h1", "h2", "h3", "blockquote"}:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in {"p", "li", "h1", "h2", "h3", "blockquote"}:
            self.parts.append("\n")


def plain_text(html):
    parser = PlainText()
    parser.feed(html)
    return " ".join("".join(parser.parts).split())


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def engine_fingerprint():
    return fingerprint({
        "engine": (ROOT / "tools/reader_engine.py").read_text(),
        "dice": (ROOT / "tools/live_playtest.py").read_text(),
    })


def source_snapshot():
    passages = index_passages(TOWER / "slice-01.md")
    engine.validate_content(passages)
    return {
        "passages": passages,
        "rules": (TOWER / "quick-rules.md").read_text(),
        "sheet": (TOWER / "adventure-sheet.md").read_text(),
    }


def passage_title(snapshot, identifier):
    if identifier == "rules":
        return "Player’s Rules"
    return snapshot["passages"][identifier].splitlines()[0].partition(" — ")[2]


def passage_html(snapshot, identifier):
    if identifier == "rules":
        return markdown(snapshot["rules"])
    # The title is displayed by the interface. All remaining authored text stays intact.
    return markdown(snapshot["passages"][identifier].partition("\n")[2])


def printed_result(snapshot, passage, result):
    """Return the authored result paragraph that applies, as HTML, or '' if none is found."""
    anchor = engine.METHOD_ANCHORS.get((result or {}).get("method"))
    label = engine.RESULT_LABELS.get((result or {}).get("outcome"))
    if not anchor or not label or passage not in snapshot["passages"]:
        return ""
    for block in re.split(r"\n(?=- )", snapshot["passages"][passage]):
        if block.startswith(anchor):
            for paragraph in re.split(r"\n\s*\n", block):
                paragraph = " ".join(line.strip() for line in paragraph.splitlines())
                if paragraph.startswith(f"*{label}:*"):
                    return markdown(paragraph)
    return ""


def place_label(snapshot, identifier):
    return "Player’s Rules" if identifier == "rules" else f"{identifier} — {passage_title(snapshot, identifier)}"


class ReaderStore:
    def __init__(self, directory: Path):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.thread_lock = threading.RLock()

    @contextmanager
    def locked(self):
        with self.thread_lock, (self.directory / ".lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(lock, fcntl.LOCK_UN)

    def _path(self, identifier):
        if not isinstance(identifier, str) or not re.fullmatch(r"[0-9a-f]{32}", identifier):
            raise StoreError("Invalid playthrough identifier.")
        return self.directory / f"{identifier}.json"

    def _load(self, identifier):
        try:
            document = json.loads(self._path(identifier).read_text())
        except FileNotFoundError as error:
            raise StoreError("That playthrough was not found.") from error
        except (OSError, ValueError) as error:
            raise StoreError("The saved playthrough could not be read. Its file has been preserved.") from error
        if document.get("id") != identifier or document.get("format") != 1:
            raise StoreError("Unrecognised playthrough format; the file has been preserved.")
        if fingerprint(document["snapshot"]) != document["source_revision"]:
            raise StoreError("The saved reader text has changed. The playthrough has been preserved.")
        return document

    def _save(self, document):
        descriptor, name = tempfile.mkstemp(prefix=".save-", dir=self.directory)
        try:
            with os.fdopen(descriptor, "w") as stream:
                json.dump(document, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, self._path(document["id"]))
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def _view(self, document, viewing=None):
        state = document["state"]
        viewing = viewing or state["passage"]
        if viewing != "rules" and viewing not in state["history"]:
            raise StoreError("Only passages already reached can be reviewed.")
        current_engine = document["engine_revision"] == engine_fingerprint()
        read_only = not current_engine or viewing != state["passage"]
        return {
            "id": document["id"], "label": document["label"],
            "version": document["version"], "updated_at": document["updated_at"],
            "source_revision": document["source_revision"],
            "state": copy.deepcopy(state), "viewing": viewing,
            "read_only": read_only,
            "read_only_reason": "The play rules have changed since this session began. You can review it and add notes; begin a new playthrough to play the revised rules." if not current_engine else "",
            "passage": {"id": viewing, "title": passage_title(document["snapshot"], viewing), "html": passage_html(document["snapshot"], viewing)},
            "rules_html": markdown(document["snapshot"]["rules"]),
            "sheet_html": markdown(document["snapshot"]["sheet"]),
            "choices": engine.choices(state) if not read_only else [],
            "result_html": printed_result(document["snapshot"], state["passage"], state.get("result")),
            "notes": copy.deepcopy(document["notes"]),
            "history": [{"id": item, "title": passage_title(document["snapshot"], item)} for item in dict.fromkeys(state["history"])],
            "last_event": copy.deepcopy(document["events"][-1]) if document["events"] else None,
        }

    def bootstrap(self):
        with self.locked():
            sessions = []
            for path in self.directory.glob("*.json"):
                try:
                    document = self._load(path.stem)
                except StoreError as error:
                    # One damaged file must not hide every other reading.
                    sessions.append({"id": path.stem, "label": path.name, "updated_at": "",
                                     "error": str(error)})
                    continue
                sessions.append({
                    "id": document["id"], "label": document["label"],
                    "updated_at": document["updated_at"], "passage": document["state"]["passage"],
                    "phase": document["state"]["phase"], "note_count": len(document["notes"]),
                })
            # Show current rules even if the mapping needs an authoring update.
            return {
                "story_title": "The Tower of the Elephant",
                "sessions": sorted(sessions, key=lambda item: item["updated_at"], reverse=True),
                "rules_html": markdown((TOWER / "quick-rules.md").read_text()),
                "sheet_html": markdown((TOWER / "adventure-sheet.md").read_text()),
            }

    def create(self, label=""):
        if not isinstance(label, str) or len(label) > 120:
            raise StoreError("Use a playthrough name of at most 120 characters.")
        with self.locked():
            snapshot = source_snapshot()
            now = utc_now()
            document = {
                "format": 1, "id": uuid.uuid4().hex,
                "label": label.strip() or f"Reading {now[:16].replace('T', ' ')} UTC",
                "created_at": now, "updated_at": now, "version": 1,
                "snapshot": snapshot, "source_revision": fingerprint(snapshot),
                "engine_revision": engine_fingerprint(),
                "state": engine.initial_state(), "events": [], "notes": [],
            }
            self._save(document)
            return self._view(document)

    def read(self, identifier, viewing=None):
        with self.locked():
            return self._view(self._load(identifier), viewing)

    def _version(self, document, version):
        if type(version) is not int or version != document["version"]:
            raise Conflict("This playthrough changed in another tab. Reload the current passage before trying again; your action was not applied.")

    def action(self, identifier, action, payload, version):
        if not isinstance(action, str) or not isinstance(payload, dict):
            raise StoreError("Invalid play action.")
        with self.locked():
            document = self._load(identifier)
            self._version(document, version)
            if document["engine_revision"] != engine_fingerprint():
                raise Conflict("The play rules changed. This session remains available to review; begin a new playthrough for the revised rules.")
            before = copy.deepcopy(document["state"])
            state, detail = engine.act(before, action, payload)
            now = utc_now()
            document["state"] = state
            document["version"] += 1
            document["updated_at"] = now
            document["events"].append({
                "id": document["version"], "at": now, "action": action,
                "input": copy.deepcopy(payload), "detail": detail,
                "before": before, "after": copy.deepcopy(state),
            })
            self._save(document)
            return self._view(document)

    def note(self, identifier, text, quote, passage, version):
        if not isinstance(text, str) or not text.strip() or len(text) > 10000:
            raise StoreError("Write a note of 1–10,000 characters.")
        if not isinstance(quote, str) or len(quote) > 10000:
            raise StoreError("The selected quotation is too long.")
        with self.locked():
            document = self._load(identifier)
            self._version(document, version)
            if passage != "rules" and passage not in document["state"]["history"]:
                raise StoreError("Notes must refer to the rules or a passage you have reached.")
            quote = " ".join(quote.split())
            if quote and quote not in plain_text(passage_html(document["snapshot"], passage)):
                raise StoreError("That quotation does not belong to this passage. Select it again, or save a passage-level note.")
            now = utc_now()
            document["notes"].append({
                "id": uuid.uuid4().hex, "created_at": now, "passage": passage,
                "text": text.strip(), "quote": quote,
                "source_revision": document["source_revision"],
                "state": copy.deepcopy(document["state"]),
                "event_id": document["version"],
            })
            document["updated_at"] = now
            document["version"] += 1
            self._save(document)
            return self._view(document, passage)

    def report(self, identifier):
        """Human-first account: notes, then the route. The session JSON keeps the full record."""
        with self.locked():
            document = self._load(identifier)
        snapshot, state, notes = document["snapshot"], document["state"], document["notes"]
        status = "ended" if state["phase"] == "ended" else "in progress"
        lines = [
            f"# {document['label']}", "",
            f"*The Tower of the Elephant*, browser playtest. Started {document['created_at'][:16].replace('T', ' ')} UTC; "
            f"last saved {document['updated_at'][:16].replace('T', ' ')} UTC.", "",
            f"**{status.capitalize()} at {place_label(snapshot, state['passage'])}.** "
            f"Fortune {state['fortune']}/10 · Stamina {state['stamina']}/6 · Exposure {state['exposure']}/5 · "
            f"Possessions: {', '.join(state['possessions']) or 'none'} · Story marks: {', '.join(state['marks']) or 'none'}.", "",
            "## Journey", "", " → ".join(state["history"]), "",
            f"## Reader notes ({len(notes)})", "",
        ]
        for place in ["rules", *dict.fromkeys(state["history"])]:
            here = [note for note in notes if note["passage"] == place]
            if not here:
                continue
            lines.extend([f"### {place_label(snapshot, place)}", ""])
            for note in here:
                if note["quote"]:
                    lines.extend([f"> {note['quote']}", ""])
                at = note["state"]
                lines.extend([note["text"], "",
                              f"*{note['created_at'][:16].replace('T', ' ')} UTC, while at {at['passage']}: "
                              f"Fortune {at['fortune']}, Stamina {at['stamina']}, Exposure {at['exposure']}.*", ""])
        if not notes:
            lines.extend(["No notes recorded.", ""])
        lines.extend(["## Route", "", "| Step | At | What happened | Sheet changes | Fortune · Stamina · Exposure after |",
                      "| ---: | --- | --- | --- | --- |"])
        for number, event in enumerate(document["events"], start=1):
            after = event["after"]
            changes = "; ".join(event["detail"].get("changes", [])) or "—"
            lines.append(f"| {number} | {event['before']['passage']} | {_describe(event)} | {changes} | "
                         f"{after['fortune']} · {after['stamina']} · {after['exposure']} |")
        lines.extend(["", "## Provenance", "",
                      f"Text revision `{document['source_revision']}`; rules engine revision `{document['engine_revision']}`. "
                      "The session file holds every event with its full before-and-after state."])
        return "\n".join(lines).rstrip() + "\n"


def _describe(event):
    detail, before, after = event["detail"], event["before"], event["after"]
    moved = f" → {after['passage']}" if after["passage"] != before["passage"] else ""
    if event["action"] == "choose":
        return f"{detail.get('label', event['input'].get('choice_id'))}{moved}"
    roll = detail.get("roll", {})
    if event["action"] == "roll":
        mode = "" if roll["mode"] == "standard" else f" with {roll['mode'].capitalize()}"
        natural = f", natural {roll['natural']}" if roll["natural"] else ""
        return (f"Rolled {', '.join(map(str, roll['dice']))}{mode} against {roll['attribute']} {roll['target']}: "
                f"kept {roll['selected_die']}{natural}")
    if event["action"] == "fortune":
        return (f"Spent {roll['fortune_spent']} Fortune: final die {roll['final_die']}, "
                f"{'success' if roll['success'] else 'failure'}")
    return f"Continued{moved}"
