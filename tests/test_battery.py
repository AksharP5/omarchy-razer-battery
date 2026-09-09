import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from battery import read_batteries


class BatteryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def device(self, pid="00B6", serial="test-mouse", level="142", charging="1"):
        path = self.root / f"0003:1532:{pid}.0001"
        path.mkdir()
        for name, value in {
            "device_type": "Razer DeathAdder V3 Pro",
            "device_serial": serial,
            "charge_level": level,
            "charge_status": charging,
        }.items():
            (path / name).write_text(value)
        return path

    def test_charging_mouse_ignores_empty_receiver(self):
        self.device()
        self.device(pid="00B7", serial="\0\n", level="0", charging="0")
        self.assertEqual(read_batteries(self.root), {
            "devices": [{"name": "Razer DeathAdder V3 Pro", "percentage": 56, "charging": True}],
            "error": "",
        })

    def test_same_mouse_is_deduplicated_and_charging_path_wins(self):
        self.device(pid="00B7", level="140", charging="0")
        self.device()
        self.assertEqual(len(read_batteries(self.root)["devices"]), 1)
        self.assertTrue(read_batteries(self.root)["devices"][0]["charging"])

    def test_real_zero_and_full_charge_are_valid(self):
        self.device(level="0", charging="0")
        self.device(pid="00B7", serial="second-mouse", level="255", charging="0")
        self.assertEqual([d["percentage"] for d in read_batteries(self.root)["devices"]], [0, 100])

    def test_invalid_data_is_reported_without_hiding_healthy_mouse(self):
        self.device(level="256")
        self.device(pid="00B7", serial="second-mouse")
        status = read_batteries(self.root)
        self.assertEqual(len(status["devices"]), 1)
        self.assertIn("Invalid battery response", status["error"])

    def test_unplug_during_read_drops_device(self):
        path = self.device()
        (path / "charge_status").unlink()
        self.assertEqual(read_batteries(self.root), {"devices": [], "error": ""})

    def test_permission_error_and_missing_driver_are_reported(self):
        self.device()
        with patch.object(Path, "read_text", side_effect=PermissionError("Permission denied")):
            self.assertIn("Permission denied", read_batteries(self.root)["error"])
        self.assertIn("not loaded", read_batteries(self.root / "missing")["error"])


if __name__ == "__main__":
    unittest.main()
