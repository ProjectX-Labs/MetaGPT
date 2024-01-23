
from pathlib import Path
from metagpt.config import CONFIG
from metagpt.const import BEACHHEAD_ROOT



def read_beachhead_contents():
    beachhead_path = BEACHHEAD_ROOT
    print(beachhead_path)
    contents = {}
    for file_path in beachhead_path.glob("**/*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(beachhead_path)
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    contents[str(relative_path)] = file.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, "r", encoding="ISO-8859-1") as file:
                        contents[str(relative_path)] = file.read()
                except Exception as e:
                    contents[str(relative_path)] = f"Error reading file: {e}"
    return contents

# Example usage
if __name__ == "__main__":
    contents = read_beachhead_contents()
    print(contents)
