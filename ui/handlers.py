import json
import os

from rich import print

from actions import ImportSyncFile
from ui.prompts import (PromptExportPlayerSelection, PromptImportFile,
                        PromptItemOptions, PromptPlayerVersions,
                        PromptPresetCreation, PromptPresetUsage,
                        PromptSpecificExportPlayers)


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
            import_file = PromptImportFile()
            if not import_file:
                input("\nPress Enter to continue...")
                return

            import_file_path = os.path.join("configs/imports", import_file)

            try:
                # Load the import file
                with open(import_file_path, "r") as f:
                    import_data = json.load(f)

                # Run the exporter to initialize the player list, then run the importer with the loaded data
                exporter.run()
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
            use_preset, preset_file = PromptPresetUsage()

            # If the user wants to use a preset, load the preset file
            # If not, prompt the user to create new export options
            if not use_preset:
                export_selections = PromptItemOptions()
                PromptPresetCreation(export_selections)
            else:
                try:
                    export_selections = json.load(
                        open(os.path.join("configs/presets", preset_file), "r")
                    )
                except Exception:
                    raise Exception("Error loading preset file from directory")

            # Check if the user wants to use the keys of an existing import file to specify which players to export
            specify_players_choice = PromptExportPlayerSelection()
            if specify_players_choice:
                import_file_path = PromptImportFile()
                selected_player_names = PromptSpecificExportPlayers(import_file_path)
                selected_player_addresses = []

                # Run the exporter first to initialize the player list & find duplicates
                exporter.run()
                exporter.find_duplicates()

                # Prompt the user to select which duplicates of each player to export
                for player_name in selected_player_names:
                    # Find the player and all of its duplicates by name
                    player, duplicates = exporter.find_player_by_name(player_name)
                    # If the player is found, prompt the user to select which versions of it to export
                    if player:
                        selected_versions = PromptPlayerVersions(duplicates)
                        if "skip" in selected_versions:
                            # TODO: Instead of using the prompt, add all of the player versions to the list
                            break
                        # Add the selected player and its duplicates to the list of selected players
                        selected_player_addresses.extend(selected_versions)

                # Convert selected_player_addresses from hexadecimal to integer
                for i in range(len(selected_player_addresses)):
                    try:
                        selected_player_addresses[i] = int(
                            selected_player_addresses[i], 16
                        )
                    except Exception:
                        continue

            # Run the player_list with the selected export options & print a success message
            exporter.run(
                export=True,
                export_selections=export_selections,
                only_include_addresses=selected_player_addresses,
            )
            print("\n[green]Successfully exported players...[/green]\n")

        case _:
            print("\n[red]Invalid choice! Please select a valid option.[/red]")

    # Wait for user input before continuing
    input("\nPress Enter to continue...")
