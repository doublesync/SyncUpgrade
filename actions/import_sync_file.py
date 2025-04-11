from rich import print
from PyInquirer import prompt

from memory import (
    WriteBinaryBytes, 
    WriteInteger,  
    BuildPlayer,
    written_in_bytes, 
    written_in_integers
)
from core import (
    offsets, 
    GetOffset, 
    conversion_list, 
    GetCodeFromString,
    ConvertToGameValue
)

from actions import BuildPlayerList

from ui.prompts import prompt_player_duplicates

# A class to handle the import of a sync file to game memory
class ImportSyncFile(object):
    """
    Import a sync file.
    """
    def __init__(self, game, exporter, json_file):
        """
        Initialize the ImportSyncFile class.

        :param game: The game object.
        :param exporter: The exporter object that holds the player list.
        :param json_file: The JSON file containing the import data.
        :return: None
        """
        self.game = game
        self.exporter = exporter
        self.json_file = json_file

    def run(self):
        """
        Run the import process.

        :return: None
        """
        # Initialize lists to store players found and not found
        logs = []
        players_not_found = []

        # Iterate through the players in the JSON file
        for name, data in self.json_file.items():
            # Check if the player is in the player list
            self.exporter.find_duplicates()
            first_occurrence, duplicates = self.exporter.find_player_by_name(name)
            selected_players = []
            selected_player_objects = []

            # Prompt user to select which duplicate(s) to use
            if duplicates:
                # Get the actual player objects from the selected players {key: team_name, value: player_address}
                selected_players = prompt_player_duplicates(duplicates)
                for player_address in selected_players:
                    player_address = int(player_address, 16)  # Convert hex address to int
                    player = BuildPlayer(self.game, None, player_address)
                    if player:
                        selected_player_objects.append(player)
            else:
                selected_player_objects = [first_occurrence]
            
            # Iterate through the selected players
            for player in selected_player_objects:
                # Check if the player is found in the player list
                if not player:
                    players_not_found.append(name)
                    logs.append(f"Player not found: {name}")
                    continue

                # Iterate through the categories that are written in bytes (only attributes)
                for category in written_in_bytes:
                    if category in data:
                        try:
                            for item, new_value in data[category].items():
                                # Get the offset information for the category
                                offset_info = GetOffset(category, item)
                                if not offset_info: 
                                    logs.append(f"Information for {item} not found in offsets.")
                                    continue

                                # Unpack the offset information & write the data to memory
                                name = offset_info["name"]
                                offset = offset_info["offset"]
                                length = offset_info["length"]
                                address = player.address + offset
                                new_game_value = ConvertToGameValue(new_value, length)

                                # Write the data to memory
                                WriteBinaryBytes(self.game, address, length, new_game_value)

                        except Exception as e:
                            logs.append(f"Error writing {new_value} to {name}: {e}")

                # Iterate through the categories that are written in integers (everything else)
                for category in written_in_integers:
                    if category in data:
                        try:

                            for item, new_value in data[category].items():
                                # Get the offset information for the category
                                offset_info = GetOffset(category, item)
                                if not offset_info:
                                    logs.append(f"Information for {item} not found in offsets.")
                                    continue

                                # Unpack the offset information & write the data to memory
                                name = offset_info["name"]
                                offset = offset_info["offset"]
                                length = offset_info["length"]
                                start_bit = offset_info["startBit"]
                                address = player.address + offset

                                # Check if the value is a string representation and convert it to the appropriate type
                                if isinstance(new_value, str):
                                    new_game_value = GetCodeFromString(item, new_value)
                                    if new_game_value is None:
                                        logs.append(f"Invalid string representation for {name}: {new_value}")
                                        continue
                                else:
                                    # Will use pre-defined 'new_game_value' if the value is not redefined,
                                    # resulting in an error.
                                    new_game_value = new_value 

                                # Convert the new value to the game value and write it to memory
                                WriteInteger(self.game, address, length, start_bit, new_game_value)

                        except Exception as e:
                            logs.append(f"Error writing {new_value} to {name}: {e}")

        # Write to the log file
        log_file_path = "configs/logs/import_log.txt"
        with open(log_file_path, 'w') as log_file:
            for log in logs:
                log_file.write(log + "\n")
        print(f"\n[green]Import completed. Logs saved to {log_file_path}[/green]")