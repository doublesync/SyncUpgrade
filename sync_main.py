import os

from dribble.memory import GetOffsets
from dribble.models import Game
from pymem.exception import MemoryReadError, ProcessNotFound
from rich import print
from rich.console import Console
from rich.panel import Panel

from actions.build_player_list import BuildPlayerList
from ui import PromptPlayerListSize, run_cli

# Setup rich console
console = Console()


def ClearConsole():
    """Clear the console window."""
    os.system("cls" if os.name == "nt" else "clear")


def StartProgram():
    """Main logic to run Sync2K."""
    try:

        # Title and donation panel
        header = Panel.fit(
            "[bold magenta]Sync2K - NBA2K Automation Tool[/bold magenta]\n"
            """
            [green]Support development:[/green] \n
            [link=https://ko-fi.com/doublesync]Donate[/link]
            """,
            title="Welcome",
            border_style="cyan",
        )
        console.print(header)

        # Initialize offsets
        try:
            GetOffsets("resources/offsets.json")
        except ValueError as e:
            print(f"\n[red]Failed to load offsets: {e}[/red]\n")
            return

        # Ask how many players to show
        player_list_size = PromptPlayerListSize()

        # # Initialize the game connection
        game = Game()
        exporter = BuildPlayerList(game, player_list_size)
        exporter.run()

        # Check if the game module is valid
        if not game.module:
            print("\n[red]Could not attach to the process.[/red]\n")
            return

        # Game loop
        while True:
            run_cli(game, exporter)

    except ProcessNotFound:
        print("\n[red]Could not find the process.[/red]\n")
    except MemoryReadError:
        print("\n[red]Could not read memory.[/red]\n")
    except KeyboardInterrupt:
        print("\n[cyan]Sync2K terminated by user.[/cyan]\n")
    except Exception as e:
        print(f"\n[red]An unexpected error occurred: {e}[/red]\n")
        raise
    finally:
        input("\nPress Enter to exit...\n")


if __name__ == "__main__":
    StartProgram()
