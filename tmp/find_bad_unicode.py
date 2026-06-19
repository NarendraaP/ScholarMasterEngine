import unicodedata

filepath = "/Users/premkumartatapudi/Desktop/ScholarMasterEngine/project_report.tex"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

print("Scanning for non-standard homoglyphs in project_report.tex...")
lines = content.split('\n')
suspect_count = 0

for line_num, line in enumerate(lines, 1):
    for char_num, char in enumerate(line, 1):
        # We want to identify characters that are Greek or Cyrillic but placed within normal words.
        # Let's inspect any character whose Unicode block is Greek or Cyrillic
        name = unicodedata.name(char, "")
        if "GREEK" in name or "CYRILLIC" in name:
            # Skip standard LaTeX math symbols or comments
            # In LaTeX, Greek letters are usually written as commands like \alpha, \beta.
            # If they are raw characters, they are suspect.
            print(f"Line {line_num}, Char {char_num}: Character '{char}' (U+{ord(char):04X}) - Name: {name}")
            print(f"  Context: ... {line[max(0, char_num-15):char_num+15]} ...")
            suspect_count += 1

print(f"\nTotal suspect characters found: {suspect_count}")
