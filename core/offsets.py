import json    

# Function to fetch offsets from a JSON file
def FetchOffsets():
    offsets_file = open("resources/offsets.json", "r")
    offsets_dict = json.load(offsets_file)
    return offsets_dict

# Function to format the offsets to hexadecimal
def FormatOffsets(offsets_dict):
    try:
        formatted_offsets = {}

        # Traverse through the dictionary
        for category, data in offsets_dict.items():
            # Check if data is a dictionary (category like "Base")
            if isinstance(data, dict):
                formatted_offsets[category] = {}
                for key, value in data.items():
                    # If the value is a hex string starting with '0x'
                    if isinstance(value, str) and value.startswith("0x"):
                        try:
                            formatted_offsets[category][key] = int(value, 16)
                        except ValueError:
                            print(f"Error converting {key}: {value}")
                            formatted_offsets[category][key] = value
            else:
                # The rest of the categories are lists of dictionaries
                formatted_offsets[category] = []
                for offset in data:
                    offset_value = offset.get("offset", "")
                    if isinstance(offset_value, str) and offset_value.startswith("0x"):
                        try:
                            offset["offset"] = int(offset_value, 16)
                        except ValueError:
                            print(f"Error converting Offset: {offset_value}")
                            offset["offset"] = offset_value  # Keep original if conversion fails
                    formatted_offsets[category].append(offset)

        return formatted_offsets

    except Exception as e:
        print(f"Unexpected error formatting offsets: {e}")
        return None

# Fetch offsets from the JSON file and store them in variables
offsets = FormatOffsets(FetchOffsets())