import unittest
from sync_main import GetOffsets, Game, BuildPlayerList


class TestSyncMainWorkflow(unittest.TestCase):

    def test_get_offsets_loads_expected_keys(self):
        offsets = GetOffsets("resources/offsets.json")
        self.assertIsInstance(offsets, dict)
        self.assertGreater(len(offsets), 0)

        # Optional: check for known offset keys
        expected_keys = [
            "Vitals",
            "Base",
            "Attributes",
            "Badges",
            "Tendencies",
            "Signatures",
            "Acccessories",
            "Gear",
        ]
        for key in expected_keys:
            self.assertIn(key, offsets)

    def test_game_attaches_and_has_module(self):
        game = Game()
        self.assertIsNotNone(game.module)
        self.assertTrue(game.module)

    def test_build_player_list_initializes_and_runs(self):
        game = Game()
        self.assertTrue(game.module)

        player_list_size = 100  # Simulated prompt value
        exporter = BuildPlayerList(game, player_list_size)
        self.assertTrue(hasattr(exporter, "run"))

        try:
            exporter.run()
        except Exception as e:
            self.fail(f"BuildPlayerList exporter.run() failed: {e}")
            raise

    def test_full_workflow_mimic(self):
        pass
