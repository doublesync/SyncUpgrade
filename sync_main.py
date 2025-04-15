import os

import pymem
from dribble.memory import GetOffsets
from dribble.models import Game
from rich import print
from rich.console import Console
from rich.panel import Panel

from actions import BuildPlayerList
from ui import run_cli
from ui.prompts import PromptPlayerListSize

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
        GetOffsets("resources/offsets.json")

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

    except pymem.exception.ProcessNotFound:
        print(
            "\n[red]Could not find the process.[/red]\n"
        )
    except pymem.exception.MemoryReadError:
        print(
            "\n[red]Could not read memory.[/red]\n"
        )
    except KeyboardInterrupt:
        print("\n[cyan]Sync2K terminated by user.[/cyan]\n")
    except Exception as e:
        print(
            f"\n[red]An unexpected error occurred: {e}[/red]\n"
        )
    finally:
        input("\nPress Enter to exit...\n")


if __name__ == "__main__":
    StartProgram()
