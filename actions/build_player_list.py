from core import offsets
from memory import BuildPlayer

import json

class BuildPlayerList(object):
    """
    A class to export a list of players from the game memory.

    :param game: The game memory reader instance.
    :param player_list_size: The number of players to export.
    :param export: Whether to export the player list to a JSON file.
    :param singular: Whether to export a single player. Defaults to False.
    :return: None
    """
    def __init__(self, game, player_list_size):
        self.game = game
        self.player_list_size = player_list_size
        self.player_list = []
        self.duplicates = {}

    def run(self, export=False, singular=False):
        # Create a list of players with their data from memory
        player_list_start = 0 if singular == False else self.player_list_size - 1
        player_list = []
        player_dump = {}
        for i in range(player_list_start, self.player_list_size):
            player = BuildPlayer(self.game, i)
            if player != None:
                player_list.append(player) # Store the player object for later memory use
                player_dump[i] = {} # Initialize the player list entry for dumping
                player_dump[i]["Attributes"] = player.attributes if player else None
                player_dump[i]["Vitals"] = player.vitals if player else None
                player_dump[i]["Badges"] = player.badges if player else None
                player_dump[i]["Tendencies"] = player.tendencies if player else None
                player_dump[i]["Signatures"] = player.signatures if player else None
            else:
                pass # If the player is None, skip to the next iteration

        # Dump the player list to a JSON file if export is True
        if export == True:
            with open("dump.json", "w") as f:
                json.dump(player_dump, f, indent=4)

        # Return the player list & store it in the class instance
        self.player_list = player_list
        return player_list
    
    def find_duplicates(self):
        if self.player_list:
            seen = set()  # Sets have faster lookups than Lists
            duplicates = {}

            for player in self.player_list:
                player_name = f"{player.vitals['First Name']} {player.vitals['Last Name']}"
                player_team_key = player.team["Key"]
                player_address = hex(player.address).upper()

                if player_name in seen:
                    # Ensure duplicates entry exists
                    duplicate_entry = duplicates.setdefault(player_name, {})
                    duplicate_entry[player_team_key] = player_address
                else:
                    # Store the first occurrence in duplicates
                    seen.add(player_name)
                    duplicates[player_name] = {player_team_key: player_address}

            # Store and return duplicates
            self.duplicates = duplicates
            return duplicates

    
    def find_player_by_name(self, name):
        if self.player_list:
            for player in self.player_list:
                full_name = f"{player.vitals['First Name']} {player.vitals['Last Name']}"
                if full_name.lower() == name.lower():
                    player_duplicates = self.duplicates.get(full_name, {})
                    return player, player_duplicates
            return None, None