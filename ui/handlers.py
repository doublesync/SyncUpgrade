import os
import sys
import json

from core.offsets import offsets
from actions import ImportSyncFile

from rich import print
from PyInquirer import prompt

from ui.prompts import (
    prompt_preset_usage, 
    prompt_preset_creation, 
    prompt_item_options, 
    prompt_import_file
)

# A function to handle the user's choice(s) from the main menu
def handle_choice(game, exporter, choice, **kwargs):
    """
    Handle the user's choice from the main menu.

    :param game: The game object.
    :param choice: The user's choice.
    :param kwargs: Additional arguments.
    :return: None
    """
    match choice:
        case "1":
            """
            Import player list data from a file.
            """
            import_file = prompt_import_file()
            if not import_file: 
                input("\nPress Enter to continue...")
                return

            import_file_path = os.path.join("configs/imports", import_file)

            try:
                # Load the import file
                with open(import_file_path, 'r') as f:
                    import_data = json.load(f)

                # Run the importer with the loaded data
                exporter.run() # Run the exporter first to intialize the player list
                importer = ImportSyncFile(game, exporter, import_data)
                importer.run()

            except Exception as e:
                print(f"\n[red]Error importing file: {e}.[/red]")

        case "2":
            """
            Export player list data to a file.
            """
            # Prompt the user for export options
            export_selections = None
            use_preset, preset_file = prompt_preset_usage()

            # If the user wants to use a preset, load the preset file
            # If not, prompt the user to create new export options
            if not use_preset:
                export_selections = prompt_item_options()
                prompt_preset_creation(export_selections)
            else:
                try:
                    export_selections = json.load(open(os.path.join("configs/presets", preset_file), 'r'))
                except Exception as e:
                    print(f"\n[red]Error loading preset file: {e}[/red]")
                    input("\nPress Enter to continue...")
                    return

            # Run the player_list with the selected export options & print a success message
            exporter.run(export=True, export_selections=export_selections)
            print("\n[green]Successfully exported players...[/green]\n")

        case _:
            print("\n[red]Invalid choice! Please select a valid option.[/red]")

    # Wait for user input before continuing
    input("\nPress Enter to continue...")