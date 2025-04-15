import threading
import time

import pymem
from dribble import (ConvertToGameValue, Game, GetCodeFromString,
                     conversion_list, offsets)
from dribble.memory import BuildPlayer, WriteBinaryBytes, WriteInteger
from nicegui import ui

# -------- GUI SETUP --------

# Global variables
game = None
last_address = None
latest_player = None
is_updating_ui = False
live_player_loading = False
integer_only_categories = ["Attributes", "Badges", "Tendencies"]

# Inputs for the UI
vital_inputs = {}
attribute_inputs = {}
badge_inputs = {}
tendency_inputs = {}
signature_inputs = {}
hotzone_inputs = {}
gear_inputs = {}
accessory_inputs = {}

# -------- UI LAYOUT --------

with ui.header().classes(replace="row items-center") as header:
    # ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
    with ui.tabs() as tabs:
        ui.tab("Vitals")
        ui.tab("Attributes")
        ui.tab("Badges")
        ui.tab("Tendencies")
        ui.tab("Hotzones")
        ui.tab("Signature")
        ui.tab("Gear")
        ui.tab("Accessories")

with ui.footer(value=False) as footer:
    ui.button(
        "Discord", on_click=lambda: ui.open("https://discord.gg/JV3H5xty34")
    ).props("flat color=white")

with ui.left_drawer().classes("bg-blue-100 p-4") as left_drawer:
    ui.label("Potion Tasks").classes("text-lg font-bold mb-2")
    ui.button("Load Player", on_click=lambda: UpdateHoverPlayer())

with ui.page_sticky(position="bottom-right", x_offset=20, y_offset=20):
    ui.button(on_click=footer.toggle, icon="contact_support").props("fab")

with ui.tab_panels(tabs, value="Vitals").classes("w-full"):
    with ui.tab_panel("Vitals"):
        label_vitals = ui.label("No player selected").classes("text-2xl")

        # Create a container for the grid layout that spans full width
        with ui.grid(columns=4).classes("gap-4 w-full"):  # Add 'w-full' here
            for vital in offsets["Vitals"]:
                vital_name = vital["name"]
                vital_options = conversion_list.get(vital_name, {})
                # Check if there are options for the signature, otherwise use a default range
                if vital_options:
                    select_element = ui.select(
                        label=vital_name,
                        options=list(vital_options.values()),
                        with_input=True,
                    ).classes("w-full")
                else:
                    input_element = ui.input(
                        label=vital_name,
                        type="number",
                        min=0,
                    ).classes("w-full")
                # Add the select element to the global dictionary
                vital_inputs[vital_name] = select_element

    with ui.tab_panel("Attributes"):
        label_attributes = ui.label("No player selected").classes("text-2xl")

        # Controls to adjust all attributes
        with ui.row().classes("my-4"):
            ui.button("Set All to 99", on_click=lambda: SetAllAttributes(99))
            ui.button("+5 All", on_click=lambda: AdjustAllAttributes(5))
            ui.button("-5 All", on_click=lambda: AdjustAllAttributes(-5))

        # Attribute input grid
        with ui.grid(columns=4).classes("gap-4 w-full"):
            for attribute in offsets["Attributes"]:
                attribute_name = attribute["name"]
                select_element = ui.select(
                    label=attribute_name,
                    options=[i for i in range(25, 111)],
                    with_input=True,
                ).classes("w-full")
                attribute_inputs[attribute_name] = select_element

    with ui.tab_panel("Badges"):
        label_badges = ui.label("No player selected").classes("text-2xl")

        # Badge input grid
        with ui.grid(columns=4).classes("gap-4 w-full"):
            for badge in offsets["Badges"]:
                badge_name = badge["name"]
                select_element = ui.select(
                    label=badge_name,
                    options=[i for i in range(0, 6)],
                ).classes("w-full")
                badge_inputs[badge_name] = select_element

    with ui.tab_panel("Tendencies"):
        label_tendencies = ui.label("No player selected").classes("text-2xl")

        # Tendency input grid
        with ui.grid(columns=4).classes("gap-4 w-full"):
            for tendency in offsets["Tendencies"]:
                tendency_name = tendency["name"]
                select_element = ui.select(
                    label=tendency_name,
                    options=[i for i in range(0, 101)],
                    with_input=True,
                ).classes("w-full")
                tendency_inputs[tendency_name] = select_element

    with ui.tab_panel("Hotzones"):
        label_hotzones = ui.label("No player selected").classes("text-2xl")

        # Create a container for the grid layout that spans full width
        with ui.grid(columns=4).classes("gap-4 w-full"):  # Add 'w-full' here
            for hotzone in offsets["Hotzones"]:
                hotzone_name = hotzone["name"]
                hotzone_options = conversion_list.get(hotzone_name, {})
                # Check if there are options for the signature, otherwise use a default range
                if hotzone_options:
                    select_element = ui.select(
                        label=hotzone_name,
                        options=list(hotzone_options.values()),
                        with_input=True,
                    ).classes("w-full")
                # Add the select element to the global dictionary
                hotzone_inputs[hotzone_name] = select_element

    with ui.tab_panel("Signature"):
        label_signature = ui.label("No player selected").classes("text-2xl")

        # Create a container for the grid layout that spans full width
        with ui.grid(columns=4).classes("gap-4 w-full"):  # Add 'w-full' here
            for signature in offsets["Signatures"]:
                signature_name = signature["name"]
                signature_options = conversion_list.get(signature_name, {})
                # Check if there are options for the signature, otherwise use a default range
                if signature_options:
                    select_element = ui.select(
                        label=signature_name,
                        options=list(signature_options.values()),
                        with_input=True,
                    ).classes("w-full")
                else:
                    select_element = ui.select(
                        label=signature["name"],
                        options=[i for i in range(0, 101)],
                    ).classes("w-full")
                # Add the select element to the global dictionary
                signature_inputs[signature_name] = select_element

    with ui.tab_panel("Gear"):
        label_gear = ui.label("No player selected").classes("text-2xl")

        # Create a container for the grid layout that spans full width
        with ui.grid(columns=4).classes("gap-4 w-full"):  # Add 'w-full' here
            for gear in offsets["Gear"]:
                gear_name = gear["name"]
                gear_options = conversion_list.get(gear_name, {})
                # Check if there are options for the signature, otherwise use a default range
                if gear_options:
                    select_element = ui.select(
                        label=gear_name,
                        options=list(gear_options.values()),
                        with_input=True,
                    ).classes("w-full")
                # Add the select element to the global dictionary
                gear_inputs[gear_name] = select_element

    with ui.tab_panel("Accessories"):
        label_accessories = ui.label("No player selected").classes("text-2xl")

        # Create a container for the grid layout that spans full width
        with ui.grid(columns=4).classes("gap-4 w-full"):  # Add 'w-full' here
            for accessory in offsets["Accessories"]:
                accessory_name = accessory["name"]
                accessory_options = conversion_list.get(accessory_name, {})
                # Check if there are options for the signature, otherwise use a default range
                if accessory_options:
                    select_element = ui.select(
                        label=accessory_name,
                        options=list(accessory_options.values()),
                        with_input=True,
                    ).classes("w-full")
                # Add the select element to the global dictionary
                accessory_inputs[accessory_name] = select_element

# -------- UI UPDATE FUNCTIONS --------


def UpdatePlayerTabs(game, player):
    """Update UI components for each tab based on the given player object."""
    global is_updating_ui
    global latest_player
    is_updating_ui = True
    latest_player = player
    try:
        # Initialize the player's full name and set the label text
        full_name = f"{player.vitals['First Name']} {player.vitals['Last Name']}"

        # Update the vitals tab
        label_vitals.set_text(f"{full_name}'s Vitals")
        for name, input_field in vital_inputs.items():
            value = player.vitals.get(name, 0)
            input_field.value = value
            input_field.on_value_change(CreateValueHandler("Vitals", name))

        # Update the Attributes tab
        label_attributes.set_text(f"{full_name}'s Attributes")
        for name, input_field in attribute_inputs.items():
            value = player.attributes.get(name, 25)
            input_field.value = value
            input_field.on_value_change(CreateValueHandler("Attributes", name))

        # Update the Badges tab
        label_badges.set_text(f"{full_name}'s Badges")
        for name, input_field in badge_inputs.items():
            value = player.badges.get(name, 0)
            input_field.value = value
            input_field.on_value_change(CreateValueHandler("Badges", name))

        # Update the Tendencies tab
        label_tendencies.set_text(f"{full_name}'s Tendencies")
        for name, input_field in tendency_inputs.items():
            value = player.tendencies.get(name, 0)
            input_field.value = value
            input_field.on_value_change(CreateValueHandler("Tendencies", name))

        # Update the Signatures tab
        label_signature.set_text(f"{full_name}'s Signatures")
        for name, input_field in signature_inputs.items():
            value = player.signatures.get(name, 0)
            input_field.value = value
            input_field.on_value_change(CreateValueHandler("Signatures", name))

        # Update the Hotzones tab
        label_hotzones.set_text(f"{full_name}'s Hotzones")
        for name, input_field in hotzone_inputs.items():
            value = player.hotzones.get(name, 0)
            input_field.value = value
            input_field.on_value_change(CreateValueHandler("Hotzones", name))

        # Update the Gear tab
        label_gear.set_text(f"{full_name}'s Gear")
        for name, input_field in gear_inputs.items():
            value = player.gear.get(name, 0)
            input_field.value = value
            input_field.on_value_change(CreateValueHandler("Gear", name))

        # Update the Accessories tab
        label_accessories.set_text(f"{full_name}'s Accessories")
        for name, input_field in accessory_inputs.items():
            value = player.accessories.get(name, 0)
            input_field.value = value
            input_field.on_value_change(CreateValueHandler("Accessories", name))

    except Exception as e:
        print(f"[UI Update Error] {e}")
    finally:
        is_updating_ui = False


def OnItemChange(game, player, category, name, new_value):
    """Handle changes to UI items and update the player in memory."""
    global is_updating_ui
    global integer_only_categories
    try:
        # Prevent recursive updates
        if is_updating_ui:
            return
        # Convert string representations if needed
        if name in conversion_list and category not in integer_only_categories:
            new_value = GetCodeFromString(name, new_value)
        # Find the offset for the item
        item_category = offsets.get(category)
        item_offset = None
        item_length = None
        item_start_bit = None
        for item in item_category:
            if item["name"] == name:
                item_offset = item.get("offset")
                item_length = item.get("length")
                item_start_bit = item.get("startBit")
                break
        # If the offset is not found in the category, check the offsets dictionary
        if item_offset is None:
            raise ValueError(f"No offset found for {category} > {name}")

        item_address = player.address + item_offset

        if category == "Attributes":
            game_value = ConvertToGameValue(new_value, item_length)
            WriteBinaryBytes(game, item_address, item_length, game_value)
        else:
            WriteInteger(game, item_address, item_length, item_start_bit, new_value)

    except Exception as e:
        line_no = e.__traceback__.tb_lineno
        print(f"[Item Change Error] {e} @ line {line_no}")


def SetAllAttributes(value: int):
    for select in attribute_inputs.values():
        select.value = value


def AdjustAllAttributes(amount: int):
    for select in attribute_inputs.values():
        current = select.value or 25
        new_value = max(25, min(110, current + amount))
        select.value = new_value


def SetLivePlayerLoading(value: bool):
    global live_player_loading
    live_player_loading = value
    if value:
        ui.notify("Live Player Loading Enabled")
    else:
        ui.notify("Live Player Loading Disabled")


def UpdateHoverPlayer():
    global last_address
    if not game:
        ui.notify("Game not loaded")
        return
    hover_player = GetHoverPlayer(game)
    if hover_player and hover_player.address != last_address:
        last_address = hover_player.address
        UpdatePlayerTabs(game, hover_player)


def CreateValueHandler(category, name):
    global is_updating_ui

    def handler(e):
        if is_updating_ui:
            return
        if latest_player:
            OnItemChange(game, latest_player, category, name, e.value)

    return handler


# -------- POTION LOGIC --------


def GetHoverPlayer(game):
    try:
        base_cursor_address = 0x1E4CB3A8
        cursor_offset = 0x1480

        cursor_base_address = game.memory.read_bytes(
            game.base_address + base_cursor_address, 8
        )
        cursor_base_address = int.from_bytes(cursor_base_address, byteorder="little")

        hover_player_address = game.memory.read_bytes(
            cursor_base_address + cursor_offset, 8
        )
        hover_player_address = int.from_bytes(hover_player_address, byteorder="little")

        return BuildPlayer(game, None, hover_player_address)
    except:
        return None


def SyncWorker():
    try:
        # Initialize global variables
        global game
        global last_address
        global live_player_loading

        # Initialize the game object
        game = Game()
        if not game.module:
            print("[red]Failed to attach to NBA2K25.exe[/red]")
            return

        while live_player_loading:
            time.sleep(0.25)
            UpdateHoverPlayer()

    except pymem.exception.ProcessNotFound:
        print("[red]NBA2K25.exe not found[/red]")
    except pymem.exception.MemoryReadError:
        print("[red]Memory read error. Try running as administrator[/red]")
    except Exception as e:
        print(f"[red]Unexpected error:[/red] {e}")


# -------- RUN NICEGUI & BACKGROUND THREAD --------

if __name__ in {"__main__", "__mp_main__"}:
    threading.Thread(target=SyncWorker, daemon=True).start()
    ui.run(favicon="🍷", title="Potion Editor")
