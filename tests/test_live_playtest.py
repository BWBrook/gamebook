from __future__ import annotations

import json
import tempfile
import unittest
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
