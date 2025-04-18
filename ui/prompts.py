import json
import os

from dribble.memory import GetOffsets
from PyInquirer import prompt
from rich import print


# A prompt that lets the user select a preset file
def PromptPresetUsage():
    """
    Prompt the user to use an export preset or create a new one.

    :return: True if the user wants to use a preset, False otherwise.
    """
    # Let's get a list of of export preset files in the configs directory
    preset_files = []
    preset_dir = "configs/presets"
    try:
        preset_files = [f for f in os.listdir(preset_dir) if f.endswith(".json")]
    except Exception as e:
        print(f"\n[red]Error reading preset directory: {e}[/red]")

    # If there are no preset files, we can skip this step
    if preset_files:

        # Print the list of preset files
        questions = [
            {
                "type": "list",
                "name": "preset",
                "message": "Do you want to use a preset?",
                "choices": [
                    {"name": "Yes", "value": True},
                    {"name": "No", "value": False},
                ],
            }
        ]

        # Prompt the user for the preset choice
        answers = prompt(questions)
        answer = answers.get("preset", False)

        # If the user wants to use a preset, show the list of presets
        if answer:
            questions = [
                {
                    "type": "list",
                    "name": "preset_file",
                    "message": "Select a preset file:",
                    "choices": preset_files,
                }
            ]

            # Prompt the user for the selected preset file
            answers = prompt(questions)
            selected_preset = answers.get("preset_file", None)

            if selected_preset:
                return True, selected_preset

    # If the user doesn't want to use a preset or there are no presets, return False
    return False, None


# A prompt that lets the user create a new export preset
def PromptPresetCreation(contents):
    """
    Prompt the user to create a new export preset.
    """
    questions = [
        {
            "type": "input",
            "name": "preset_name",
            "message": "Enter a name for the preset (or leave blank to skip):",
        }
    ]
    answers = prompt(questions)
    preset_name = answers.get("preset_name", None)

    if preset_name:
        preset_file = os.path.join("configs/presets", f"{preset_name}.json")
        with open(preset_file, "w") as f:
            json.dump(contents, f, indent=4)

        print(f"\n[green]Export options saved as preset:[/green] {preset_file}")


# A prompt that lets the user select which items to export
def PromptItemOptions():
    """
    Prompt the user for export options.

    :return: List of selected items for export.
    """
    choices = {}
    offsets = GetOffsets(None)
    categories = [key for key in offsets.keys() if key != "Base"]

    # For each category, prompt the user to select items for export
    for category in categories:
        # Print the category name
        print(f"\n[cyan]Choose items to export from {category}[/cyan]")

        # Create a list of items for the current category
        item_list = [item["name"] for item in offsets[category]]
        questions = [
            {
                "type": "checkbox",
                "name": "selected_items",
                "message": "Select items to export:",
                "choices": [{"name": item} for item in item_list],
            }
        ]

        # Prompt the user for the selected items & store them in the choices dictionary
        answers = prompt(questions)
        choices[category] = answers.get("selected_items", [])

    # Return the choices dictionary containing all selected items
    return choices


# A prompt that lets the user select a file for import
def PromptImportFile(custom_title=None):
    """
    Prompt the user to select a file for import.

    :return: True if the file is valid, False otherwise.
    """
    # Let's get a list of import files in the configs directory
    import_files = []
    import_dir = "configs/imports"
    try:
        import_files = [f for f in os.listdir(import_dir) if f.endswith(".json")]
    except Exception as e:
        raise Exception(f"Error reading import directory: {e}")

    # If there are no preset files, we can skip this step
    if not import_files:
        raise Exception("No import files found in the directory.")

    # Print the list of import files
    questions = [
        {
            "type": "list",
            "name": "import_file",
            "message": custom_title or "Select a file for import:",
            "choices": import_files,
        }
    ]

    # Prompt the user for the selected preset file
    answers = prompt(questions)
    import_file_name = answers.get("import_file", None)

    if not import_file_name:
        raise Exception("No import file selected.")

    import_file_path = os.path.join(import_dir, import_file_name)
    return import_file_path


# A prompt that lets the user select one or more options from a list of player versions
def PromptPlayerVersions(versions):
    """
    Prompt the user to select one or more options from a list of player versions.

    :param versions: List of versions players.
    :return: List of selected players.
    """
    questions = [
        {
            "type": "checkbox",
            "name": "selected_versions",
            "message": "Select which versions of this player to use:",
            "choices": [
                {"name": player, "value": versions[player]} for player in versions
            ],
        }
    ]

    # Prompt the user for the selected versions
    answers = prompt(questions)
    selected_versions = answers.get("selected_versions", [])

    return selected_versions


# A prompt that lets the user choose the size of the player list
def PromptPlayerListSize():
    """
    Prompt the user for the size of the player list.

    :return: Size of the player list.
    """
    questions = [
        {
            "type": "list",
            "name": "import_file",
            "message": "Select a player list size:",
            "choices": [
                {"name": "500", "value": 500},
                {"name": "2,500", "value": 2500},
                {"name": "5,000", "value": 5000},
                {"name": "10,000 (Default)", "value": 10000},
                {"name": "20,000", "value": 20000},
                {"name": "30,000", "value": 30000},
            ],
        }
    ]

    # Prompt the user for the player list size
    answers = prompt(questions)
    player_list_size = int(answers.get("player_list_size", 10000))

    input("\nPress Enter to continue...")

    return player_list_size


# A prompt that lets the user choose if they want to specify which players to export
def PromptExportPlayerSelection():
    """
    Prompt the user to specify which players to export.

    :return: True if the user wants to specify players, False otherwise.
    """
    questions = [
        {
            "type": "list",
            "name": "specify_players_choice",
            "message": "Do you want to use the player names in an existing import file to specify which players to export?",
            "choices": [
                {
                    "name": "Yes, but I want to select all player versions",
                    "value": "all_versions",
                },
                {
                    "name": "Yes, but I want to select specific player versions",
                    "value": "specific_versions",
                },
                {
                    "name": "No, but export all players from the player list",
                    "value": "full_list",
                },
            ],
        }
    ]

    # Prompt the user for the export player selection
    answers = prompt(questions)
    specify_players_choice = answers.get("specify_players_choice", False)

    return specify_players_choice


# A prompt that lets the user choose which players to export from the import file
def PromptSpecificExportPlayers(import_file_path):
    """
    Prompt the user to select which players to export from the import file.

    :param import_file_path: The import file path of the file to select players from.
    :return: List of selected players.
    """
    # Load the import file
    try:
        with open(import_file_path, "r") as f:
            import_data = json.load(f)
    except Exception:
        return []

    # Get the list of player names from the import data
    player_names = [player for player in import_data.keys()]

    # Prompt the user to select players from the list
    questions = [
        {
            "type": "checkbox",
            "name": "selected_players",
            "message": "Select players to export:",
            "choices": [{"name": player} for player in player_names],
        }
    ]

    # Prompt the user for the selected players
    answers = prompt(questions)
    selected_players = answers.get("selected_players", [])

    return selected_players


# A prompt that lets the user select if they want to use all versions of players
def PromptImportAllVersions():
    """
    Prompt the user to select if they want to use all versions of players.

    :return: True if the user wants to use all versions, False otherwise.
    """
    questions = [
        {
            "type": "list",
            "name": "import_all_versions",
            "message": "Do you want to import all versions of players?",
            "choices": [
                {"name": "Yes", "value": True},
                {"name": "No", "value": False},
            ],
        }
    ]

    # Prompt the user for the export all versions choice
    answers = prompt(questions)
    import_all_versions = answers.get("import_all_versions", False)

    return import_all_versions
