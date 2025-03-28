import pymem
import pymem.process

from rich import print
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.emoji import Emoji

from core import offsets, GetOffset, Game, ConvertToGameValue
from memory import BuildPlayer, WriteBinaryBytes
from actions import BuildPlayerList, ReplacePlayer, TradePlayer

PLAYER_LIST_SIZE = 10000

def main():
    
    console = Console()
    
    try:
        
        # Display a welcome & donation message
        console.print(
            Panel(
                ":smiley: Enjoying the mod? Consider supporting the developer with a donation by clicking [bold green][underline][link=https://ko-fi.com/doublesync]here[/link][/underline][/bold green].",
                title="[bold blue]Sync2K[/bold blue]",
                subtitle="Created by [link=https://github.com/doublesync/]doublesync[/link]",
            )
        )
        
        # Define choices with emojis
        choices = {
            "1": "📥 Import Players",
            "2": "📤 Export Players",
            "3": "🔄 Trade Players",
            "4": "📦 Replace Players",
            "5": "📚 Mode Tutorials"
        }

        # Display menu using rich
        console.print("[bold cyan]Choose a mode:[/bold cyan]")
        for key, value in choices.items():
            console.print(f"[bold yellow]{key})[/bold yellow] {value}")
        
        # Get user input
        choice = Prompt.ask("[bold green]Enter the number of your choice[/bold green]", choices=choices.keys())

        console.print(f"[bold magenta]You selected: {choices[choice]}[/bold magenta]")
                        
        # # Initialize the game connection
        # game = Game()

        # # Check if the game module is loaded
        # if game.module:

            # ########################################################### #
            # DUMP PLAYER DATA BASED ON A USER SEARCH FOR A PLAYER NAME   #
            # ########################################################### #

            # Build a list of players from the game memory
            # list_builder = BuildPlayerList(game, PLAYER_LIST_SIZE)
            # list_builder.run(export=False, singular=False)
            # # duplicates = list_builder.find_duplicates()
            # search = input("\nEnter a player name to search for: ")
            # player, duplicates = list_builder.find_player_by_name(search)
            # if player:
            #     # Print the player details and any duplicates found
            #     # with open(f"{player}.json", "w") as f:
            #     #     f.write(player.to_json())
            #     # Write new number to driving layup address
            #     import time
            #     offset_data = GetOffset("Attributes", "Driving Layup")
            #     for i in range(25, 111):
            #         game_value = ConvertToGameValue(i, offset_data["length"])
            #         WriteBinaryBytes(game, player.address + offset_data["offset"], offset_data["length"], game_value)
            #         time.sleep(0.2)
            #         rprint(f"Success! [green]Successfully wrote {i} to {player}'s driving layup.[/green]")
            # else:
            #     print("\nThere was no player found with that name.")            

            # ########################################################### #
            # FINDING DUPLICATES BASED ON A USER SEARCH FOR A PLAYER NAME #
            # ########################################################### #

            # while True:
            #     # Search for player, it's first instance, and all duplicates by name
            #     search = input("\nEnter a player name to search for: ")
            #     player, duplicates = list_builder.find_player_by_name(search)
            #     # Print the player details and any duplicates found
            #     if player and duplicates:
            #             print(f"\nFound {len(duplicates)} instance(s) of {search.upper()}:\n")
            #             for team, address in duplicates.items():
            #                 print(f"- ({team}) {address}")
            #         else:
            #             print(f"\nThere were no duplicates found for this player.")
            #     else:
            #         print("\nThere was no player found with that name.")

            # with open("duplicates.json", "w") as f:
            #     import json
            #     json.dump(duplicates, f, indent=4)

        # else:
        #     print("Sync2K had a problem while attaching to NBA2K25.exe.")

    except pymem.exception.ProcessNotFound:
        print("Sync2K cannot find the NBA2K25.exe process. Make sure the game is running.")
    except pymem.exception.MemoryReadError:
        print("Sync2K cannot read memory. Make sure you have the necessary permissions.")
    except Exception as e:
        print(f"Unexpected error: {e}")

# Run the main function if this script is executed directly
if __name__ == "__main__":
    main()