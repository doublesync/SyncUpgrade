from dribble import conversion_list

with open("strings_list.txt", "w") as file:
    for item in conversion_list:
        file.write(f"\n\n### {item}\n\n")  # Write the outer item
        for item_code, item_string in conversion_list[item].items():
            file.write(f"`{item_string}` ")  # Write each nested item string

# Move the file to the base directory
