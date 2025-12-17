from dribble.memory import (
    BuildPlayer,
    GetOffset,
    WriteBinaryBytes,
    WriteInteger,
    written_in_bytes,
    written_in_integers,
)
from dribble.models import GetCodeFromString
from dribble.utils import ConvertToGameValue
from rich import print

def ResolveWriteAddress(game, player, offset_info):
	# --- normalize offset ---
	raw_offset = offset_info.get("offset")
	if raw_offset is None:
		raise ValueError("offset_info missing required 'offset'")

	try:
		offset = int(raw_offset, 0) if isinstance(raw_offset, str) else int(raw_offset)
	except Exception:
		raise TypeError(f"Invalid offset value: {raw_offset}")

	# --- normalize derefAddress (optional) ---
	raw_deref = offset_info.get("derefAddress")
	if raw_deref is None:
		return player.address + offset

	try:
		deref = int(raw_deref, 0) if isinstance(raw_deref, str) else int(raw_deref)
	except Exception:
		raise TypeError(f"Invalid derefAddress value: {raw_deref}")

	# --- dereference using pymem-style read ---
	ptr_address = player.address + deref

	ptr_bytes = game.memory.read_bytes(ptr_address, 8)
	sub_ptr = int.from_bytes(ptr_bytes, byteorder="little")

	if not sub_ptr:
		raise ValueError(f"Null pointer at derefAddress {hex(deref)}")

	return sub_ptr + offset


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
        # Locally import the PromptPlayerVersions function
        from ui import PromptImportAllVersions, PromptPlayerVersions

        # Initialize lists to store players found and not found
        logs = []
        players_not_found = []

        # If there are multiple versions, prompt the user to select all or a specific one
        import_all_versions = PromptImportAllVersions()

        try:
            # Iterate through the players in the JSON file
            for name, data in self.json_file.items():
                # Check if the player is in the player list
                self.exporter.find_versions()
                first_version, versions = self.exporter.find_player_by_name(name)
                selected_players = []
                selected_player_objects = []

                # Prompt user to select which versions(s) to use
                if versions and len(versions) > 1:
                    if import_all_versions:
                        selected_players = [versions[version] for version in versions]
                    else:
                        selected_players = PromptPlayerVersions(versions)

                    # Compile the selected players into a list of player objects
                    for player_address in selected_players:
                        player_address = int(player_address, 16)
                        player = BuildPlayer(self.game, None, player_address)
                        if player:
                            selected_player_objects.append(player)
                else:
                    # Only the first version is available, so add it to the list
                    selected_player_objects.append(first_version)

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
                                        logs.append(
                                            f"Information for {item} not found in {category} offsets."
                                        )
                                        continue

                                    # Unpack the offset information & write the data to memory
                                    name = offset_info["name"]
                                    offset = offset_info["offset"]
                                    length = offset_info["length"]
                                    address = player.address + offset
                                    new_game_value = ConvertToGameValue(new_value, length)

                                    # Write the data to memory
                                    WriteBinaryBytes(
                                        self.game, address, length, new_game_value
                                    )

                            except Exception as e:
                                logs.append(f"Error writing {new_value} to {name}: {e}")

                    # Iterate through the categories that are written in integers (everything else)
                    for category in written_in_integers:
                        if category in data:
                            try:
                                for item, new_value in data[category].items():
                                    offset_info = GetOffset(category, item)
                                    if not offset_info:
                                        logs.append(f"Information for {item} not found in {category} offsets.")
                                        continue

                                    name = offset_info["name"]
                                    length = offset_info["length"]
                                    start_bit = offset_info.get("startBit", 0)
                                    address = ResolveWriteAddress(self.game, player, offset_info)

                                    if isinstance(new_value, str):
                                        new_game_value = GetCodeFromString(item, new_value)
                                        if new_game_value is None:
                                            logs.append(f"Invalid string representation for {name}: {new_value}")
                                            continue
                                    else:
                                        new_game_value = new_value

                                    WriteInteger(
                                        self.game,
                                        address,
                                        length,
                                        start_bit,
                                        new_game_value,
                                    )

                            except Exception as e:
                                logs.append(f"Error writing {new_value} to {name}: {e}")

        except Exception as e:
            line_no = getattr(e, "__traceback__", None).tb_lineno if getattr(e, "__traceback__", None) else "unknown"
            print(f"\n[red]Error during import at line @{line_no}: {e}.[/red]")

        # Write to the log file
        log_file_path = "configs/logs/import_log.txt"
        with open(log_file_path, "w") as log_file:
            if len(logs) > 0:
                for log in logs:
                    log_file.write(log + "\n")
            else:
                log_file.write("No errors found.\n")
        print(f"\n[green]Import completed. Logs saved to {log_file_path}[/green]")
