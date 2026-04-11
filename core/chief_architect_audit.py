import os
import re

PAPERS_DIR = "docs/papers"
PATTERNS = {
    # INV-A: No Raw Persistence
    "INV-A_VIOLATION": [
        r"store[s]?\s+raw",
        r"save[s]?\s+video",
        r"persist[s]?\s+frames",
        r"database\s+of\s+faces",
        r"retain[s]?\s+images"
    ],
    # INV-B: Governance Non-Bypass
    "INV-B_VIOLATION": [
        r"direct\s+upload",
        r"bypass[es]*\s+governance",
        r"bypassing\s+governance",
        r"directly\s+to\s+cloud",
        r"skipping\s+policy"
    ],
    # INV-C: Fail-Closed
    "INV-C_VIOLATION": [
        r"fail-open",
        r"prioritize[s]?\s+availability",
        r"fail\s+safe\s+open",
        r"continue\s+processing", # dangerous if unchecked
        r"best\s+effort\s+security"
    ],
    # INV-D: Threat Model Alignment (A0-A3 only)
    "INV-D_VIOLATION": [
        r"prevent[s]?\s+physical\s+attack",
        r"defend[s]?\s+against\s+kernel",
        r"guarantee[s]?\s+hardware",
        r"immutable\s+hardware", # unless claiming we DON'T have it
        r"A4\s+adversary", # Check context (should be "excluded")
        r"A5\s+adversary"  # Check context
    ],
    # INV-E: No Capability Drift
    "INV-E_VIOLATION": [
        r"future\s+work.*raw",
        r"enable\s+surveillance",
        r"repurpose\s+for\s+security",
        r"later\s+version"
    ]
}

def scan_papers():
    results = {}
    
    files = [f for f in os.listdir(PAPERS_DIR) if f.startswith("paper") and f.endswith("_corrected.tex")]
    files.sort(key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 999)

    print(f"Scanning {len(files)} papers in {PAPERS_DIR}...\n")
    
    for filename in files:
        filepath = os.path.join(PAPERS_DIR, filename)
        with open(filepath, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            
        file_hits = []
        
        # Check Patterns
        for inv_id, regex_list in PATTERNS.items():
            for regex in regex_list:
                for i, line in enumerate(lines, 1):
                    if line.strip().startswith('%'): continue # Skip comments
                    
                    if re.search(regex, line, re.IGNORECASE):
                        # Filter out "explicitly out of scope" or "does not"
                        if "not" in line.lower() or "no" in line.lower() or "exclude" in line.lower() or "out of scope" in line.lower():
                            continue # Likely a negation, naive check but helpful
                            
                        context = line.strip()[:100]
                        file_hits.append(f"[{inv_id}] L{i}: ...{context}...")

        if file_hits:
            results[filename] = file_hits

    # Report
    if not results:
        print("✅ ALL PAPERS PASSED CHIEF ARCHITECT AUDIT (No gross violations found).")
    else:
        print(f"⚠️  FOUND VIOLATIONS IN {len(results)} PAPERS:\n")
        for fname, hits in results.items():
            print(f"📄 {fname}:")
            for h in hits:
                print(f"  ❌ {h}")
            print("")

if __name__ == "__main__":
    scan_papers()
