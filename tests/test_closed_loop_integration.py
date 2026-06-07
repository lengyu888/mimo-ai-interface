import unittest

import server


class ClosedLoopSocketTests(unittest.TestCase):
    def setUp(self):
        if not server.WEBSOCKET_AVAILABLE:
            self.skipTest("Flask-SocketIO is not installed")
        server.shared_state.reset()
        self.ai = server.socketio.test_client(server.app)
        self.petro = server.socketio.test_client(server.app)

    def tearDown(self):
        self.ai.disconnect()
        self.petro.disconnect()

    @staticmethod
    def events(client, name):
        return [event["args"][0] for event in client.get_received() if event["name"] == name]

    def test_ai_join_receives_complete_snapshot_and_timeline(self):
        self.petro.emit("join", {"room": "petrochemical_room"})
        self.petro.emit("petrochemical_update", {"type": "alerts", "data": [{"id": "A1"}]})
        self.ai.emit("join", {"room": "ai_room"})

        received = self.ai.get_received()
        state = next(event["args"][0] for event in received if event["name"] == "petrochemical_state")
        timeline = next(event["args"][0] for event in received if event["name"] == "integration_timeline")

        self.assertTrue(state["sourceOnline"])
        self.assertEqual([{"id": "A1"}], state["alerts"])
        self.assertIsNotNone(state["lastUpdate"])
        self.assertGreaterEqual(len(timeline), 1)

    def test_command_result_and_analysis_are_recorded(self):
        self.petro.emit("join", {"room": "petrochemical_room"})
        self.ai.emit("join", {"room": "ai_room"})
        self.ai.emit("ai_command", {"command": "focus_zone", "params": {"zoneId": 3}})
        command = self.events(self.petro, "ai_command")[0]

        self.petro.emit("command_result", {"commandId": command["commandId"], "status": "executed"})
        self.ai.emit("ai_analysis_result", {"type": "alarm_analysis", "summary": "Check tank"})

        timeline = server.shared_state.get_timeline()
        event_types = [item["type"] for item in timeline]
        self.assertIn("command_queued", event_types)
        self.assertIn("command_result", event_types)
        self.assertIn("ai_analysis", event_types)


if __name__ == "__main__":
    unittest.main()
