import sys
from rich.panel import Panel
from rich.console import Console
from rich.prompt import Prompt
from ui.handlers import handle_choice

console = Console()

def run_cli(game, exporter):
    """Runs the Sync2K CLI interface."""

    # Main menu choices
    choices = {
        "1": "Import Players",
        "2": "Export Players",
        "q": "Quit"
    }

    while True:
        console.print("\n[bold cyan]Choose a mode:[/bold cyan]")
        for key, value in choices.items():
            console.print(f"[bold yellow]{key})[/bold yellow] {value}")

        choice = Prompt.ask("\n[bold green]Enter your choice[/bold green]", choices=list(choices.keys()))

        if choice == "q":
            console.print("\n[cyan]Thanks for using Sync2K![/cyan]\n")
            sys.exit()

        handle_choice(game, exporter, choice)