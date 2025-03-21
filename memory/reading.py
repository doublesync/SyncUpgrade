from core import (
    offsets, 
    Player, 
    HasValidCharacters, 
    ConvertTeamType, 
    GetStringFromCode,
    ConvertToGameValue,
    ConvertToReadableValue
)

# Read the integer value from memory and format it if needed
def ReadInteger(game, address, length, return_readable=False, start_bit=0):
    """
    Reads an integer from memory, optionally extracting a specific bit range.

    :param game: The game memory reader instance.
    :param address: The memory address to read from.
    :param length: The number of bits to read.
    :param return_readable: Whether to format the value for readability.
    :param startBit: The starting bit position (default is 0, meaning full integer).
    :return: The extracted integer value.

    "num_bytes" Explanation:
        - Calculate the number of bytes needed to fully cover the requested bit range.
        - We add startBit because the value might not start at a byte boundary.
        - We add 7 before integer division to round up, ensuring we read enough bytes.
        - Example: For startBit=6 and length=8, we need (6 + 8 + 7) // 8 = 2 bytes,
        because the 8 bits start in the middle of the byte and span two bytes.
    """
    # Calculate the number of bytes needed to store the value
    num_bytes = max((start_bit + length + 7) // 8, 1)
    raw_bytes = game.memory.read_bytes(address, num_bytes)
    integer_value = int.from_bytes(raw_bytes, byteorder='little')

    # Apply the start bit and mask to extract the correct value
    mask = (1 << length) - 1  # Create a mask for the bit length
    integer_value = (integer_value >> start_bit) & mask  # Extract the bits based on startBit and length

    # Format the result if needed
    if return_readable:
        integer_value = ConvertToReadableValue(integer_value)

    # Return the extracted integer value
    return integer_value

# Get the data for the team of a player
def GetTeamData(game, player_address):
    """
    Get the team data for a given player.

    :param game: The game memory reader instance.
    :param player: The Player object for which to retrieve team data.
    :return: A dictionary containing the team data.
    """
    try:
        # Read the team address from the player's data
        team_address = game.memory.read_bytes(player_address + offsets["Base"]["Offset Player Team"], 8) # Dereference the pointer to get the actual team address
        team_address = int.from_bytes(team_address, byteorder='little')

        # Assuming we have a predefined offset for team data, read the team details
        # FYI: "read_bytes" takes byte-size for length, while "ReadInteger" takes bit-size for length
        team_name = game.memory.read_bytes(team_address + offsets["Base"]["Offset Player Team Name"], 24).decode("utf-16-le", errors="ignore").rstrip("\x00")
        team_short_name = game.memory.read_bytes(team_address + offsets["Base"]["Offset Player Team Short Name"], 8).decode("utf-16-le", errors="ignore").rstrip("\x00")
        team_year = ReadInteger(game, team_address + offsets["Base"]["Offset Player Team Year"], 7, return_readable=False, start_bit=3)
        team_type = ReadInteger(game, team_address + offsets["Base"]["Offset Player Team Type"], 5, return_readable=False, start_bit=2)
        team_data = {
            "Key": "",
            "Name": team_name,
            "Short Name": team_short_name,
            "Year": f"{team_year - 1}-{team_year}" if team_year > 0 else "Current",
            "Type": ConvertTeamType(team_type),
        }
        # Set a "key" for the team based on type/year and short name
        if team_data["Type"] == "Normal":
            team_data["Key"] = f"{team_data['Year']} {team_short_name}" 
        else:
            team_data["Key"] = f"{team_data['Type']} {team_short_name}"

    except Exception: # Results in a pymem.exception.MemoryReadError if the player isn't found
        team_data = {
            "Key": "Current FA",
            "Name": "Free Agents",
            "Short Name": "FA",
            "Year": "Current",
            "Type": "Normal"
        }

    return team_data

# Get player data from memory and create a Player object
def BuildPlayer(game, player_id):
    """
    Builds player data from memory and creates a Player object."
    
    :param game: The game memory reader instance.
    :param player_base_address: The base address of the player data.
    :param player_id: The ID of the player to retrieve data for.
    :return: A Player object containing the player's data.
    """ 
    # Calculate Player Base Address: Read 8-bytes because this will be a 64-bit pointer to the player data
    # Note: This should probably only be done once and stored, but for simplicity and centralization, it's done here
    player_base_address = game.memory.read_bytes(game.base_address + offsets["Base"]["Player Base Address"], 8) # Dereference the pointer to get the actual player base address
    player_base_address = int.from_bytes(player_base_address, byteorder='little')

    # Calculate the specific player address
    player_address = player_base_address + offsets["Base"]["Player Offset Length"] * player_id

    # Read player team data (address points to team address, where we can then get team details)
    team_data = GetTeamData(game, player_address)

    # Read player vitals data
    first_name_address = player_address + offsets["Base"]["Offset First Name"]
    last_name_address = player_address + offsets["Base"]["Offset Last Name"]

    # Read the names (assuming they are stored as UTF-16 strings)
    player_vitals = {
        "First Name": game.memory.read_bytes(first_name_address, 40).decode("utf-16-le", errors="ignore").rstrip("\x00"),
        "Last Name": game.memory.read_bytes(last_name_address, 40).decode("utf-16-le", errors="ignore").rstrip("\x00")
    }

    # Check if the first and last names are valid characters
    if (HasValidCharacters(player_vitals["First Name"]) == False 
    or HasValidCharacters(player_vitals["Last Name"]) == False):
        return None  # Skip invalid characters

    # Initialize dictionaries for player attributes, badges, and tendencies
    player_skill_categories = {
        "Vitals": offsets["Vitals"],
        "Attributes": offsets["Attributes"], 
        "Badges": offsets["Badges"], 
        "Tendencies": offsets["Tendencies"],
        "Hotzones": offsets["Hotzones"],
        "Signatures": offsets["Signatures"],
        "Gear": offsets["Gear"]
    }
    player_skills = {
        "Vitals": player_vitals,
        "Attributes": {}, 
        "Badges": {}, 
        "Tendencies": {},
        "Hotzones": {},
        "Signatures": {},
        "Gear": {}
    }

    # Iterate over each skill category and read the data
    for skill_category, category_data in player_skill_categories.items():
        return_readable = True if skill_category == "Attributes" else False
        for item in category_data:
            name = item["name"]
            length = item["length"]
            address = player_address + item["offset"]
            start_bit = item.get("startBit", 0) # Default to 0 if not specified
            value = ReadInteger(game, address, length, start_bit=start_bit, return_readable=return_readable)
            string_repr = None
            # Set the value in the player_skills dictionary, using the string representation if available
            # This is so we can show string representations instead of integer codes in memory exports
            # Attributes, badges, and tendencies are always in integer form, so we don't need to check for them
            if skill_category not in ["Attributes", "Badges", "Tendencies"]:
                string_repr = GetStringFromCode(name, value)
            player_skills[skill_category][name] = string_repr if string_repr else value

    # Create a Player object
    player_object = Player(
        address=player_address,
        team=team_data,
        vitals=player_skills["Vitals"],
        attributes=player_skills["Attributes"],
        badges=player_skills["Badges"],
        tendencies=player_skills["Tendencies"],
        hotzones=player_skills["Hotzones"],
        signatures=player_skills["Signatures"],
        gear=player_skills["Gear"]
    )

    # Return the Player object
    return player_object