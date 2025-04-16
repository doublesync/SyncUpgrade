import unittest
import os
import json
import random
from pathlib import Path

from dribble.memory import GetOffsets
from dribble.models import Game
from actions.build_player_list import BuildPlayerList


class TestPlayerExportWorkflow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        GetOffsets("resources/offsets.json")
        cls.output_file = Path("exports/test_exports.json")
        cls.preset_file = "test.json"
        cls.selected_player_names = ["LeBron James", "Kevin Durant", "Tyrese Maxey"]

        cls.player_list_size = 10000
        cls.game = Game()
        cls.exporter = BuildPlayerList(cls.game, cls.player_list_size)

    def test_export_archies(self):
        export_selections = None
        selected_player_addresses = []

        # Load export preset
        try:
            with open(os.path.join("configs/presets", self.preset_file), "r") as f:
                export_selections = json.load(f)
        except Exception as e:
            self.fail(f"Could not load preset file: {e}")

        self.exporter.run()
        self.exporter.find_versions()

        for player_name in self.selected_player_names:
            player, versions = self.exporter.find_player_by_name(player_name)
            self.assertIsNotNone(player, f"Player {player_name} not found.")

            # ✅ Grab a random subset of version addresses
            version_addresses = list(versions.keys())
            self.assertGreater(
                len(version_addresses), 0, f"No versions found for {player_name}"
            )
            selected_versions = random.sample(
                version_addresses, min(2, len(version_addresses))
            )

            selected_player_addresses.extend(selected_versions)

        # Convert hex strings to integers
        selected_player_addresses = [
            int(addr, 16) for addr in selected_player_addresses
        ]

        self.exporter.run(
            export=True,
            export_file=str(self.output_file),
            export_selections=export_selections,
            only_include_addresses=selected_player_addresses,
        )

        data = self.exporter.player_dump

        self.assertTrue(data is not None, "Player dump is None.")

        self.assertIsInstance(data, dict, "Exported data is not a dictionary.")
        self.assertGreater(len(data), 0, "Exported data dictionary is empty.")

        names = [p.get("name") for p in data]
        for name in self.selected_player_names:
            self.assertIn(name, names, f"{name} not found in exported data.")

    @classmethod
    def tearDownClass(cls):
        if cls.output_file.exists():
            cls.output_file.unlink()
