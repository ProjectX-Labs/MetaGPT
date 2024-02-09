# main_script.py
from pathlib import Path
import json
from ..api.utils.utils_generate import read_user_contents

# The path to the directory you want to read
directory_path = Path("workspace/employee_shift_manager")

# Use the function to read the contents
contents = read_user_contents(directory_path)

# Define the output JSON file name
output_file_name = "code1.json"  # Change the number as needed

# Write the contents to the JSON file
with open(output_file_name, "w") as json_file:
    json.dump(contents, json_file, indent=4)

print(f"Contents written to {output_file_name}")
