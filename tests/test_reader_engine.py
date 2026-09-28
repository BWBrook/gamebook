from __future__ import annotations

import copy
from pathlib import Path
import unittest

from tools import reader_engine as engine
from tools.live_playtest import index_passages


class ReaderEngineTests(unittest.TestCase):
    def choose(self, state, identifier):
        return engine.act(state, "choose", {"choice_id": identifier})[0]

    def settle(self, state, dice, spend=0):
        state, _ = engine.act(state, "roll", {"dice": dice})
        if state["phase"] == "fortune":
            state, _ = engine.act(state, "fortune", {"spend": spend})
        return engine.act(state, "continue", {})[0]

    def to_lion(self, *, wait=False, discovery=None, stalk=None):
        state = self.choose(engine.initial_state(), "wait" if wait else "climb")
        if wait:
            state = self.choose(state, "climb")
        state = self.choose(state, "examine" if discovery else "pursue")
        if discovery:
            state = self.choose(state, discovery)
        if discovery == "read_body":
            state = self.choose(state, "recognise")
        elif stalk:
            state = self.settle(self.choose(state, "stalk"), stalk)
        else:
            state = self.choose(state, "call")
        state = self.choose(state, "continue")
        state = self.choose(state, "accept")
        for _ in range(3):
            state = self.choose(state, "continue")
        self.assertEqual(state["passage"], "S11")
        return state

    def test_complete_route_fortune_and_preserved_state(self):
        state = self.to_lion(wait=True, discovery="read_body")
        self.assertEqual(state["marks"], [engine.WARNED])
        state = self.choose(state, "sword")
        state, _ = engine.act(state, "roll", {"dice": [16]})
        self.assertEqual(state["phase"], "fortune")
        self.assertEqual(state["fortune"], 10)
        state, event = engine.act(state, "fortune", {"spend": 3})
        self.assertEqual(state["result"]["outcome"], "success")
        self.assertEqual(event["roll"]["final_die"], 13)
        state = engine.act(state, "continue", {})[0]
        state = self.choose(state, "continue")
        self.assertEqual((state["passage"], state["phase"]), ("S14", "ended"))
        self.assertEqual((state["fortune"], state["stamina"], state["exposure"]), (7, 6, 1))
        self.assertEqual(state["history"], ["S01", "S02", "S03", "S04", "S05", "S06", "S07", "S08", "S09", "S10", "S11", "S12", "S14"])

    def test_all_lion_methods_success_failure_and_naturals(self):
        for method in ("spear", "sword", "evade"):
            for face, passage in ((1, "S12"), (12, "S12"), (19, "S13"), (20, "E03")):
                with self.subTest(method=method, face=face):
                    state = self.to_lion(discovery="take_spear")
                    before = copy.deepcopy(state)
                    state = self.choose(state, method)
                    self.assertEqual(engine.SPEAR in state["possessions"], method != "spear")
                    state = self.settle(state, [face, face] if method == "spear" else [face])
                    self.assertEqual(state["passage"], passage)
                    if face == 19:
                        self.assertEqual(state["stamina"], before["stamina"] - (1 if method == "evade" else 2))
                        self.assertEqual(state["exposure"], before["exposure"] + (2 if method == "evade" else 1))
                    else:
                        self.assertEqual(state["stamina"], before["stamina"])

    def test_only_kept_natural_locks_advantage(self):
        state = self.choose(self.to_lion(discovery="take_spear"), "spear")
        ordinary = engine.act(state, "roll", {"dice": [20, 19]})[0]
        self.assertEqual(ordinary["phase"], "fortune")
        self.assertEqual(self.settle(state, [20, 1])["passage"], "S12")
        death = engine.act(state, "roll", {"dice": [20, 20]})[0]
        self.assertEqual(death["result"]["outcome"], "natural 20")
        with self.assertRaises(engine.ReaderError):
            engine.act(death, "fortune", {"spend": 10})

    def test_wait_and_pursuit_advantage_and_mark_consumption(self):
        for wait, discovery, mode in ((False, None, "advantage"), (False, "take_spear", "standard"), (True, "take_spear", "advantage")):
            state = self.choose(engine.initial_state(), "wait" if wait else "climb")
            if wait:
                self.assertIn(engine.WARNED, state["marks"])
                state = self.choose(state, "climb")
            state = self.choose(state, "examine" if discovery else "pursue")
            if discovery:
                state = self.choose(state, discovery)
            state = self.choose(state, "stalk")
            self.assertEqual(state["pending"]["roll"]["mode"], mode)
            self.assertNotIn(engine.WARNED, state["marks"])

    def test_exposure_five_escape_route(self):
        state = self.to_lion(wait=True, discovery="take_spear", stalk=[20, 20])
        self.assertEqual((state["stamina"], state["exposure"]), (4, 3))
        state = self.settle(self.choose(state, "evade"), [19])
        self.assertEqual((state["stamina"], state["exposure"], state["passage"]), (3, 5, "S13"))
        state = self.choose(state, "continue")
        self.assertEqual((state["passage"], state["phase"]), ("E02", "ended"))

    def test_stalk_costs_and_recognition_exclusivity(self):
        for face, stamina, exposure in ((1, 6, 0), (12, 6, 0), (19, 5, 1), (20, 4, 2)):
            state = self.to_lion(discovery="take_spear", stalk=[face])
            self.assertEqual((state["stamina"], state["exposure"]), (stamina, exposure))
        state = self.choose(self.choose(engine.initial_state(), "climb"), "examine")
        state = self.choose(state, "read_body")
        self.assertEqual([choice["id"] for choice in engine.choices(state)], ["recognise"])
        with self.assertRaises(engine.ReaderError):
            self.choose(state, "stalk")
        state = self.choose(state, "recognise")
        self.assertNotIn(engine.READ, state["marks"])
        self.assertNotIn(engine.SPEAR, state["possessions"])

    def test_s13_button_names_the_destination_the_sheet_dictates(self):
        state = self.to_lion(discovery="read_body")
        for stamina, exposure, destination in ((3, 2, "S14"), (3, 5, "E02"), (0, 5, "E03")):
            with self.subTest(stamina=stamina, exposure=exposure):
                probe = dict(copy.deepcopy(state), passage="S13", stamina=stamina, exposure=exposure)
                label = engine.choices(probe)[0]["label"]
                self.assertEqual(self.choose(probe, "continue")["passage"], destination)
                self.assertEqual(destination in label, destination != "S14")

    def test_costly_direct_choices_carry_hints_and_results_carry_no_engine_prose(self):
        hints = {choice["id"]: choice["hint"] for choice in engine.choices(engine.initial_state())}
        self.assertEqual(hints, {"climb": "", "wait": "+1 Exposure"})
        state = self.choose(self.to_lion(discovery="take_spear"), "evade")
        state, _ = engine.act(state, "roll", {"dice": [20]})
        self.assertEqual(set(state["result"]), {"outcome", "method", "destination", "changes"})
        self.assertEqual(state["result"]["method"], "evade")

    def test_endings_and_stamina_priority(self):
        state = self.to_lion(discovery="read_body")
        state.update(passage="S13", stamina=0, exposure=5)
        state = self.choose(state, "continue")
        self.assertEqual(state["passage"], "E03")
        state = self.to_lion(discovery="read_body")
        state.update(passage="S07")
        state = self.choose(state, "leave")
        self.assertEqual(state["passage"], "E01")
        self.assertEqual(engine.choices(state), [])
        with self.assertRaises(engine.ReaderError):
            self.choose(state, "accept")

    def test_bad_actions_are_atomic_and_cannot_repeat_costs(self):
        state = self.to_lion(discovery="read_body")
        with self.assertRaises(engine.ReaderError):
            self.choose(state, "spear")
        state = self.choose(state, "sword")
        before = copy.deepcopy(state)
        for action, payload in (("choose", {"choice_id": "sword"}), ("roll", {"dice": [True]}),
                                ("roll", {"dice": [0]}), ("roll", {"dice": [21]}),
                                ("roll", {"dice": [2, 3]}), ("roll", {"dice": "12"}),
                                ("roll", {"dice": [12], "target": 20}), ("continue", {})):
            with self.subTest(action=action, payload=payload), self.assertRaises(engine.ReaderError):
                engine.act(state, action, payload)
            self.assertEqual(state, before)
        state = engine.act(state, "roll", {"dice": [19]})[0]
        before = copy.deepcopy(state)
        for spend in (True, -1, 11, 2.5, "2"):
            with self.assertRaises(engine.ReaderError):
                engine.act(state, "fortune", {"spend": spend})
            self.assertEqual(state, before)
        result = engine.act(state, "fortune", {"spend": 0})[0]
        self.assertEqual(state, before)
        self.assertEqual(result["stamina"], 4)
        with self.assertRaises(engine.ReaderError):
            engine.act(result, "fortune", {"spend": 0})
        result = engine.act(result, "continue", {})[0]
        self.assertEqual(result["stamina"], 4)
        with self.assertRaises(engine.ReaderError):
            engine.act(result, "continue", {})

    def test_content_guard_accepts_current_text_rejects_drift(self):
        path = Path(__file__).resolve().parents[1] / "stories/public_domain/howard/tower_of_the_elephant/playtest/slice-01.md"
        passages = index_passages(path)
        engine.validate_content(passages)
        passages["S11"] = passages["S11"].replace("Brawn 13", "Brawn 14")
        with self.assertRaisesRegex(engine.ReaderError, "text has changed"):
            engine.validate_content(passages)


if __name__ == "__main__":
    unittest.main()
