import json
import os

from rich import print

from actions.import_sync_file import ImportSyncFile
from actions.load_import_file import LoadImportFile
from ui.prompts import (
    PromptExportPlayerSelection,
    PromptImportFile,
    PromptItemOptions,
    PromptPlayerVersions,
    PromptPresetCreation,
    PromptPresetUsage,
    PromptSpecificExportPlayers,
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
            import_file_path = PromptImportFile()
            if not import_file_path:
                input("\nPress Enter to continue...")
                return

            try:
                # Load the import file and get the data
                import_handler = LoadImportFile(import_file_path)
                import_data = import_handler.load_file()

                # Run the exporter to initialize the player list, then run the importer with the loaded data
                exporter.run()

                # Run the importer with the loaded data
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
                only_export_selected = True
                import_file_path = None
                selected_player_names = None
                selected_player_addresses = []

                # Run the exporter first to initialize the player list & find versions
                exporter.run()
                exporter.find_versions()

                # Check the user's decision on how to specify players
                match specify_players_choice:
                    case "specific_versions":
                        # Prompt the user for the import file path and the specific player versions to export
                        import_file_path = PromptImportFile()
                        selected_player_names = PromptSpecificExportPlayers(
                            import_file_path
                        )

                        # Prompt the user to select which versions of each player to export
                        for player_name in selected_player_names:
                            player, versions = exporter.find_player_by_name(player_name)
                            if player:
                                selected_versions = PromptPlayerVersions(versions)
                                selected_player_addresses.extend(selected_versions)

                    case "all_versions":
                        # Prompt the user for the import file path and the specific player versions to export
                        import_file_path = PromptImportFile()
                        selected_player_names = PromptSpecificExportPlayers(
                            import_file_path
                        )

                        # If the user wants to export all versions of the players, add all of them to the list
                        for player_name in selected_player_names:
                            _, versions = exporter.find_player_by_name(player_name)
                            if versions:
                                selected_player_addresses.extend(
                                    list(versions.values())
                                )

                    case "full_list":
                        # If the user wants to export all players from the player list, set the flag to false
                        only_export_selected = False

                # Convert selected_player_addresses from hexadec
                # imal to integer
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
                only_include_addresses=(
                    selected_player_addresses if only_export_selected else None
                ),
            )
            print("\n[green]Successfully exported players...[/green]\n")

        case _:
            print("\n[red]Invalid choice! Please select a valid option.[/red]")

    # Wait for user input before continuing
    input("\nPress Enter to continue...")
