import ast
import os

TARGET_FILE = 'modules/master_engine.py'

# Features to check explicitly
STANDARD_FEATURES = {
    'search_face': 'Paper 1: Real Identity',
    'check_compliance': 'Paper 4: Truancy',
    'mark_present': 'Paper 4: Attendance Logging',
    'detect_violence': 'Paper 6: Visual Safety',
    'detect_hand_raise': 'Paper 3: Attention',
}

def verify_integration():
    if not os.path.exists(TARGET_FILE):
        print(f"Error: {TARGET_FILE} not found. Please run this script from the project root.")
        return

    try:
        with open(TARGET_FILE, 'r') as f:
            tree = ast.parse(f.read())
    except Exception as e:
        print(f"Error parsing {TARGET_FILE}: {e}")
        return

    found_calls = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            # Check for direct calls: func()
            if isinstance(node.func, ast.Name):
                found_calls.add(node.func.id)
            # Check for method calls: obj.method()
            elif isinstance(node.func, ast.Attribute):
                found_calls.add(node.func.attr)

    print(f"Integration Verification Report for {TARGET_FILE}")
    print("=" * 60)

    # 1. Standard Features
    for func_name, desc in STANDARD_FEATURES.items():
        if func_name in found_calls:
            print(f"Feature '{func_name}' ({desc}): ✅ CALL FOUND")
        else:
            print(f"Feature '{func_name}' ({desc}): ❌ NOT CALLED")

    # 2. Scribe/Audio (transcribe OR listen)
    if 'transcribe' in found_calls or 'listen' in found_calls:
        print(f"Feature 'transcribe' or 'listen' (Paper 2: Scribe/Audio): ✅ CALL FOUND")
    else:
        print(f"Feature 'transcribe' or 'listen' (Paper 2: Scribe/Audio): ❌ NOT CALLED")

    # 3. Crowd Counting (count OR len)
    # The prompt specifically asks to look for 'len(boxes)' which implies 'len' is called, 
    # or a method named 'count'.
    if 'count' in found_calls or 'len' in found_calls:
        print(f"Feature 'count' or 'len' (Paper 4: Crowd Counting Logic): ✅ CALL FOUND")
    else:
        print(f"Feature 'count' or 'len' (Paper 4: Crowd Counting Logic): ❌ NOT CALLED")

if __name__ == "__main__":
    verify_integration()
