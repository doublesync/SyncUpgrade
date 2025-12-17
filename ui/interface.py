import sys

from rich.console import Console
from rich.prompt import Prompt

from actions.import_sync_file import ImportSyncFile
from actions.load_import_file import LoadImportFile
from ui.prompts import PromptImportFile

console = Console()


def run_cli(game, exporter):
    """Runs the Sync2K CLI interface."""

    while True:
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
            line_no = getattr(e, "__traceback__", None).tb_lineno if getattr(e, "__traceback__", None) else "unknown"
            print(f"\n[red]Error importing file at line @{line_no}: {e}.[/red]")
