import os
import pymem
from rich import print
from rich.panel import Panel
from rich.console import Console

from dribble.models import Game
from dribble.memory import GetOffsets
from ui import run_cli
from ui.prompts import PromptPlayerListSize
from actions import BuildPlayerList

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
            "[green]Support development:[/green] [link=https://ko-fi.com/doublesync]https://ko-fi.com/doublesync[/link]",
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
            print("\n[red]Sync2K had a problem while attaching to NBA2K25.exe.[/red]\n")
            return

        # Game loop
        while True:
            run_cli(game, exporter)

    except pymem.exception.ProcessNotFound:
        print(
            "\n[red]Sync2K cannot find the NBA2K25.exe process. Make sure the game is running.[/red]\n"
        )
    except pymem.exception.MemoryReadError:
        print(
            "\n[red]Sync2K cannot read memory. Make sure you have the necessary permissions.[/red]\n"
        )
    except KeyboardInterrupt:
        print("\n[cyan]Sync2K terminated by user.[/cyan]\n")
    except Exception as e:
        print(
            f"\n[red]An unexpected error occurred @ line {e.__traceback__.tb_lineno}:[/red] {e}\n"
        )
    finally:
        input("\nPress Enter to exit...\n")


if __name__ == "__main__":
    StartProgram()
