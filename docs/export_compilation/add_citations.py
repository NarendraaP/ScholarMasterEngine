import os
import re

# Logic:
# 1. Iterate P1 to P19.
# 2. Check if paper{N}_corrected.tex exists.
# 3. Read file.
# 4. Check for existing P20/P21 bib entries.
# 5. Append if missing.
# 6. Check for existing P20/P21 citations in text.
# 7. Insert standard sentence in Introduction if missing.

BIB_ENTRIES = r"""
\bibitem{P20} N. Babu P., "Unified Reference Model for ScholarMaster Architecture," \textit{ScholarMaster Series}, 2026.
\bibitem{P21} N. Babu P., "Formal Foundations of Distributed Trust," \textit{ScholarMaster Series}, 2026.
"""

CITATION_SENTENCE = r" This work is rigorously aligned with the Unified Reference Model \cite{P20} and adheres to the Formal Foundations of Distributed Trust \cite{P21} established for the ScholarMaster architecture."

def process_file(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    original_content = content
    modified = False

    # 1. Add Bibliography Entries
    if "{P20}" not in content and "Unified Reference Model" not in content:
        # Find end of bibliography
        bib_end_match = re.search(r'\\end\{thebibliography\}', content)
        if bib_end_match:
            print(f"Adding bib entries to {os.path.basename(filepath)}")
            insert_pos = bib_end_match.start()
            content = content[:insert_pos] + BIB_ENTRIES + content[insert_pos:]
            modified = True
        else:
            print(f"WARNING: No bibliography found in {os.path.basename(filepath)}")

    # 2. Add Citation to Introduction
    # Check if P20 is cited (simple check for \cite{P20} or \cite{P20,})
    if "\\cite{P20}" not in content:
        # Find Introduction section
        intro_match = re.search(r'\\section\{Introduction\}', content, re.IGNORECASE)
        if intro_match:
            # Find the end of the first paragraph after Introduction
            # We look for the first double newline after the section header
            section_end = intro_match.end()
            # Search for the next blank line (paragraph break)
            para_break = re.search(r'\n\s*\n', content[section_end:])
            
            if para_break:
                insert_pos = section_end + para_break.start()
                # Insert before the newline characters
                print(f"Adding citation sentence to {os.path.basename(filepath)}")
                content = content[:insert_pos] + CITATION_SENTENCE + content[insert_pos:]
                modified = True
            else:
                 # Fallback: if no paragraph break found (unlikely), try to find end of next sentence? 
                 # Or just append to the very end of the section text if short?
                 # Let's try to find the next section
                 next_section = re.search(r'\\section\{', content[section_end:])
                 if next_section:
                     insert_pos = section_end + next_section.start()
                     # Backtrack to find last non-whitespace
                     while insert_pos > section_end and content[insert_pos-1].isspace():
                         insert_pos -= 1
                     print(f"Adding citation sentence (end of section fallback) to {os.path.basename(filepath)}")
                     content = content[:insert_pos] + CITATION_SENTENCE + content[insert_pos:]
                     modified = True
        else:
             print(f"WARNING: No Introduction section found in {os.path.basename(filepath)}")

    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Successfully updated {os.path.basename(filepath)}")
    else:
        print(f"No changes needed for {os.path.basename(filepath)}")

def main():
    base_dir = "/Users/premkumartatapudi/Desktop/ScholarMasterEngine/docs/export_compilation"
    
    # Process P1 to P19
    for i in range(1, 20):
        filename = f"paper{i}_corrected.tex"
        filepath = os.path.join(base_dir, filename)
        
        if os.path.exists(filepath):
            process_file(filepath)
        else:
            print(f"Skipping {filename} (not found)")

if __name__ == "__main__":
    main()
