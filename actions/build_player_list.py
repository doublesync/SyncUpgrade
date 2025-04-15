import json

from dribble.memory import BuildPlayer
from rich.console import Console
from rich.progress import Progress

# Initialize the console for rich text output
console = Console()


# A class to export/build a list of players from the game memory
class BuildPlayerList(object):
    """
    A class to export/build a list of players from the game memory.

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
        self.player_dump = {}
        self.duplicates = {}

    def run(
        self,
        export=False,
        singular=False,
        export_selections=None,
        only_include_addresses=None,
    ):
        # Print initial loading message
        console.print("\n[cyan]Compiling player list...[/cyan]", justify="center")
        console.print(
            "[yellow]This may take a few seconds...[/yellow]\n", justify="center"
        )

        player_list = []  # Initialize player list
        player_dump = {}  # Initialize player dump

        # If we don't already have an initialized player list & dump, we need to create them
        if not self.player_list and not self.player_dump:
            # Start the progress bar & loading players
            with Progress(transient=True) as progress:
                task = progress.add_task(
                    "[green]Loading players...",
                    total=self.player_list_size if not singular else 1,
                )

                # Create list of players with their data from memory
                player_list_start = 0 if not singular else self.player_list_size - 1
                player_list = []
                player_dump = {}

                for i in range(player_list_start, self.player_list_size):
                    player = BuildPlayer(self.game, i)

                    # Update progress bar
                    progress.update(task, advance=1)

                    if player is not None:
                        full_name = f"{player.vitals['First Name']} {player.vitals['Last Name']}"
                        player_list.append(player)  # Store player object
                        player_dump[full_name] = {
                            "Address": player.address,
                        }
                        player_dump[full_name]["Attributes"] = player.attributes
                        player_dump[full_name]["Vitals"] = player.vitals
                        player_dump[full_name]["Badges"] = player.badges
                        player_dump[full_name]["Tendencies"] = player.tendencies
                        player_dump[full_name]["Signatures"] = player.signatures
                        player_dump[full_name]["Gear"] = player.gear
                        player_dump[full_name]["Accessories"] = player.accessories
                        player_dump[full_name]["Hotzones"] = player.hotzones
                        player_dump[full_name]["Team"] = player.team
                    else:
                        pass  # Skip if player is None
        else:
            # If player list & dump already exist, use them; filter if only_include_addresses is provided
            player_list = (
                self.player_list
                if not only_include_addresses
                else [
                    player
                    for player in self.player_list
                    if player.address in only_include_addresses
                ]
            )
            player_dump = (  # TODO: Looks like specific player exporting is working, however the versions are overwriting each other
                self.player_dump
                if not only_include_addresses
                else {
                    player_name: data
                    for player_name, data in self.player_dump.items()
                    if data["Address"] in only_include_addresses
                }
            )

        # Dump player_dump to a JSON file if export is True
        if export:
            # Check if the user wants to export specific selections
            if export_selections:
                filtered_dump = {}

                # Iterate through the player dump and filter based on user selections
                for player, data in player_dump.items():
                    for category, items in data.items():
                        if category in export_selections:
                            selected_keys = export_selections[category]
                            matching_items = {}

                            # Filter the items based on user selections
                            for item, value in items.items():
                                if item in selected_keys:
                                    matching_items[item] = value

                            # If there are matching items, add them to the filtered dump
                            if matching_items:
                                filtered_dump[player] = filtered_dump.get(player, {})
                                filtered_dump[player][category] = matching_items

                player_dump = filtered_dump

            # Export player_dump to a JSON file
            export_name = input(
                "\nEnter the name of the export file (without extension): "
            )
            export_dir = "configs/exports"
            with open(f"{export_dir}/{export_name}.json", "w") as f:
                json.dump(player_dump, f, indent=4)

        # Return the player list & store it in the class instance
        self.player_list = player_list
        self.player_dump = player_dump
        return player_list

    def find_duplicates(self):
        if self.duplicates:  # If duplicates already found, return them
            return self.duplicates

        if self.player_list:
            seen = set()  # Sets have faster lookups than Lists
            duplicates = {}

            for player in self.player_list:
                player_name = (
                    f"{player.vitals['First Name']} {player.vitals['Last Name']}"
                )
                player_team_key = player.team.get("Key", "Unknown")
                player_address = hex(player.address).upper()

                if player_name in seen:
                    # Ensure duplicates entry exists
                    duplicate_entry = duplicates.setdefault(player_name, {})
                    duplicate_entry[f"{player_name} on {player_team_key}"] = (
                        player_address
                    )
                else:
                    # Store the first occurrence in duplicates
                    seen.add(player_name)
                    duplicates[player_name] = {
                        f"{player_name} on {player_team_key}": player_address
                    }

            # Store and return duplicates
            self.duplicates = duplicates
            return duplicates

    def find_player_by_name(self, name):
        if self.player_list:
            for player in self.player_list:
                full_name = (
                    f"{player.vitals['First Name']} {player.vitals['Last Name']}"
                )
                if full_name.lower() == name.lower():
                    # Find the duplicates for the player (will include the first occurrence)
                    player_duplicates = self.duplicates.get(full_name, {})
                    return player, player_duplicates
            return None, None
