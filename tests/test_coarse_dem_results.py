import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "simulation" / "auger" / "results" / "phase-02a-coarse-dem-sweep.json"


class CoarseDemEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(RESULT.read_text(encoding="utf-8"))

    def scenario(self, rpm, cohesion):
        return next(
            item
            for item in self.data["scenarios"]
            if item["rpm"] == rpm and item["cohesion_to_weight"] == cohesion
        )

    def test_control_has_no_driven_discharge(self):
        self.assertEqual(self.scenario(0, 0.8)["discharged_during_run"], 0)

    def test_screw_conveys_material(self):
        self.assertGreater(self.scenario(60, 0.8)["discharged_during_run"], 0)

    def test_high_cohesion_is_more_pulsatile(self):
        low = self.scenario(60, 0.15)["delivery_cv"]
        high = self.scenario(60, 5.0)["delivery_cv"]
        self.assertGreater(high, low)

    def test_result_is_not_claimed_as_calibrated(self):
        self.assertEqual(self.data["status"], "MODELLED_UNCALIBRATED")


if __name__ == "__main__":
    unittest.main()
