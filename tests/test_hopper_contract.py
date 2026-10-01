import unittest

from cad.hopper import inspect_model


class HopperContractTests(unittest.TestCase):
    def test_inspector_returns_valid_metrics(self):
        metrics = inspect_model()
        self.assertTrue(metrics["solid_valid"])
        self.assertEqual(metrics["solid_count"], 1)
        self.assertGreater(metrics["capacity_ml"], 0)
        self.assertGreater(metrics["outlet_clear_diameter_mm"], 0)


if __name__ == "__main__":
    unittest.main()
