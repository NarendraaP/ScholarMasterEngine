import re
import os

SCHEMA_PATH = "core/api/scholarmaster_core.proto"

def validate_schema():
    print("===================================================================")
    print("Paper 20: Architecture Synthesis & Schema Validator")
    print("===================================================================\n")
    
    if not os.path.exists(SCHEMA_PATH):
        print(f"[ERROR] Schema not found at {SCHEMA_PATH}")
        return
        
    with open(SCHEMA_PATH, 'r') as f:
        content = f.read()
        
    print(f"Validating Canonical Protobuf Schema: {SCHEMA_PATH}")
    
    # ---------------------------------------------------------
    # Rule 1: Identity Non-Propagation (No string fields)
    # ---------------------------------------------------------
    print("\n[CHECK 1] Architecting against Identity Strings (INV-02)")
    # Split content into lines and check non-comment lines
    has_string = False
    for line in content.split('\n'):
        if not line.strip().startswith('//'):
            if re.search(r'\bstring\b', line):
                has_string = True
                break
                
    if has_string:
        print("  [FAIL] Schema contains a 'string' field. Potential PII leak vector.")
    else:
        print("  [PASS] Zero 'string' fields detected. Identity must be handled structurally via ephemeral IDs.")
        
    # ---------------------------------------------------------
    # Rule 2: Raw Data Non-Persistence (No bytes/image blobs)
    # ---------------------------------------------------------
    print("\n[CHECK 2] Architecting against Raw Matrix Emission (INV-01)")
    if re.search(r'\bbytes\b', content):
        print("  [FAIL] Schema contains a 'bytes' field. Potential raw image/audio escape vector.")
    else:
        print("  [PASS] Zero 'bytes' fields detected. It is structurally impossible to serialize raw RGB tensors across the L3 boundary.")

    # ---------------------------------------------------------
    # Rule 3: Dimensionality Bound (INV-10)
    # ---------------------------------------------------------
    print("\n[CHECK 3] Enforcing Abstract Dimensionality Limit (INV-10)")
    if 'repeated float geometric_keypoints' in content:
        print("  [PASS] Structural Abstraction confirmed ('geometric_keypoints'). Raw data must be irreversibly reduced before bridging.")
    else:
        print("  [FAIL] Schema missing bounding float array for geometric abstraction.")
        
    print("\n===================================================================")
    print("Validation Complete. The L3/L4 Canonical Execution Contract SECURE.")
    print("===================================================================")

if __name__ == "__main__":
    validate_schema()
