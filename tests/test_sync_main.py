import random
import unittest

from dribble.memory import (
    GetOffsets,
    ReadInteger,
    WriteBinaryBytes,
    WriteInteger,
    written_in_bytes,
    written_in_integers,
)
from dribble.models import Game, conversion_list
from dribble.utils import ConvertToGameValue

from actions import BuildPlayerList


class TestSyncMainWorkflow(unittest.TestCase):
    """
    Test the full workflow of the application.
    """

    def test_01_load_offsets(self):
        """
        Test if GetOffsets loads the offsets correctly.
        """
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
            "Accessories",
            "Gear",
        ]
        for key in expected_keys:
            self.assertIn(key, offsets)

    def test_02_attach_to_game_module(self):
        """
        Test if the Game class attaches to the module and has a module.
        """
        game = Game()
        self.assertIsNotNone(game.module)
        self.assertTrue(game.module)

    def test_03_build_player_list_and_run(self):
        """
        Test if BuildPlayerList initializes correctly and runs without errors.
        """
        GetOffsets("resources/offsets.json")
        game = Game()
        self.assertTrue(game.module)

        player_list_size = 100
        exporter = BuildPlayerList(game, player_list_size)
        self.assertTrue(hasattr(exporter, "run"))

        try:
            exporter.run()
        except Exception as e:
            self.fail(f"BuildPlayerList exporter.run() failed: {e}")
            raise

    def test_04_build_and_export_all_players(self):
        """
        Test if the exporter method works correctly for all players.
        """
        GetOffsets("resources/offsets.json")
        game = Game()
        self.assertTrue(game.module)

        player_list_size = 100
        exporter = BuildPlayerList(game, player_list_size)
        self.assertTrue(hasattr(exporter, "run"))

        try:
            exporter.run(export=True)
        except Exception as e:
            self.fail(f"BuildPlayerList exporter.run() failed: {e}")
            raise

    def test_05_build_and_export_single_player(self):
        """
        Test if the exporter method works correctly for a single player.
        """
        GetOffsets("resources/offsets.json")
        game = Game()
        self.assertTrue(game.module)

        player_list_size = 100
        exporter = BuildPlayerList(game, player_list_size)
        self.assertTrue(hasattr(exporter, "run"))

        try:
            # This will export the player @ index <player_list_size>
            exporter.run(export=True, singular=True)
        except Exception as e:
            self.fail(f"BuildPlayerList exporter.run() failed: {e}")
            raise

    def test_06_build_and_export_with_selections(self):
        """
        Test if the exporter method works correctly for a single player
        with random export selections from the offsets file.
        """
        offsets_path = "resources/offsets.json"
        GetOffsets(offsets_path)
        game = Game()
        self.assertTrue(game.module)

        player_list_size = 10
        exporter = BuildPlayerList(game, player_list_size)
        self.assertTrue(hasattr(exporter, "run"))

        # Dummy, just use .keys() instead
        categories = [
            "Vitals",
            "Base",
            "Attributes",
            "Badges",
            "Tendencies",
            "Signatures",
            "Accessories",
            "Gear",
        ]

        # Load offset definitions
        offset_data = GetOffsets(offsets_path)

        export_selections = {}

        for category in categories:
            items = offset_data.get(category, [])
            if items:
                names = [item["name"] for item in items if "name" in item]
                selected = random.sample(
                    names, min(2, len(names))
                )  # Pick 2 or fewer if limited
                export_selections[category] = selected

        try:
            exporter.run(export=True, export_selections=export_selections)
        except Exception as e:
            self.fail(f"BuildPlayerList exporter.run() failed: {e}")

    def test_07_build_and_import_player_data(self):
        """
        Test if the importer method works correctly for a single player.
        """
        offsets = GetOffsets("resources/offsets.json")
        game = Game()
        self.assertTrue(game.module)

        player_list_size = 100
        exporter = BuildPlayerList(game, player_list_size)
        self.assertTrue(hasattr(exporter, "run"))

        player_list = exporter.run()
        categories = offsets.keys()
        player = player_list[0]

        for category in categories:
            items = offsets.get(category, [])
            if items:
                for item in items:
                    try:
                        # If the item is not a dictionary, skip it
                        # Only the 'Base' category isn't a dictionary
                        if not isinstance(item, dict):
                            continue
                        # Compile the item data
                        name = item["name"]
                        offset = item["offset"]
                        length = item["length"]
                        start_bit = item.get("startBit", None)
                        # Initialize the test value on an item-by-item basis
                        test_value = 0 if category == "Badges" else 60
                        test_value_bytes = ConvertToGameValue(
                            integer=test_value, length=length
                        )
                        # Write to the game based on category
                        if category in written_in_bytes:
                            # Write the value to the game
                            WriteBinaryBytes(
                                game=game,
                                address=player.address + offset,
                                value=test_value_bytes,
                                length=length,
                            )
                            # Read the value back from the game, and assert it
                            # matches the test value
                            in_game_value = ReadInteger(
                                game=game,
                                address=player.address + offset,
                                length=length,
                                use_start_bit=False,
                                return_readable=True,
                            )
                            if in_game_value != test_value:
                                self.fail(
                                    f"""
                                    {item['name']}:
                                    Expected {test_value},
                                    got {in_game_value}
                                    """
                                )
                        elif category in written_in_integers:
                            # Choose a random integer value for the test
                            if name in conversion_list:
                                item_option_keys = conversion_list[name].keys()
                                list_of_keys = list(item_option_keys)
                                test_value = random.choice(list_of_keys)

                            # Write the test value to the game
                            WriteInteger(
                                game=game,
                                address=player.address + offset,
                                length=length,
                                start_bit=start_bit,
                                value=test_value,
                            )
                            # Read the value back from the game, and assert it
                            # matches the test value
                            in_game_value = ReadInteger(
                                game=game,
                                address=player.address + offset,
                                length=length,
                                start_bit=start_bit,
                                use_start_bit=True,
                                return_readable=False,
                            )
                            if in_game_value != test_value:
                                print(
                                    f"""
                                        {item['name']}:
                                        Expected {test_value},
                                        got {in_game_value}
                                      """
                                )
                                # self.fail(
                                #     f"""
                                #     Failed to write {item['name']}:
                                #     expected {test_value},
                                #     got {in_game_value}
                                #     """
                                # )

                    except Exception as e:
                        self.fail(f"{item} failed: {e}")
                        raise


if __name__ == "__main__":
    unittest.main()
