import unittest

from prototype_runner.workspace import build_manifest


class WorkspaceManifestTests(unittest.TestCase):
    def test_current_components_are_published(self):
        config = {
            "project": {
                "name": "Rangoli Printer Prototype",
                "units": "mm",
            },
            "components": [
                {"module": "cad.hopper"},
                {"module": "cad.auger"},
            ],
        }
        manifest = build_manifest(config)
        ids = {part["id"] for part in manifest["parts"]}
        self.assertIn("system-assembly-v1", ids)
        self.assertIn("hopper-shell-v1", ids)
        self.assertIn("auger-meter-v1", ids)
        self.assertIn("auger-screw-v1", ids)
        self.assertIn("auger-housing-v1", ids)


if __name__ == "__main__":
    unittest.main()
