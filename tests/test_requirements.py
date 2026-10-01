import unittest

from prototype_runner.pipeline import evaluate, requirement_results


class RequirementEngineTests(unittest.TestCase):
    def test_operators(self):
        self.assertTrue(evaluate(5, "eq", 5))
        self.assertTrue(evaluate(5, "gt", 4))
        self.assertTrue(evaluate(5, "gte", 5))
        self.assertTrue(evaluate(5, "between", [4, 6]))
        self.assertFalse(evaluate(5, "lt", 5))

    def test_missing_metric_is_unknown(self):
        reqs = [{"id": "R1", "component": "missing", "metric": "x", "operator": "eq", "target": 1}]
        results = requirement_results(reqs, {})
        self.assertEqual(results[0]["status"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
