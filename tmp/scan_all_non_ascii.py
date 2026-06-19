import unicodedata

filepath = "/Users/premkumartatapudi/Desktop/ScholarMasterEngine/project_report.tex"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

print("Scanning all non-ASCII characters in project_report.tex...")
suspects = set()
for char in content:
    o = ord(char)
    if o > 127:
        suspects.add(char)

for char in sorted(suspects):
    print(f"Char: '{char}' | Code: U+{ord(char):04X} | Name: {unicodedata.name(char, 'UNKNOWN')}")
