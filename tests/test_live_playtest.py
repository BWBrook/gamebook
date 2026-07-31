from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from tools import live_playtest as lp


class RollMechanicsTests(unittest.TestCase):
    def test_standard_advantage_and_disadvantage_selection(self) -> None:
        standard = lp.resolve_roll("CUN", 12, "standard", [15])
        advantage = lp.resolve_roll("BRN", 13, "advantage", [6, 20])
        disadvantage = lp.resolve_roll("AGI", 12, "disadvantage", [3, 17])

        self.assertEqual(standard["selected_die"], 15)
        self.assertEqual(standard["provisional_margin"], -3)
        self.assertEqual(advantage["selected_die"], 6)
        self.assertEqual(advantage["selected_index"], 0)
        self.assertIsNone(advantage["natural"])
        self.assertEqual(disadvantage["selected_die"], 17)

    def test_tied_die_selection_keeps_the_first_physical_die(self) -> None:
        result = lp.resolve_roll("BRN", 13, "advantage", [8, 8])

        self.assertEqual(result["selected_die"], 8)
        self.assertEqual(result["selected_index"], 0)

    def test_only_the_selected_die_can_lock(self) -> None:
        result = lp.resolve_roll("BRN", 13, "advantage", [6, 20])
        self.assertIsNone(result["natural"])
        result = lp.resolve_roll("BRN", 13, "disadvantage", [1, 20])
        self.assertEqual(result["natural"], 20)
        self.assertEqual(result["provisional_margin"], -7)
        self.assertTrue(result["margin_is_resolution_inert"])

    def test_selected_natural_one_is_locked(self) -> None:
        result = lp.resolve_roll("BRN", 13, "standard", [1])

        self.assertEqual(result["natural"], 1)
        self.assertEqual(result["final_die"], 1)
        self.assertEqual(result["final_margin"], 12)
        self.assertEqual(result["fortune_status"], "forbidden")
        self.assertTrue(result["success"])

    def test_invalid_face_or_wrong_dice_count_is_rejected(self) -> None:
        for dice in ([0], [21], [2, 3]):
            with self.subTest(dice=dice):
                with self.assertRaises(lp.HarnessError):
                    lp.resolve_roll("CUN", 12, "standard", dice)
        with self.assertRaisesRegex(lp.HarnessError, "requires two dice"):
            lp.resolve_roll("CUN", 12, "advantage", [7])

    def test_fortune_recomputes_without_clamping_final_result(self) -> None:
        roll = lp.resolve_roll("CUN", 12, "standard", [15])
        result = lp.apply_fortune(roll, 3, 10)
        self.assertEqual(result["final_die"], 12)
        self.assertEqual(result["final_margin"], 0)
        self.assertTrue(result["success"])
        self.assertEqual(result["fortune_spent"], 3)

        deepened = lp.apply_fortune(
            lp.resolve_roll("BRN", 13, "standard", [2]),
            3,
            10,
        )
        self.assertEqual(deepened["final_die"], -1)
        self.assertEqual(deepened["final_margin"], 14)

    def test_locked_or_unaffordable_fortune_is_rejected(self) -> None:
        locked = lp.resolve_roll("BRN", 13, "standard", [20])
        with self.assertRaisesRegex(lp.HarnessError, "locked natural"):
            lp.apply_fortune(locked, 1, 10)
        ordinary = lp.resolve_roll("CUN", 12, "standard", [15])
        with self.assertRaisesRegex(lp.HarnessError, "only 2 Fortune"):
            lp.apply_fortune(ordinary, 3, 2)


class HarnessTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)
        self.story = self.root / "slice.md"
        self.rules = self.root / "rules.md"
        self.sheet = self.root / "sheet.md"
        self.story.write_text(
            "# Slice\n\n"
            "Introduction that must not be shown.\n\n"
            "## S01 — First\n\n"
            "Reached text.\n\n"
            "## A reader-facing inset\n\n"
            "Still part of the reached passage.\n\n"
            "Turn to **S02**.\n\n"
            "## S02 — Second\n\n"
            "Unreached secret.\n\n"
            "## E01 — Ending\n\n"
            "Terminal prose.\n",
            encoding="utf-8",
        )
        self.rules.write_text(
            "# Rules\n\n"
            "## Fortune\n\n"
            "Spend after the roll.\n\n"
            "### Timing\n\n"
            "The captured target does not change.\n\n"
            "## Endings\n\n"
            "Stop at a terminal.\n",
            encoding="utf-8",
        )
        self.sheet.write_text("# Sheet\n", encoding="utf-8")

    def fixed_clock(self) -> str:
        return "2026-07-31T10:00:00Z"

    def initial_state(self) -> dict[str, object]:
        return lp.build_initial_state(
            attributes={"BRN": 13, "AGI": 12, "CUN": 12, "WIL": 12},
            resources={"Fortune": (10, 10), "Stamina": (6, 6)},
            pressure=("Exposure", 0, 5),
            possessions=["Sword"],
            story_marks=[],
            start_passage="S01",
        )

    def start(self, session_id: str = "test-session") -> lp.LoadedSession:
        return lp.start_session(
            self.root / "sessions",
            session_id,
            self.story,
            self.rules,
            self.sheet,
            "Natural calibration playthrough",
            None,
            self.initial_state(),
            self.fixed_clock,
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()


class StateMutationTests(HarnessTestCase):
    def test_resource_pressure_possession_and_mark_changes(self) -> None:
        loaded = self.start()
        lp.change_resource(loaded, "Stamina", -1, "Printed injury", self.fixed_clock)
        lp.change_pressure(loaded, 7, "Printed disturbance", self.fixed_clock)
        lp.change_collection(
            loaded,
            "possessions",
            "add",
            "Guard's spear",
            "Taken at S04",
            clock=self.fixed_clock,
        )
        lp.change_collection(
            loaded,
            "story_marks",
            "add",
            "Read the strangling",
            "Discovery at S04",
            clock=self.fixed_clock,
        )

        self.assertEqual(loaded.state["resources"]["Stamina"]["current"], 5)
        self.assertEqual(loaded.state["pressure"]["current"], 5)
        self.assertIn("Guard's spear", loaded.state["possessions"])
        self.assertIn("Read the strangling", loaded.state["story_marks"])
        self.assertEqual(
            loaded.events[-4]["data"],
            {
                "name": "Stamina",
                "delta": -1,
                "before": 6,
                "after": 5,
                "reason": "Printed injury",
            },
        )
        self.assertEqual(loaded.events[-3]["data"]["requested_delta"], 7)
        self.assertEqual(loaded.events[-3]["data"]["applied_delta"], 5)

    def test_resource_recovery_and_bounds_are_enforced_case_insensitively(self) -> None:
        loaded = self.start()
        lp.change_resource(loaded, "stamina", -2, "Loss", self.fixed_clock)
        event = lp.change_resource(loaded, "STAMINA", 2, "Recovery", self.fixed_clock)

        self.assertEqual(event["data"]["name"], "Stamina")
        self.assertEqual(loaded.state["resources"]["Stamina"]["current"], 6)
        for delta, message in ((1, "outside 0/6"), (-7, "outside 0/6")):
            with self.subTest(delta=delta):
                with self.assertRaisesRegex(lp.HarnessError, message):
                    lp.change_resource(loaded, "Stamina", delta, "Invalid", self.fixed_clock)

    def test_pressure_saturates_positive_delta_and_rejects_underflow(self) -> None:
        loaded = self.start()
        event = lp.change_pressure(loaded, 7, "Disturbance", self.fixed_clock)

        self.assertEqual(event["data"]["before"], 0)
        self.assertEqual(event["data"]["after"], 5)
        self.assertEqual(event["data"]["requested_delta"], 7)
        self.assertEqual(event["data"]["applied_delta"], 5)
        with self.assertRaisesRegex(lp.HarnessError, "below 0"):
            lp.change_pressure(loaded, -6, "Invalid", self.fixed_clock)

    def test_collection_actions_distinguish_consuming_removing_and_duplicates(self) -> None:
        loaded = self.start()
        added = lp.change_collection(
            loaded, "possessions", "add", "Guard's spear", "Taken", clock=self.fixed_clock
        )
        with self.assertRaisesRegex(lp.HarnessError, "already present"):
            lp.change_collection(
                loaded, "possessions", "add", "guard's SPEAR", "Duplicate", clock=self.fixed_clock
            )
        duplicate = lp.change_collection(
            loaded,
            "possessions",
            "add",
            "guard's SPEAR",
            "Explicit duplicate",
            allow_duplicate=True,
            clock=self.fixed_clock,
        )
        self.assertEqual(
            loaded.state["possessions"],
            ["Sword", "Guard's spear", "guard's SPEAR"],
        )
        consumed = lp.change_collection(
            loaded, "possessions", "consume", "GUARD'S SPEAR", "Used", clock=self.fixed_clock
        )
        self.assertEqual(loaded.state["possessions"], ["Sword", "guard's SPEAR"])
        removed = lp.change_collection(
            loaded, "possessions", "remove", "guard's spear", "Discarded", clock=self.fixed_clock
        )
        self.assertEqual(loaded.state["possessions"], ["Sword"])

        self.assertEqual(added["data"]["action"], "add")
        self.assertEqual(added["data"]["name"], "Guard's spear")
        self.assertFalse(added["data"]["allow_duplicate"])
        self.assertTrue(duplicate["data"]["allow_duplicate"])
        self.assertEqual(duplicate["data"]["name"], "guard's SPEAR")
        self.assertEqual(consumed["data"]["action"], "consume")
        self.assertEqual(consumed["data"]["name"], "GUARD'S SPEAR")
        self.assertEqual(removed["data"]["action"], "remove")
        self.assertEqual(removed["data"]["name"], "guard's spear")
        with self.assertRaisesRegex(lp.HarnessError, "not present"):
            lp.change_collection(
                loaded, "possessions", "consume", "missing", "Invalid", clock=self.fixed_clock
            )
        with self.assertRaisesRegex(lp.HarnessError, "not present"):
            lp.change_collection(
                loaded, "story_marks", "remove", "missing", "Invalid", clock=self.fixed_clock
            )

    def test_invalid_changes_leave_files_unchanged(self) -> None:
        loaded = self.start()
        before = (
            (loaded.directory / "events.jsonl").read_bytes(),
            (loaded.directory / "session.json").read_bytes(),
        )
        invalid_calls = (
            lambda: lp.change_resource(loaded, "Stamina", -7, "Invalid", self.fixed_clock),
            lambda: lp.change_resource(loaded, "Unknown", 1, "Invalid", self.fixed_clock),
            lambda: lp.change_resource(loaded, "Stamina", -1, " ", self.fixed_clock),
            lambda: lp.change_pressure(loaded, -1, "Invalid", self.fixed_clock),
            lambda: lp.change_pressure(loaded, 1, " ", self.fixed_clock),
            lambda: lp.change_collection(loaded, "inventory", "add", "Thing", "Invalid", clock=self.fixed_clock),
            lambda: lp.change_collection(loaded, "possessions", "drop", "Thing", "Invalid", clock=self.fixed_clock),
            lambda: lp.change_collection(loaded, "possessions", "add", " ", "Invalid", clock=self.fixed_clock),
            lambda: lp.change_collection(loaded, "possessions", "add", "Thing", " ", clock=self.fixed_clock),
        )
        for invalid_call in invalid_calls:
            with self.subTest(invalid_call=invalid_call):
                with self.assertRaises(lp.HarnessError):
                    invalid_call()
                self.assertEqual(
                    (
                        (loaded.directory / "events.jsonl").read_bytes(),
                        (loaded.directory / "session.json").read_bytes(),
                    ),
                    before,
                )


class LifecycleAndCorrectionTests(HarnessTestCase):
    def test_pause_resume_replays_equivalently(self) -> None:
        loaded = self.start()
        lp.pause_session(loaded, "Voice break", self.fixed_clock)
        self.assertEqual(loaded.state["status"], "paused")

        reloaded = lp.load_session(self.root / "sessions", "test-session")
        lp.resume_session(reloaded, self.fixed_clock)

        self.assertEqual(reloaded.state["status"], "active")
        self.assertEqual(lp.replay_events(reloaded.events)["state"], reloaded.state)

    def test_resume_rechecks_reader_hashes_before_recording(self) -> None:
        loaded = self.start()
        lp.pause_session(loaded, "Voice break", self.fixed_clock)
        self.story.write_text("## S01 — Changed\n", encoding="utf-8")
        before = (loaded.directory / "events.jsonl").read_bytes()

        with self.assertRaisesRegex(lp.HarnessError, "reader file changed: story"):
            lp.resume_session(loaded, self.fixed_clock)

        self.assertEqual((loaded.directory / "events.jsonl").read_bytes(), before)

    def test_lifecycle_transition_rules_and_finished_read_only_access(self) -> None:
        loaded = self.start()
        with self.assertRaisesRegex(lp.HarnessError, "cannot resume"):
            lp.resume_session(loaded, self.fixed_clock)
        with self.assertRaisesRegex(lp.HarnessError, "outcome must be non-empty"):
            lp.finish_session(loaded, " ", self.fixed_clock)
        lp.pause_session(loaded, "Break", self.fixed_clock)
        with self.assertRaisesRegex(lp.HarnessError, "cannot pause"):
            lp.pause_session(loaded, "Again", self.fixed_clock)
        with self.assertRaisesRegex(lp.HarnessError, "cannot finish"):
            lp.finish_session(loaded, "Too early", self.fixed_clock)
        lp.resume_session(lp.load_session(self.root / "sessions", "test-session"), self.fixed_clock)
        reloaded = lp.load_session(self.root / "sessions", "test-session")
        lp.finish_session(reloaded, "E01 — theft abandoned", self.fixed_clock)

        self.assertEqual(reloaded.state["status"], "finished")
        self.assertIn("Status: finished", lp.format_state(reloaded.state))
        with self.assertRaisesRegex(lp.HarnessError, "status is finished"):
            lp.record_note(reloaded, "player", "One more thought", self.fixed_clock)

    def test_finished_session_is_immutable_for_all_recording_operations(self) -> None:
        loaded = self.start()
        lp.finish_session(loaded, "E01 — theft abandoned", self.fixed_clock)
        before = (
            (loaded.directory / "events.jsonl").read_bytes(),
            (loaded.directory / "session.json").read_bytes(),
        )
        operations = (
            lambda: lp.change_resource(loaded, "Stamina", -1, "Late", self.fixed_clock),
            lambda: lp.change_pressure(loaded, 1, "Late", self.fixed_clock),
            lambda: lp.change_collection(loaded, "possessions", "add", "Late", "Late", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Late", "annotate", replacement_text="Late", clock=self.fixed_clock),
            lambda: lp.pause_session(loaded, "Late", self.fixed_clock),
            lambda: lp.finish_session(loaded, "Late", self.fixed_clock),
        )
        for operation in operations:
            with self.subTest(operation=operation):
                with self.assertRaisesRegex(lp.HarnessError, "status is finished"):
                    operation()
                self.assertEqual(
                    (
                        (loaded.directory / "events.jsonl").read_bytes(),
                        (loaded.directory / "session.json").read_bytes(),
                    ),
                    before,
                )

    def test_correction_preserves_original_and_compensates_state(self) -> None:
        loaded = self.start()
        original = lp.change_resource(loaded, "Stamina", -1, "Misheard loss", self.fixed_clock)

        lp.correct_session(
            loaded,
            original["number"],
            "Player said no Stamina loss",
            "set-resource",
            name="Stamina",
            value=6,
            clock=self.fixed_clock,
        )

        self.assertEqual(loaded.events[-2]["type"], "resource_changed")
        self.assertEqual(loaded.events[-2]["data"]["after"], 5)
        self.assertEqual(loaded.events[-1]["type"], "correction")
        self.assertEqual(loaded.state["resources"]["Stamina"]["current"], 6)
        self.assertEqual(loaded.events[-1]["data"]["compensation"], "set Stamina to 6")

    def test_each_correction_contract_changes_only_its_authorized_state(self) -> None:
        cases = (
            ("annotate", {"replacement_text": "Correct wording"}, None, None),
            ("set-resource", {"name": "stamina", "value": 4}, ("resources", "Stamina", "current"), 4),
            ("set-pressure", {"value": 3}, ("pressure", "current"), 3),
            ("add-possession", {"name": "Shield"}, ("possessions",), ["Sword", "Shield"]),
            ("remove-possession", {"name": "sword"}, ("possessions",), []),
            ("add-mark", {"name": "Saw smoke"}, ("story_marks",), ["Saw smoke"]),
            ("remove-mark", {"name": "Saw smoke"}, ("story_marks",), []),
            ("set-passage", {"value": "E01"}, ("current_passage",), "E01"),
            ("clear-workflow", {}, None, None),
        )
        for operation, kwargs, state_path, expected_value in cases:
            with self.subTest(operation=operation):
                loaded = self.start(operation.replace("-", "_"))
                if operation == "remove-mark":
                    lp.change_collection(loaded, "story_marks", "add", "Saw smoke", "Setup", clock=self.fixed_clock)
                if operation == "clear-workflow":
                    lp.record_choice(loaded, "Go on", None, "S02", self.fixed_clock)
                before_state = json.loads(json.dumps(loaded.state))
                before_workflow = json.loads(json.dumps(loaded.workflow))
                expected_state = json.loads(json.dumps(before_state))
                expected_workflow = json.loads(json.dumps(before_workflow))
                if state_path == ("resources", "Stamina", "current"):
                    expected_state["resources"]["Stamina"]["current"] = expected_value
                elif state_path == ("pressure", "current"):
                    expected_state["pressure"]["current"] = expected_value
                elif state_path == ("possessions",):
                    expected_state["possessions"] = expected_value
                elif state_path == ("story_marks",):
                    expected_state["story_marks"] = expected_value
                elif state_path == ("current_passage",):
                    expected_state["current_passage"] = expected_value
                elif operation == "clear-workflow":
                    expected_workflow = {"choice": None, "roll": None}
                event = lp.correct_session(
                    loaded, 1, "Compensate operator error", operation, clock=self.fixed_clock, **kwargs
                )
                self.assertEqual(event["type"], "correction")
                self.assertEqual(loaded.state, expected_state)
                self.assertEqual(loaded.workflow, expected_workflow)

    def test_correction_rejects_invalid_target_reason_arguments_and_results_without_mutation(self) -> None:
        loaded = self.start()
        before = (
            (loaded.directory / "events.jsonl").read_bytes(),
            (loaded.directory / "session.json").read_bytes(),
        )
        invalid_calls = (
            lambda: lp.correct_session(loaded, 99, "Reason", "annotate", replacement_text="Text", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, " ", "annotate", replacement_text="Text", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "unknown", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "annotate", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "annotate", replacement_text="Text", name="extra", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "annotate", replacement_text="Text", value=1, clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "set-resource", value=4, clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "set-resource", name="Stamina", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "set-resource", name="Stamina", value=7, clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "set-resource", name="Stamina", value=4, replacement_text="extra", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "set-pressure", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "set-pressure", value=-1, clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "set-pressure", value=3, name="extra", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "set-pressure", value=3, replacement_text="extra", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "add-possession", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "add-possession", name="sword", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "add-possession", name="Shield", value=1, clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "add-possession", name="Shield", replacement_text="extra", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "remove-possession", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "remove-possession", name="missing", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "remove-possession", name="Sword", value=1, clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "remove-possession", name="Sword", replacement_text="extra", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "add-mark", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "add-mark", name=" ", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "add-mark", name="Saw smoke", value=1, clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "add-mark", name="Saw smoke", replacement_text="extra", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "remove-mark", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "remove-mark", name="missing", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "remove-mark", name="Saw smoke", value=1, clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "remove-mark", name="Saw smoke", replacement_text="extra", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "set-passage", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "set-passage", value="S99", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "set-passage", value="S02", name="extra", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "set-passage", value="S02", replacement_text="extra", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "clear-workflow", name="extra", clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "clear-workflow", value=1, clock=self.fixed_clock),
            lambda: lp.correct_session(loaded, 1, "Reason", "clear-workflow", replacement_text="extra", clock=self.fixed_clock),
        )
        for invalid_call in invalid_calls:
            with self.subTest(invalid_call=invalid_call):
                with self.assertRaises(lp.HarnessError):
                    invalid_call()
                self.assertEqual(
                    (
                        (loaded.directory / "events.jsonl").read_bytes(),
                        (loaded.directory / "session.json").read_bytes(),
                    ),
                    before,
                )


class MarkdownIndexTests(HarnessTestCase):
    def test_passage_index_returns_one_bounded_block(self) -> None:
        passages = lp.index_passages(self.story)
        self.assertEqual(list(passages), ["S01", "S02", "E01"])
        self.assertTrue(passages["S01"].startswith("## S01 — First\n"))
        self.assertIn("Reached text.", passages["S01"])
        self.assertIn("Still part of the reached passage.", passages["S01"])
        self.assertNotIn("Introduction", passages["S01"])
        self.assertNotIn("Unreached secret", passages["S01"])

    def test_duplicate_passage_identifier_is_rejected(self) -> None:
        self.story.write_text(
            "## S01 — First\n\nOne.\n\n## S01 — Duplicate\n\nTwo.\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(lp.HarnessError, "duplicate passage S01"):
            lp.index_passages(self.story)

    def test_rules_are_indexed_case_insensitively_without_h3_splitting(self) -> None:
        sections = lp.index_rule_sections(self.rules)
        self.assertEqual(list(sections), ["fortune", "endings"])
        self.assertIn("## Fortune", sections["fortune"])
        self.assertIn("Spend after", sections["fortune"])
        self.assertIn("### Timing", sections["fortune"])

    def test_named_value_parsers(self) -> None:
        self.assertEqual(lp.parse_named_integer("BRN=13"), ("BRN", 13))
        self.assertEqual(
            lp.parse_named_bound("Fortune=10/10"),
            ("Fortune", 10, 10),
        )
        with self.assertRaisesRegex(lp.HarnessError, "NAME=VALUE"):
            lp.parse_named_integer("BRN")
        with self.assertRaisesRegex(lp.HarnessError, "CURRENT/MAXIMUM"):
            lp.parse_named_bound("Fortune=10")


class PersistenceTests(HarnessTestCase):
    def test_start_writes_one_authoritative_event_and_cache(self) -> None:
        loaded = self.start()
        self.assertEqual(loaded.document["format_version"], 1)
        self.assertEqual(loaded.document["dice_mode"], "physical")
        self.assertEqual(loaded.document["observer_mode"], "neutral")
        self.assertEqual(loaded.document["last_event"], 1)
        self.assertEqual(loaded.events[0]["type"], "session_started")
        self.assertIsNone(loaded.events[0]["before"])
        self.assertEqual(
            loaded.events[0]["after"]["state"]["current_passage"],
            "S01",
        )
        self.assertEqual(
            lp.replay_events(loaded.events),
            loaded.events[-1]["after"],
        )

    def test_duplicate_session_identifier_is_rejected(self) -> None:
        self.start()
        with self.assertRaisesRegex(lp.HarnessError, "already exists"):
            self.start()

    def test_missing_start_passage_is_rejected(self) -> None:
        state = self.initial_state()
        state["current_passage"] = "S99"
        with self.assertRaisesRegex(lp.HarnessError, "undefined start passage S99"):
            lp.start_session(
                self.root / "sessions",
                "missing-passage",
                self.story,
                self.rules,
                self.sheet,
                "Missing-passage check",
                None,
                state,
                self.fixed_clock,
            )

    def test_reader_hash_drift_stops_loading(self) -> None:
        self.start()
        self.story.write_text("## S01 — Changed\n\nChanged.\n", encoding="utf-8")
        with self.assertRaisesRegex(lp.HarnessError, "reader file changed"):
            lp.load_session(self.root / "sessions", "test-session")

    def test_cache_cannot_replace_authoritative_start_metadata(self) -> None:
        loaded = self.start()
        document_path = loaded.directory / "session.json"
        original_document = json.loads(document_path.read_text(encoding="utf-8"))
        original_story = self.story.read_text(encoding="utf-8")

        self.story.write_text("## S01 — Changed\n\nChanged.\n", encoding="utf-8")
        tampered_document = json.loads(json.dumps(original_document))
        tampered_document["reader_files"]["story"]["sha256"] = lp.sha256_file(
            self.story
        )
        document_path.write_text(json.dumps(tampered_document), encoding="utf-8")
        with self.assertRaisesRegex(
            lp.HarnessError,
            "authoritative session-start metadata",
        ):
            lp.load_session(self.root / "sessions", "test-session")

        self.story.write_text(original_story, encoding="utf-8")
        tampered_initial_state = json.loads(json.dumps(self.initial_state()))
        tampered_initial_state["attributes"]["BRN"] = 1
        for field, value in (
            ("purpose", "Tampered purpose"),
            ("hypothesis", "Tampered hypothesis"),
            ("dice_mode", "digital"),
            ("observer_mode", "advisory"),
            ("initial_state", tampered_initial_state),
        ):
            with self.subTest(field=field):
                document = json.loads(json.dumps(original_document))
                document[field] = value
                document_path.write_text(json.dumps(document), encoding="utf-8")
                with self.assertRaisesRegex(
                    lp.HarnessError,
                    "authoritative session-start metadata",
                ):
                    lp.load_session(self.root / "sessions", "test-session")

    def test_stale_cache_requires_explicit_recovery(self) -> None:
        loaded = self.start()
        document_path = loaded.directory / "session.json"
        document = json.loads(document_path.read_text(encoding="utf-8"))
        document["last_event"] = 0
        document_path.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(lp.HarnessError, "recover-cache"):
            lp.load_session(self.root / "sessions", "test-session")

        recovered = lp.recover_cache(
            self.root / "sessions",
            "test-session",
            self.fixed_clock,
        )
        self.assertEqual(recovered.document["last_event"], 1)
        self.assertEqual(recovered.state, self.initial_state())

    def test_broken_event_chain_cannot_be_recovered(self) -> None:
        loaded = self.start()
        event_path = loaded.directory / "events.jsonl"
        event = json.loads(event_path.read_text(encoding="utf-8"))
        event["number"] = 2
        event_path.write_text(json.dumps(event) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(lp.HarnessError, "event number"):
            lp.recover_cache(
                self.root / "sessions",
                "test-session",
                self.fixed_clock,
            )


class ObserverOperationTests(HarnessTestCase):
    def test_show_returns_only_current_passage_and_logs_it(self) -> None:
        loaded = self.start()

        shown = lp.show_current_passage(loaded, self.fixed_clock)

        self.assertIn("## S01 — First", shown)
        self.assertIn("Reached text.", shown)
        self.assertNotIn("Unreached secret", shown)
        self.assertEqual(loaded.events[-1]["type"], "passage_shown")

    def test_notes_preserve_received_text_and_kind(self) -> None:
        loaded = self.start()
        text = "I don't trust that silence—yet."

        lp.record_note(loaded, "player", text, self.fixed_clock)

        self.assertEqual(loaded.events[-1]["data"]["text"], text)
        self.assertEqual(loaded.events[-1]["data"]["kind"], "player")

    def test_rules_lookup_is_case_insensitive_and_logged(self) -> None:
        loaded = self.start()

        section = lp.record_rules_lookup(loaded, "FORTUNE", self.fixed_clock)

        self.assertIn("Spend after the roll.", section)
        self.assertEqual(loaded.events[-1]["type"], "rules_lookup")
        self.assertEqual(loaded.events[-1]["data"]["section"], "Fortune")

    def test_format_state_is_complete_and_deterministic(self) -> None:
        loaded = self.start()

        formatted = lp.format_state(loaded.state)

        self.assertEqual(
            formatted,
            "Passage: S01\n"
            "Status: active\n"
            "Attributes: AGI 12 | BRN 13 | CUN 12 | WIL 12\n"
            "Fortune: 10/10\n"
            "Stamina: 6/6\n"
            "Exposure: 0/5\n"
            "Possessions: Sword\n"
            "Story marks: —",
        )

    def test_choice_precedes_valid_referenced_transition(self) -> None:
        loaded = self.start()

        lp.record_choice(
            loaded,
            "Go on",
            None,
            "S02",
            self.fixed_clock,
        )
        lp.goto_passage(loaded, "S02", self.fixed_clock)

        self.assertEqual(loaded.state["current_passage"], "S02")
        self.assertEqual(loaded.workflow, {"choice": None, "roll": None})

    def test_unreferenced_or_undefined_destination_does_not_mutate(self) -> None:
        loaded = self.start()
        lp.record_choice(loaded, "Invent a route", None, "E01", self.fixed_clock)
        before_log = (loaded.directory / "events.jsonl").read_bytes()
        before_cache = (loaded.directory / "session.json").read_bytes()

        with self.assertRaisesRegex(lp.HarnessError, "not referenced"):
            lp.goto_passage(loaded, "E01", self.fixed_clock)
        self.assertEqual(
            (loaded.directory / "events.jsonl").read_bytes(),
            before_log,
        )
        self.assertEqual(
            (loaded.directory / "session.json").read_bytes(),
            before_cache,
        )
        with self.assertRaisesRegex(lp.HarnessError, "undefined passage S99"):
            lp.goto_passage(loaded, "S99", self.fixed_clock)

    def test_invalid_notes_and_rules_lookup_do_not_mutate(self) -> None:
        loaded = self.start()
        before_log = (loaded.directory / "events.jsonl").read_bytes()
        before_cache = (loaded.directory / "session.json").read_bytes()

        with self.assertRaisesRegex(lp.HarnessError, "note text must be non-empty"):
            lp.record_note(loaded, "player", "  \t", self.fixed_clock)
        with self.assertRaisesRegex(lp.HarnessError, "unknown note kind"):
            lp.record_note(loaded, "observer", "A note", self.fixed_clock)
        with self.assertRaisesRegex(lp.HarnessError, "unknown rules heading"):
            lp.record_rules_lookup(loaded, "Combat", self.fixed_clock)

        self.assertEqual((loaded.directory / "events.jsonl").read_bytes(), before_log)
        self.assertEqual((loaded.directory / "session.json").read_bytes(), before_cache)

    def test_second_choice_and_transition_before_choice_are_rejected(self) -> None:
        loaded = self.start()
        with self.assertRaisesRegex(lp.HarnessError, "committed choice"):
            lp.goto_passage(loaded, "S02", self.fixed_clock)

        lp.record_choice(loaded, "Go on", None, "S02", self.fixed_clock)
        with self.assertRaisesRegex(lp.HarnessError, "unresolved choice"):
            lp.record_choice(loaded, "Go on again", None, "S02", self.fixed_clock)

    def test_transition_waits_for_a_pending_ordinary_roll(self) -> None:
        loaded = self.start()
        lp.record_choice(loaded, "Go on", None, "S02", self.fixed_clock)
        loaded.workflow["roll"] = {"fortune_status": "pending"}

        with self.assertRaisesRegex(lp.HarnessError, "Fortune decision"):
            lp.goto_passage(loaded, "S02", self.fixed_clock)

    def test_finished_sessions_reject_observer_operations(self) -> None:
        loaded = self.start()
        loaded.state["status"] = "finished"

        with self.assertRaisesRegex(lp.HarnessError, "cannot show passage"):
            lp.show_current_passage(loaded, self.fixed_clock)
        with self.assertRaisesRegex(lp.HarnessError, "cannot record note"):
            lp.record_note(loaded, "player", "No more", self.fixed_clock)
        with self.assertRaisesRegex(lp.HarnessError, "cannot look up rules"):
            lp.record_rules_lookup(loaded, "Fortune", self.fixed_clock)
        with self.assertRaisesRegex(lp.HarnessError, "cannot record choice"):
            lp.record_choice(loaded, "Go on", None, "S02", self.fixed_clock)
        with self.assertRaisesRegex(lp.HarnessError, "cannot transition"):
            lp.goto_passage(loaded, "S02", self.fixed_clock)


class RollRecordingTests(HarnessTestCase):
    def _commit_choice(self, loaded: lp.LoadedSession) -> None:
        lp.record_choice(loaded, "Go on", None, "S02", self.fixed_clock)

    def test_roll_requires_a_committed_choice_and_captures_an_attribute(self) -> None:
        loaded = self.start()
        with self.assertRaisesRegex(lp.HarnessError, "committed choice"):
            lp.record_roll(loaded, "CUN", "standard", [15], self.fixed_clock)

        self._commit_choice(loaded)
        event = lp.record_roll(loaded, "cun", "standard", [15], self.fixed_clock)

        roll = loaded.workflow["roll"]
        self.assertEqual(event["type"], "roll_recorded")
        self.assertEqual(roll["attribute"], "CUN")
        self.assertEqual(roll["target"], 12)
        self.assertEqual(roll["choice_event"], 2)
        self.assertEqual(loaded.state["resources"]["Fortune"]["current"], 10)
        self.assertEqual(roll["fortune_status"], "pending")

    def test_roll_captures_current_fortune_as_its_target(self) -> None:
        loaded = self.start()
        self._commit_choice(loaded)

        lp.record_roll(loaded, "fortune", "standard", [8], self.fixed_clock)

        roll = loaded.workflow["roll"]
        self.assertEqual(roll["attribute"], "Fortune")
        self.assertEqual(roll["target"], 10)

    def test_pending_roll_blocks_transition_and_zero_spend_finalises_it(self) -> None:
        loaded = self.start()
        self._commit_choice(loaded)
        lp.record_roll(loaded, "CUN", "standard", [15], self.fixed_clock)

        with self.assertRaisesRegex(lp.HarnessError, "Fortune decision"):
            lp.goto_passage(loaded, "S02", self.fixed_clock)

        event = lp.record_fortune(loaded, 0, self.fixed_clock)
        self.assertEqual(event["type"], "fortune_decided")
        self.assertEqual(loaded.workflow["roll"]["fortune_status"], "decided")
        self.assertEqual(loaded.workflow["roll"]["fortune_spent"], 0)
        self.assertEqual(loaded.workflow["roll"]["final_die"], 15)
        lp.goto_passage(loaded, "S02", self.fixed_clock)

    def test_fortune_decision_deducts_from_current_resource(self) -> None:
        loaded = self.start()
        self._commit_choice(loaded)
        lp.record_roll(loaded, "CUN", "standard", [15], self.fixed_clock)

        lp.record_fortune(loaded, 3, self.fixed_clock)

        self.assertEqual(loaded.state["resources"]["Fortune"]["current"], 7)
        self.assertEqual(loaded.workflow["roll"]["final_die"], 12)
        self.assertEqual(loaded.workflow["roll"]["final_margin"], 0)

    def test_locked_roll_is_immediately_final_and_rejects_fortune(self) -> None:
        loaded = self.start()
        self._commit_choice(loaded)
        lp.record_roll(loaded, "BRN", "standard", [1], self.fixed_clock)

        self.assertEqual(loaded.workflow["roll"]["fortune_status"], "forbidden")
        with self.assertRaisesRegex(lp.HarnessError, "locked natural"):
            lp.record_fortune(loaded, 0, self.fixed_clock)
        lp.goto_passage(loaded, "S02", self.fixed_clock)

    def test_second_roll_before_transition_is_rejected(self) -> None:
        loaded = self.start()
        self._commit_choice(loaded)
        lp.record_roll(loaded, "CUN", "standard", [15], self.fixed_clock)

        with self.assertRaisesRegex(lp.HarnessError, "existing roll"):
            lp.record_roll(loaded, "BRN", "standard", [12], self.fixed_clock)

    def test_invalid_dice_and_fortune_leave_persisted_files_unchanged(self) -> None:
        loaded = self.start()
        self._commit_choice(loaded)
        events_path = loaded.directory / "events.jsonl"
        cache_path = loaded.directory / "session.json"
        before_dice = (events_path.read_bytes(), cache_path.read_bytes())

        with self.assertRaises(lp.HarnessError):
            lp.record_roll(loaded, "CUN", "standard", [21], self.fixed_clock)
        self.assertEqual((events_path.read_bytes(), cache_path.read_bytes()), before_dice)

        lp.record_roll(loaded, "CUN", "standard", [15], self.fixed_clock)
        before_fortune = (events_path.read_bytes(), cache_path.read_bytes())
        with self.assertRaises(lp.HarnessError):
            lp.record_fortune(loaded, 11, self.fixed_clock)
        self.assertEqual(
            (events_path.read_bytes(), cache_path.read_bytes()),
            before_fortune,
        )


class ReportTests(HarnessTestCase):
    def build_eventful_session(self) -> lp.LoadedSession:
        loaded = self.start("report-session")
        lp.show_current_passage(loaded, self.fixed_clock)
        player_note = lp.record_note(
            loaded,
            "player",
            "I hear a | pause\nand want to press on.",
            self.fixed_clock,
        )
        lp.record_note(loaded, "rules-question", "Can Fortune help?", self.fixed_clock)
        lp.record_rules_lookup(loaded, "Fortune", self.fixed_clock)
        lp.record_choice(loaded, "Press onward", "spoken choice", "S02", self.fixed_clock)
        lp.record_roll(loaded, "CUN", "standard", [15], self.fixed_clock)
        lp.record_fortune(loaded, 3, self.fixed_clock)
        lp.goto_passage(loaded, "S02", self.fixed_clock)
        lp.change_collection(
            loaded,
            "possessions",
            "add",
            "Guard's spear",
            "Taken from guard",
            clock=self.fixed_clock,
        )
        lp.change_collection(
            loaded,
            "possessions",
            "consume",
            "Guard's spear",
            "Used to bar a door",
            clock=self.fixed_clock,
        )
        lp.record_note(
            loaded,
            "operator",
            "Observed ambiguity: which door?",
            self.fixed_clock,
        )
        lp.pause_session(loaded, "Voice break", self.fixed_clock)
        loaded = lp.load_session(self.root / "sessions", "report-session")
        lp.resume_session(loaded, self.fixed_clock)
        lp.correct_session(
            loaded,
            player_note["number"],
            "The player clarified the pause.",
            "annotate",
            replacement_text="The player named the pause.",
            clock=self.fixed_clock,
        )
        lp.finish_session(loaded, "S02 — passage completed", self.fixed_clock)
        return loaded

    def test_report_is_deterministic_complete_and_derived(self) -> None:
        loaded = self.build_eventful_session()
        event_bytes = (loaded.directory / "events.jsonl").read_bytes()
        cache_bytes = (loaded.directory / "session.json").read_bytes()

        first = lp.render_report(loaded.document, loaded.events)
        second = lp.render_report(loaded.document, loaded.events)
        self.assertEqual(first, second)
        self.assertEqual(
            [line for line in first.splitlines() if line.startswith("#")],
            [
            "# Live Playtest Report",
            "## Session",
            "## Route",
            "## Player narration",
            "## Operator observations",
            "## Choices and tests",
            "## State history",
            "## Rules activity",
            "## Corrections and pauses",
            "## Timing",
            "## Final state",
            "## Limitations",
            ],
        )
        self.assertIn("| ID | report-session |", first)
        self.assertIn("| Purpose | Natural calibration playthrough |", first)
        self.assertIn("| Dice mode | physical |", first)
        self.assertIn("| Observer mode | neutral |", first)
        for label in ("story", "rules", "sheet"):
            reader = loaded.document["reader_files"][label]
            self.assertIn(reader["path"], first)
            self.assertIn(reader["sha256"], first)
        self.assertIn("Guard's spear", first)
        self.assertIn("consum", first.casefold())
        self.assertIn("I hear a \\| pause<br>and want to press on.", first)
        self.assertIn("Observed ambiguity: which door?", first)
        self.assertIn("Can Fortune help?", first)
        self.assertIn(loaded.events[4]["data"]["sha256"], first)
        self.assertIn(
            "| 6 | Press onward | spoken choice | S02 | CUN | standard | 15 |",
            first,
        )
        self.assertIn("| decided | 3 | 12 | 0 | yes |", first)
        self.assertIn("Taken from guard", first)
        self.assertIn("Possessions: Sword \\| Guard's spear", first)
        self.assertIn("The player clarified the pause.", first)
        self.assertIn("recorded corrected wording", first)
        self.assertIn("| 13 | 2026-07-31T10:00:00Z | pause |", first)
        self.assertIn("| 14 | 2026-07-31T10:00:00Z | resume |", first)
        self.assertIn("Interaction interval", first)
        self.assertIn("Passage: S02", first)
        self.assertIn("Status: finished", first)
        self.assertIn("Outcome: S02 — passage completed", first)
        for limitation in (
            "raw audio was not retained",
            "Voice-derived text is stored as received",
            "Codex was not blind to unread material",
            "not a blind or controlled experiment",
            "Timing includes network, tool, and transcription delay",
            "One player cannot establish general behaviour",
        ):
            self.assertIn(limitation, first)

        report_path = lp.write_report(loaded)
        first_bytes = report_path.read_bytes()
        report_path = lp.write_report(loaded)
        self.assertEqual(report_path.read_bytes(), first_bytes)
        self.assertNotIn(b"\r", first_bytes)
        self.assertEqual((loaded.directory / "events.jsonl").read_bytes(), event_bytes)
        self.assertEqual((loaded.directory / "session.json").read_bytes(), cache_bytes)

    def test_report_normalizes_finish_outcome_to_lf(self) -> None:
        loaded = self.start("crlf-outcome")
        lp.finish_session(loaded, "first line\r\nsecond line", self.fixed_clock)

        report_path = lp.write_report(loaded)

        report_bytes = report_path.read_bytes()
        self.assertNotIn(b"\r", report_bytes)
        self.assertIn(b"Outcome: first line\nsecond line", report_bytes)

    def test_report_marks_two_die_natural_margin_as_resolution_inert(self) -> None:
        loaded = self.start("natural-report")
        lp.show_current_passage(loaded, self.fixed_clock)
        lp.record_choice(loaded, "Press onward", "spoken choice", "S02", self.fixed_clock)
        lp.record_roll(loaded, "BRN", "disadvantage", [1, 20], self.fixed_clock)
        lp.goto_passage(loaded, "S02", self.fixed_clock)
        report = lp.render_report(loaded.document, loaded.events)

        self.assertIn("Margin resolution-inert", report)
        self.assertIn(
            "| 3 | Press onward | spoken choice | S02 | BRN | disadvantage | 1, 20 | 1 | 20 | 13 | -7 | 20 | yes | forbidden | 0 | 20 | -7 | no |",
            report,
        )

    def test_unfinished_report_marks_empty_sections_and_final_state(self) -> None:
        loaded = self.start("unfinished-report")

        report = lp.render_report(loaded.document, loaded.events)

        self.assertGreaterEqual(report.count("None recorded."), 7)
        self.assertIn("Session unfinished", report)
        self.assertIn("Passage: S01", report)
        self.assertIn("Status: active", report)


class TowerSmokeReplayTests(unittest.TestCase):
    """Prove the audited route against the authoritative Tower reader files."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(__file__).resolve().parents[1]

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def fixed_clock(self) -> str:
        return "2026-07-31T10:00:00Z"

    def test_audited_s01_to_s14_route_replays_the_reported_state(self) -> None:
        tower = self.root / "stories/public_domain/howard/tower_of_the_elephant/playtest"
        loaded = lp.start_session(
            Path(self.temporary_directory.name) / "sessions",
            "tower-smoke",
            tower / "slice-01.md",
            tower / "quick-rules.md",
            tower / "adventure-sheet.md",
            "Deterministic audited route replay",
            "The observer reproduces the existing 7/6/0 route",
            lp.build_initial_state(
                {"BRN": 13, "AGI": 12, "CUN": 12, "WIL": 12},
                {"Fortune": (10, 10), "Stamina": (6, 6)},
                ("Exposure", 0, 5),
                ["Sword"],
                [],
                "S01",
            ),
            self.fixed_clock,
        )

        def choose_and_go(text: str, destination: str) -> None:
            lp.show_current_passage(loaded, self.fixed_clock)
            lp.record_choice(
                loaded,
                text,
                None,
                destination,
                self.fixed_clock,
            )
            lp.goto_passage(loaded, destination, self.fixed_clock)

        choose_and_go("Climb now", "S03")
        choose_and_go("Examine the corpse", "S04")
        lp.show_current_passage(loaded, self.fixed_clock)
        lp.record_choice(loaded, "Take the guard's spear", None, "S05", self.fixed_clock)
        lp.change_collection(
            loaded,
            "possessions",
            "add",
            "Guard's spear",
            "Printed S04 discovery",
            clock=self.fixed_clock,
        )
        lp.goto_passage(loaded, "S05", self.fixed_clock)

        lp.show_current_passage(loaded, self.fixed_clock)
        lp.record_choice(loaded, "Stalk the stranger", "Stalk", "S06", self.fixed_clock)
        lp.record_roll(loaded, "CUN", "standard", [15], self.fixed_clock)
        lp.record_fortune(loaded, 3, self.fixed_clock)
        lp.goto_passage(loaded, "S06", self.fixed_clock)

        choose_and_go("Hear the alliance", "S07")
        choose_and_go("Accept Taurus", "S08")
        choose_and_go("Cross the inner wall", "S09")
        choose_and_go("Trust Taurus", "S10")
        choose_and_go("Advance after the cloud", "S11")

        lp.show_current_passage(loaded, self.fixed_clock)
        lp.record_choice(
            loaded,
            "Brace the guard's spear",
            "Brace the guard's spear",
            "S12",
            self.fixed_clock,
        )
        lp.change_collection(
            loaded,
            "possessions",
            "consume",
            "Guard's spear",
            "Committed before the S11 roll",
            clock=self.fixed_clock,
        )
        lp.record_roll(loaded, "BRN", "advantage", [6, 20], self.fixed_clock)
        lp.record_fortune(loaded, 0, self.fixed_clock)
        lp.goto_passage(loaded, "S12", self.fixed_clock)
        choose_and_go("Give Taurus room to finish the cast", "S14")
        lp.show_current_passage(loaded, self.fixed_clock)
        lp.finish_session(loaded, "S14 — slice complete", self.fixed_clock)
        lp.write_report(loaded)

        self.assertEqual(
            loaded.state["resources"],
            {
                "Fortune": {"current": 7, "maximum": 10},
                "Stamina": {"current": 6, "maximum": 6},
            },
        )
        self.assertEqual(
            loaded.state["pressure"],
            {"name": "Exposure", "current": 0, "maximum": 5},
        )
        self.assertEqual(loaded.state["possessions"], ["Sword"])
        self.assertEqual(loaded.state["story_marks"], [])
        self.assertEqual(loaded.state["current_passage"], "S14")
        self.assertEqual(loaded.state["status"], "finished")
        self.assertEqual(lp.replay_events(loaded.events)["state"], loaded.state)
        reloaded = lp.load_session(Path(self.temporary_directory.name) / "sessions", "tower-smoke")
        self.assertEqual(reloaded.state, loaded.state)
        self.assertEqual(reloaded.workflow, loaded.workflow)
        report = (loaded.directory / "report.md").read_text(encoding="utf-8")
        self.assertIn("15", report)
        self.assertIn("-3", report)
        self.assertIn("Fortune", report)
        self.assertIn("6, 20", report)
        self.assertIn("Guard's spear", report)
        self.assertIn("S14", report)


class CliTests(HarnessTestCase):
    """Exercise the operator contract through main, without a subprocess."""

    def command(self, *arguments: str) -> tuple[int, str, str]:
        stdout = StringIO()
        stderr = StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = lp.main(list(arguments))
        return status, stdout.getvalue(), stderr.getvalue()

    def start_arguments(self, session_id: str = "cli-session") -> list[str]:
        return [
            "--sessions-dir", str(self.root / "sessions"),
            "start", session_id,
            "--story", str(self.story),
            "--rules", str(self.rules),
            "--sheet", str(self.sheet),
            "--purpose", "Natural calibration playthrough",
            "--start-passage", "S01",
            "--attribute", "BRN=13",
            "--attribute", "AGI=12",
            "--attribute", "CUN=12",
            "--attribute", "WIL=12",
            "--resource", "Fortune=10/10",
            "--resource", "Stamina=6/6",
            "--pressure", "Exposure=0/5",
            "--possession", "Sword",
        ]

    def session_arguments(self, *arguments: str) -> tuple[str, ...]:
        return (
            "--sessions-dir", str(self.root / "sessions"),
            *arguments,
        )

    def test_help_exposes_all_and_only_the_locked_command_surface(self) -> None:
        parser = lp.build_parser()
        help_text = parser.format_help()
        for command in (
            "start", "show", "state", "note", "lookup", "choose", "roll",
            "fortune", "apply", "goto", "correct", "recover-cache", "pause",
            "resume", "finish", "report",
        ):
            self.assertIn(command, help_text)

        option_strings: set[str] = set()
        parsers = [parser]
        while parsers:
            current = parsers.pop()
            for action in current._actions:
                option_strings.update(action.option_strings)
                choices = getattr(action, "choices", None)
                if isinstance(choices, dict):
                    parsers.extend(
                        choice for choice in choices.values()
                        if isinstance(choice, type(parser))
                    )
        for forbidden in ("--rng", "--prose-rewrite", "--ai", "--simulation", "--passage-list"):
            self.assertNotIn(forbidden, option_strings)
        for correction_option in (
            "--annotate", "--set-resource", "--set-pressure", "--add-possession",
            "--remove-possession", "--add-mark", "--remove-mark", "--set-passage",
            "--clear-workflow",
        ):
            self.assertIn(correction_option, option_strings)

    def test_start_show_and_state_create_and_read_the_session(self) -> None:
        status, stdout, stderr = self.command(*self.start_arguments())
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertEqual(json.loads(stdout)["event"]["type"], "session_started")
        self.assertTrue((self.root / "sessions" / "cli-session" / "session.json").exists())

        status, stdout, stderr = self.command(*self.session_arguments("show", "cli-session"))
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertIn("## S01 — First", stdout)
        self.assertNotIn("## S02 — Second", stdout)

        status, stdout, stderr = self.command(*self.session_arguments("state", "cli-session"))
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertIn("Passage: S01", stdout)
        self.assertIn("Fortune: 10/10", stdout)
        self.assertIn("Exposure: 0/5", stdout)

    def test_event_commands_dispatch_all_families(self) -> None:
        status, _, stderr = self.command(*self.start_arguments())
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")

        def record(*arguments: str, event_type: str) -> dict[str, object]:
            status, stdout, stderr = self.command(*self.session_arguments(*arguments))
            self.assertEqual(status, 0, stderr)
            self.assertEqual(stderr, "")
            payload = json.loads(stdout)
            self.assertEqual(payload["event"]["type"], event_type)
            self.assertIn("state", payload)
            return payload

        record("note", "cli-session", "--kind", "operator", "--text", "Observed pause", event_type="operator_note")
        status, stdout, stderr = self.command(*self.session_arguments("lookup", "cli-session", "--section", "Fortune"))
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertIn("## Fortune", stdout)
        record("choose", "cli-session", "--text", "Press onward", "--method", "spoken", "--destination", "S02", event_type="choice_committed")
        record("roll", "cli-session", "--attribute", "CUN", "--mode", "standard", "--die", "15", event_type="roll_recorded")
        record("fortune", "cli-session", "--spend", "3", event_type="fortune_decided")
        record("goto", "cli-session", "S02", event_type="passage_transition")
        record("apply", "resource", "cli-session", "Stamina", "--delta", "-1", "--reason", "Injury", event_type="resource_changed")
        record("apply", "pressure", "cli-session", "--delta", "2", "--reason", "Noise", event_type="pressure_changed")
        record("apply", "possession", "cli-session", "add", "Spear", "--reason", "Taken", event_type="possession_changed")
        record("apply", "mark", "cli-session", "add", "Saw smoke", "--reason", "Observed", event_type="story_mark_changed")
        record("correct", "cli-session", "--target-event", "1", "--reason", "Clarification", "--annotate", "Corrected purpose", event_type="correction")
        record("pause", "cli-session", "--reason", "Break", event_type="session_paused")
        record("resume", "cli-session", event_type="session_resumed")
        record("finish", "cli-session", "--outcome", "S02 complete", event_type="session_finished")

        status, stdout, stderr = self.command(*self.session_arguments("report", "cli-session"))
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertEqual(Path(stdout.strip()), self.root / "sessions" / "cli-session" / "report.md")

    def test_every_correction_option_maps_to_its_operation_and_state(self) -> None:
        def expected_state(
            *,
            stamina: int = 6,
            pressure: int = 0,
            possessions: list[str] | None = None,
            marks: list[str] | None = None,
            passage: str = "S01",
        ) -> dict[str, object]:
            return {
                "attributes": {"BRN": 13, "AGI": 12, "CUN": 12, "WIL": 12},
                "resources": {
                    "Fortune": {"current": 10, "maximum": 10},
                    "Stamina": {"current": stamina, "maximum": 6},
                },
                "pressure": {"name": "Exposure", "current": pressure, "maximum": 5},
                "possessions": ["Sword"] if possessions is None else possessions,
                "story_marks": [] if marks is None else marks,
                "current_passage": passage,
                "status": "active",
            }

        cases = (
            (
                "annotate",
                (),
                False,
                ("--annotate", "Corrected wording"),
                "annotate",
                {"replacement_text": "Corrected wording"},
                expected_state(),
                {"choice": None, "roll": None},
            ),
            (
                "set-resource",
                (),
                False,
                ("--set-resource", "Stamina=4"),
                "set-resource",
                {"name": "Stamina", "value": 4},
                expected_state(stamina=4),
                {"choice": None, "roll": None},
            ),
            (
                "set-pressure",
                (),
                False,
                ("--set-pressure", "3"),
                "set-pressure",
                {"value": 3},
                expected_state(pressure=3),
                {"choice": None, "roll": None},
            ),
            (
                "add-possession",
                (),
                False,
                ("--add-possession", "Shield"),
                "add-possession",
                {"name": "Shield"},
                expected_state(possessions=["Sword", "Shield"]),
                {"choice": None, "roll": None},
            ),
            (
                "remove-possession",
                (),
                False,
                ("--remove-possession", "Sword"),
                "remove-possession",
                {"name": "Sword"},
                expected_state(possessions=[]),
                {"choice": None, "roll": None},
            ),
            (
                "add-mark",
                (),
                False,
                ("--add-mark", "Saw smoke"),
                "add-mark",
                {"name": "Saw smoke"},
                expected_state(marks=["Saw smoke"]),
                {"choice": None, "roll": None},
            ),
            (
                "remove-mark",
                ("--mark", "Saw smoke"),
                False,
                ("--remove-mark", "Saw smoke"),
                "remove-mark",
                {"name": "Saw smoke"},
                expected_state(),
                {"choice": None, "roll": None},
            ),
            (
                "set-passage",
                (),
                False,
                ("--set-passage", "S02"),
                "set-passage",
                {"value": "S02"},
                expected_state(passage="S02"),
                {"choice": None, "roll": None},
            ),
            (
                "clear-workflow",
                (),
                True,
                ("--clear-workflow",),
                "clear-workflow",
                {},
                expected_state(),
                {"choice": None, "roll": None},
            ),
        )

        for (
            label,
            start_additions,
            prepare_choice,
            option,
            operation,
            correction_arguments,
            expected,
            workflow,
        ) in cases:
            with self.subTest(option=label):
                session_id = f"correction-{label}"
                start_arguments = self.start_arguments(session_id)
                start_arguments.extend(start_additions)
                status, _, stderr = self.command(*start_arguments)
                self.assertEqual(status, 0, stderr)
                if prepare_choice:
                    status, _, stderr = self.command(
                        *self.session_arguments(
                            "choose", session_id, "--text", "Press onward"
                        )
                    )
                    self.assertEqual(status, 0, stderr)

                status, stdout, stderr = self.command(
                    *self.session_arguments(
                        "correct",
                        session_id,
                        "--target-event",
                        "1",
                        "--reason",
                        "CLI correction",
                        *option,
                    )
                )
                self.assertEqual(status, 0, stderr)
                self.assertEqual(stderr, "")
                payload = json.loads(stdout)
                event = payload["event"]
                self.assertEqual(event["type"], "correction")
                self.assertEqual(event["data"]["target_event"], 1)
                self.assertEqual(event["data"]["reason"], "CLI correction")
                self.assertEqual(event["data"]["operation"], operation)
                self.assertEqual(event["data"]["arguments"], correction_arguments)
                self.assertEqual(event["after"], {"state": expected, "workflow": workflow})
                self.assertEqual(payload["state"], expected)

                loaded = lp.load_session(self.root / "sessions", session_id)
                self.assertEqual(loaded.state, expected)
                self.assertEqual(loaded.workflow, workflow)

    def test_malformed_start_values_are_harness_errors(self) -> None:
        for option, value in (
            ("--attribute", "BRN:not-an-integer"),
            ("--resource", "Fortune=10"),
            ("--pressure", "Exposure=0"),
        ):
            with self.subTest(option=option):
                arguments = self.start_arguments(f"bad-{option[2:]}")
                index = arguments.index(option)
                arguments[index + 1] = value
                status, stdout, stderr = self.command(*arguments)
                self.assertEqual(status, 2)
                self.assertEqual(stdout, "")
                self.assertTrue(stderr.startswith("error: "))
                self.assertNotIn("Traceback", stderr)

    def test_duplicate_attribute_or_resource_names_are_rejected_before_start(self) -> None:
        for option, duplicate in (
            ("--attribute", "brn=12"),
            ("--resource", "fortune=9/10"),
        ):
            with self.subTest(option=option):
                arguments = self.start_arguments(f"duplicate-{option[2:]}")
                arguments.extend((option, duplicate))
                status, stdout, stderr = self.command(*arguments)
                self.assertEqual(status, 2)
                self.assertEqual(stdout, "")
                self.assertIn("duplicate", stderr)
                self.assertFalse((self.root / "sessions" / f"duplicate-{option[2:]}").exists())

    def test_wrong_dice_and_unknown_session_exit_two_without_mutation(self) -> None:
        status, _, stderr = self.command(*self.start_arguments())
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        status, _, stderr = self.command(*self.session_arguments("choose", "cli-session", "--text", "Press onward"))
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        event_path = self.root / "sessions" / "cli-session" / "events.jsonl"
        before = event_path.read_bytes()
        status, stdout, stderr = self.command(*self.session_arguments("roll", "cli-session", "--attribute", "CUN", "--mode", "advantage", "--die", "7"))
        self.assertEqual(status, 2)
        self.assertEqual(stdout, "")
        self.assertTrue(stderr.startswith("error: "))
        self.assertNotIn("Traceback", stderr)
        self.assertEqual(event_path.read_bytes(), before)

        status, stdout, stderr = self.command(*self.session_arguments("state", "missing-session"))
        self.assertEqual(status, 2)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr.count("error: "), 1)
        self.assertNotIn("Traceback", stderr)

    def test_recover_cache_bypasses_normal_cache_verification(self) -> None:
        status, _, stderr = self.command(*self.start_arguments())
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        cache_path = self.root / "sessions" / "cli-session" / "session.json"
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
        cache["last_event"] = 0
        cache_path.write_text(json.dumps(cache), encoding="utf-8")

        status, stdout, stderr = self.command(*self.session_arguments("recover-cache", "cli-session"))
        self.assertEqual(status, 0)
        self.assertEqual(stderr, "")
        self.assertEqual(json.loads(stdout)["current_passage"], "S01")
        self.assertEqual(json.loads(cache_path.read_text(encoding="utf-8"))["last_event"], 1)
