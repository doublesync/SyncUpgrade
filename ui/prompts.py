import json
import os
import requests

from dribble.memory import GetOffsets
from rich import print
from InquirerPy import inquirer


# A prompt that lets the user select a preset file
def PromptPresetUsage():
    preset_dir = "configs/presets"
    preset_files = []

    try:
        preset_files = [f for f in os.listdir(preset_dir) if f.endswith(".json")]
    except Exception as e:
        print(f"\n[red]Error reading preset directory: {e}[/red]")

    if preset_files:
        use_preset = inquirer.select(
            message="Do you want to use a preset?",
            choices=[
                ("Yes", True),
                ("No", False),
            ],
        ).execute()

        if use_preset:
            selected = inquirer.select(
                message="Select a preset file:",
                choices=preset_files,
            ).execute()

            return True, selected

    return False, None


# A prompt that lets the user create a new export preset
def PromptPresetCreation(contents):
    preset_name = inquirer.text(
        message="Enter a name for the preset (or leave blank to skip):"
    ).execute()

    if preset_name:
        preset_file = os.path.join("configs/presets", f"{preset_name}.json")
        with open(preset_file, "w") as f:
            json.dump(contents, f, indent=4)

        print(f"\n[green]Export options saved as preset:[/green] {preset_file}")


# A prompt that lets the user select which items to export
def PromptItemOptions():
    choices = {}
    offsets = GetOffsets(None)
    categories = [key for key in offsets.keys() if key != "Base"]

    for category in categories:
        print(f"\n[cyan]Choose items to export from {category}[/cyan]")

        item_list = [item["name"] for item in offsets[category]]
        selected_items = inquirer.checkbox(
            message="Select items to export:",
            choices=item_list,
            cycle=True,
            instruction="Press space to toggle, enter to confirm",
        ).execute()

        choices[category] = selected_items

    return choices


# A prompt that lets the user select a file for import
def PromptImportFile(custom_title=None):
    import_dir = "configs/imports"

    try:
        import_files = [f for f in os.listdir(import_dir) if f.endswith(".json")]
        import_files.append("Import from Dribble API")
    except Exception as e:
        raise Exception(f"Error reading import directory: {e}")

    if not import_files:
        raise Exception("No import files found in the directory.")

    selected = inquirer.select(
        message=custom_title or "Select a file for import:",
        choices=import_files,
    ).execute()
    
    if selected == "Import from Dribble API":
        return "api"
    else:
        return os.path.join(import_dir, selected)


# A prompt that lets the user select one or more options from a list of player versions
def PromptPlayerVersions(versions):
    selected = inquirer.checkbox(
        message="Select which versions of this player to use:",
        choices=[
            {"name": name, "value": versions[name]}
            for name in versions
        ],
        cycle=True,
    ).execute()

    return selected


# A prompt that lets the user choose the size of the player list
def PromptPlayerListSize():
    selected = inquirer.select(
        message="Select a player list size:",
        choices=[
            ("500", 500),
            ("2,500", 2500),
            ("5,000", 5000),
            ("10,000 (Default)", 10000),
            ("20,000", 20000),
            ("30,000", 30000),
        ],
    ).execute()

    input("\nPress Enter to continue...")

    return int(selected)


# A prompt that lets the user choose if they want to specify which players to export
def PromptExportPlayerSelection():
    selected = inquirer.select(
        message="Do you want to use the player names in an existing import file to specify players to export?",
        choices=[
            ("Yes, select all player versions", "all_versions"),
            ("Yes, select specific player versions", "specific_versions"),
            ("No, export all players from the player list", "full_list"),
        ],
    ).execute()

    return selected


# A prompt that lets the user choose which specific players to export
def PromptSpecificExportPlayers(import_file_path):
    try:
        with open(import_file_path, "r") as f:
            import_data = json.load(f)
    except Exception:
        return []

    player_names = list(import_data.keys())

    selected = inquirer.checkbox(
        message="Select players to export:",
        choices=player_names,
        cycle=True,
    ).execute()

    return selected


# A prompt that lets the user select if they want to use all versions of players
def PromptImportAllVersions():
    selected = inquirer.select(
        message="Do you want to import all versions of players?",
        choices=[
            ("Yes", True),
            ("No", False),
        ],
    ).execute()

    return selected
