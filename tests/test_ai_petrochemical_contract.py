import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AI_HTML = (ROOT / "index.html").read_text(encoding="utf-8")
PETRO_HTML = (ROOT / "petrochemical.html").read_text(encoding="utf-8")


class AIPetrochemicalContractTests(unittest.TestCase):
    def test_ai_handles_initial_snapshot_and_merges_updates(self):
        for marker in (
            "aiSocket.on('petrochemical_state'",
            "function mergePetrochemicalUpdate(",
            "function renderIntegrationTimeline(",
            "function renderPetrochemicalConnectionState(",
        ):
            self.assertIn(marker, AI_HTML)

    def test_ai_query_response_updates_state_and_panel(self):
        self.assertIn("applyPetrochemicalSnapshot(response.data)", AI_HTML)

    def test_ai_exposes_closed_loop_actions(self):
        for marker in (
            "function sendPetrochemicalAction(",
            "acknowledge_alarm",
            "dispatch_alarm",
            "escalate_alarm",
            "resolve_alarm",
            "focus_zone",
        ):
            self.assertIn(marker, AI_HTML)

    def test_workbench_publishes_snapshot_and_reports_results(self):
        for marker in (
            "function publishPetrochemicalSnapshot(",
            "function reportCommandResult(",
            "function displayAIRecommendation(",
            "selectedContext",
        ):
            self.assertIn(marker, PETRO_HTML)


if __name__ == "__main__":
    unittest.main()
