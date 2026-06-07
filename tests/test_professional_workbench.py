import re
import unittest
from pathlib import Path


HTML = Path(__file__).resolve().parents[1] / "petrochemical.html"


class ProfessionalWorkbenchContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HTML.read_text(encoding="utf-8")

    def test_professional_mode_and_workbench_regions_exist(self):
        self.assertIn('class="professional-mode"', self.html)
        self.assertIn('id="professional-workbench"', self.html)
        self.assertIn('class="panel evidence-panel"', self.html)
        self.assertIn('class="panel alarm-rail"', self.html)
        self.assertIn('id="alarmDetail"', self.html)
        self.assertIn('id="evidenceContent"', self.html)

    def test_alarm_response_functions_exist(self):
        for function_name in (
            "selectAlarm",
            "renderAlarmDetail",
            "updateAlarmState",
            "focusAlarmOnMap",
            "renderEvidence",
            "selectWorkbenchContext",
            "updateOperationalCounts",
        ):
            self.assertRegex(
                self.html,
                rf"function\s+{function_name}\s*\(",
                msg=f"missing {function_name}",
            )

    def test_professional_visual_and_responsive_contract_exists(self):
        for marker in (
            "--ops-selection:",
            "--ops-normal:",
            "--ops-warning:",
            "--ops-critical:",
            ".professional-mode .grid",
            ".professional-mode .alarm-rail",
            ".professional-mode .evidence-panel",
            "@media (prefers-reduced-motion: reduce)",
            "@media (max-width: 1100px)",
        ):
            self.assertIn(marker, self.html)

    def test_primary_alarm_queue_uses_accessible_buttons(self):
        self.assertIn('class="alert-item ${a.level} ${a.state ||', self.html)
        self.assertIn('aria-label="${a.title}', self.html)
        self.assertIn('onclick="selectAlarm(\'${a.id}\')"', self.html)

    def test_presentation_mode_is_preserved(self):
        self.assertIn('id="dashboard-mode"', self.html)
        self.assertRegex(self.html, r"function\s+toggleDashboardMode\s*\(")

    def test_connection_status_targets_unique_header_element(self):
        function = re.search(
            r"function\s+updateConnectionStatus\s*\([^)]*\)\s*\{(.*?)\n\}",
            self.html,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(function)
        self.assertIn("getElementById('connectionStatus')", function.group(1))
        self.assertNotIn("querySelector('.status-badge')", function.group(1))

    def test_websocket_state_sync_does_not_reassign_const_data_arrays(self):
        for assignment in (
            "personnelData = state.personnel",
            "equipmentData = state.equipment",
            "sensorsData = state.sensors",
            "alertsData = state.alerts",
        ):
            self.assertNotIn(assignment, self.html)
        self.assertRegex(self.html, r"function\s+replaceArrayContents\s*\(")

    def test_no_disruptive_entity_selection_alerts_remain(self):
        entity_functions = re.findall(
            r"function\s+(selectZone|selectPersonnel|selectEquipment)\s*\([^)]*\)\s*\{(.*?)\n\}",
            self.html,
            flags=re.DOTALL,
        )
        self.assertEqual(3, len(entity_functions))
        for name, body in entity_functions:
            self.assertNotIn("alert(", body, msg=f"{name} still uses alert()")


if __name__ == "__main__":
    unittest.main()
