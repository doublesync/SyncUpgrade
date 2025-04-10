import os
import json

from rich import print
from PyInquirer import prompt

from core import offsets

# A prompt that lets the user select a preset file
def prompt_preset_usage():
    """
    Prompt the user to use an export preset or create a new one.

    :return: True if the user wants to use a preset, False otherwise.
    """
    # Let's get a list of of export preset files in the configs directory
    preset_files = []
    preset_dir = "configs/presets"
    try:
        preset_files = [f for f in os.listdir(preset_dir) if f.endswith('.json')]
    except Exception as e:
        print(f"\n[red]Error reading preset directory: {e}[/red]")

    # If there are no preset files, we can skip this step
    if preset_files:

        # Print the list of preset files
        questions = [
            {
                'type': 'list',
                'name': 'preset',
                'message': 'Do you want to use a preset?',
                'choices': [
                    {'name': 'Yes', 'value': True},
                    {'name': 'No', 'value': False}
                ]
            }
        ]

        # Prompt the user for the preset choice
        answers = prompt(questions)
        answer = answers.get('preset', False)

        # If the user wants to use a preset, show the list of presets
        if answer:
            questions = [
                {
                    'type': 'list',
                    'name': 'preset_file',
                    'message': 'Select a preset file:',
                    'choices': preset_files
                }
            ]

            # Prompt the user for the selected preset file
            answers = prompt(questions)
            selected_preset = answers.get('preset_file', None)

            if selected_preset:
                return True, selected_preset
    
    # If the user doesn't want to use a preset or there are no presets, return False
    return False, None

# A prompt that lets the user create a new export preset
def prompt_preset_creation(contents):
    """
    Prompt the user to create a new export preset.
    """
    questions = [
        {
            'type': 'input',
            'name': 'preset_name',
            'message': 'Enter a name for the preset (or leave blank to skip):'
        }
    ]
    answers = prompt(questions)
    preset_name = answers.get('preset_name', None)

    if preset_name:
        preset_file = os.path.join("configs/presets", f"{preset_name}.json")
        with open(preset_file, 'w') as f:
            json.dump(contents, f, indent=4)

        print(f"\n[green]Export options saved as preset:[/green] {preset_file}")

# A prompt that lets the user select which items to export
def prompt_item_options():
    """
    Prompt the user for export options.

    :return: List of selected items for export.
    """
    choices = {}
    categories = [key for key in offsets.keys() if key != "Base"]

    # For each category, prompt the user to select items for export
    for category in categories:
        # Print the category name
        print(f"\n[cyan]Choose items to export from {category}[/cyan]")

        # Create a list of items for the current category
        item_list = [item["name"] for item in offsets[category]]
        questions = [
            {
                'type': 'checkbox',
                'name': 'selected_items',
                'message': 'Select items to export:',
                'choices': [
                    {'name': item} for item in item_list
                ]
            }
        ]

        # Prompt the user for the selected items & store them in the choices dictionary
        answers = prompt(questions)
        choices[category] = answers.get('selected_items', [])

    # Return the choices dictionary containing all selected items
    return choices

# A prompt that lets the user select a file for import
def prompt_import_file():
    """
    Prompt the user to select a file for import.

    :return: True if the file is valid, False otherwise.
    """
    # Let's get a list of import files in the configs directory
    import_files = []
    import_dir = "configs/imports"
    try:
        import_files = [f for f in os.listdir(import_dir) if f.endswith('.json')]
    except Exception as e:
        print(f"\n[red]Error reading import directory: {e}[/red]")

    # If there are no preset files, we can skip this step
    if import_files:
        questions = [
            {
                'type': 'list',
                'name': 'import_file',
                'message': 'Select a preset file:',
                'choices': import_files
            }
        ]

        # Prompt the user for the selected preset file
        answers = prompt(questions)
        import_file = answers.get('import_file', None)

        if import_file:
            print(f"\nUsing import file: [yellow]{import_file}[/yellow]")
            return import_file
    else:
        print("\n[red]No import files found in the directory.[/red]")

    # If the user doesn't want to use a preset or there are no presets, return False
    return None

# A prompt that lets the user select one or more options from a list of player duplicates
def prompt_player_duplicates(duplicates):
    """
    Prompt the user to select one or more options from a list of player duplicates.

    :param duplicates: List of duplicate players.
    :return: List of selected players.
    """
    questions = [
        {
            'type': 'checkbox',
            'name': 'selected_duplicates',
            'message': 'Select which duplicate(s) to use:',
            'choices': [{'name': str(player)} for player in duplicates]
        }
    ]

    # Prompt the user for the selected duplicates
    answers = prompt(questions)
    selected_duplicates = answers.get('selected_duplicates', [])

    return selected_duplicates

# A prompt that lets the user choose the size of the player list
def prompt_player_list_size():
    """
    Prompt the user for the size of the player list.

    :return: Size of the player list.
    """
    questions = [
        {
            'type': 'list',
            'name': 'import_file',
            'message': 'Select a player list size:',
            'choices': [
                {'name': '500', 'value': 500},
                {'name': '2,500', 'value': 2500},
                {'name': '5,000', 'value': 5000},
                {'name': '10,000 (Default)', 'value': 10000},
                {'name': '20,000', 'value': 20000},
                {'name': '30,000', 'value': 30000},
            ]
        }
    ]

    # Prompt the user for the player list size
    answers = prompt(questions)
    player_list_size = int(answers.get('player_list_size', 10000))

    input("\nPress Enter to continue...")

    return player_list_size