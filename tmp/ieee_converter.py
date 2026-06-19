import re

filepath = "/Users/premkumartatapudi/Desktop/ScholarMasterEngine/project_report.tex"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Extract the references block
bib_match = re.search(r'\\begin\{thebibliography\}\{99\}(.*?)\\end\{thebibliography\}', content, re.DOTALL)
if not bib_match:
    print("Could not find the bibliography block.")
    exit()

bib_block = bib_match.group(1)

# Regex to split into individual bibitem strings
# A bibitem starts with \bibitem{key} and continues until the next \bibitem
items = re.split(r'\\bibitem\{', bib_block)
items = [item.strip() for item in items if item.strip()]

print(f"Total parsed items: {len(items)}")

# Let's map each key and parse its details
converted_items = []

for item in items:
    # Split key and text
    key_match = re.match(r'^([^}]+)\}(.*)$', item, re.DOTALL)
    if not key_match:
        print(f"Error parsing item: {item[:100]}...")
        continue
    
    key = key_match.group(1).strip()
    raw_text = key_match.group(2).strip()
    
    # We want to reformat raw_text into IEEE style
    # Let's print out the raw details to help us map them
    print("--- KEY:", key)
    print("RAW:", raw_text)
    print()
