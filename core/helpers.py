import re

# Function to check if a string contains only valid characters (alphanumeric, hyphens, apostrophes, and spaces)
def HasValidCharacters(text):
    return bool(re.fullmatch(r"[a-zA-Z0-9-'. ]+", text))

# Function to convert an integert o a memory-friendly value
# Sidenote (1/2): We only need to use these functions on attributes.
# Sidenote (2/2): They are some sort of 0-255 slider range.
def ConvertToGameValue(integer):
    return bin((integer - 25) * 3) # Scale and convert to binary

# Function to convert a memory-friendly value to a user-readble integer
def ConvertToReadableValue(integer):
    return (integer // 3) + 25