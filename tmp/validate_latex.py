import re
import sys
import os

filepath = "/Users/premkumartatapudi/Desktop/ScholarMasterEngine/project_report.tex"

if not os.path.exists(filepath):
    print(f"Error: {filepath} does not exist.")
    sys.exit(1)

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

lines = content.splitlines()

errors = []

# 1. Check for balanced braces
stack = []
for idx, char in enumerate(content):
    if char == '{':
        # Check if escaped \{
        if idx > 0 and content[idx-1] == '\\':
            continue
        stack.append(idx)
    elif char == '}':
        if idx > 0 and content[idx-1] == '\\':
            continue
        if len(stack) == 0:
            # Find line number
            line_no = content[:idx].count('\n') + 1
            errors.append(f"Line {line_no}: Mismatched closing brace '}}'")
        else:
            stack.pop()

for idx in stack:
    line_no = content[:idx].count('\n') + 1
    errors.append(f"Line {line_no}: Unclosed opening brace '{{'")

# 2. Check for balanced \begin and \end environments
env_stack = []
begin_matches = re.finditer(r'\\begin\{([a-zA-Z*]+)\}', content)
end_matches = re.finditer(r'\\end\{([a-zA-Z*]+)\}', content)

envs = []
for m in begin_matches:
    envs.append((m.start(), "begin", m.group(1)))
for m in end_matches:
    envs.append((m.start(), "end", m.group(1)))

envs.sort(key=lambda x: x[0])

for pos, type_, name in envs:
    line_no = content[:pos].count('\n') + 1
    if type_ == "begin":
        env_stack.append((name, line_no))
    else:
        if len(env_stack) == 0:
            errors.append(f"Line {line_no}: \\end{{{name}}} without matching \\begin")
        else:
            expected_name, begin_line = env_stack.pop()
            if expected_name != name:
                errors.append(f"Line {line_no}: \\end{{{name}}} does not match \\begin{{{expected_name}}} on line {begin_line}")

for name, line_no in env_stack:
    errors.append(f"Line {line_no}: \\begin{{{name}}} has no matching \\end")

# 3. Check for unescaped characters in text
# E.g. unescaped & outside of tables or matrices (align, tabular, array)
# Or unescaped _ outside of math mode
in_math = False
in_table = False
in_comment = False

for line_idx, line in enumerate(lines):
    line_no = line_idx + 1
    
    # Simple check for tabular/align to track table state
    if "\\begin{tabular}" in line or "\\begin{array}" in line or "\\begin{align}" in line:
        in_table = True
    if "\\end{tabular}" in line or "\\end{array}" in line or "\\end{align}" in line:
        in_table = False
        
    # Check for unescaped & when not in table/align
    if not in_table:
        # Check if there is an unescaped &
        # & is escaped as \&
        # We need to find & not preceded by \
        matches = re.finditer(r'(?<!\\)&', line)
        for m in matches:
            errors.append(f"Line {line_no}: Possible unescaped '&' found outside tabular/align environment.")

    # Check for unescaped _ outside math mode
    # Math mode can be $...$ or \[...\] or \(...\)
    # This is a basic scanner
    escaped = False
    for char_idx, char in enumerate(line):
        if char == '%':
            if char_idx == 0 or line[char_idx-1] != '\\':
                break # Comment starts, ignore rest of line
        if char == '$':
            if char_idx == 0 or line[char_idx-1] != '\\':
                in_math = not in_math
        if char == '_' and not in_math:
            if char_idx == 0 or line[char_idx-1] != '\\':
                errors.append(f"Line {line_no}: Possible unescaped '_' at column {char_idx+1}")

if errors:
    print(f"Validation failed with {len(errors)} issues:")
    for err in errors:
        print(f" - {err}")
else:
    print("LaTeX validation passed successfully! No syntax errors or unescaped characters detected.")
