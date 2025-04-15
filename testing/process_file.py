import json

import pyperclip


# Function to read the text file and process it
def process_file(file_path):
    name_dict = {}

    # Open the file and read line by line
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            try:
                # Split the line at the semicolon
                number, name = line.strip().split(":")
                # Convert number to integer and add the pair to the dictionary
                name_dict[int(number)] = name
            except:
                pass

    # Copy the dictionary to clipboard in JSON format
    # Copy in one-line format for clipboard compatibility
    pyperclip.copy(name_dict)
    return name_dict


# Path to your text file
file_path = "testing/names.txt"

# Process the file and get the dictionary
name_dict = process_file(file_path)
