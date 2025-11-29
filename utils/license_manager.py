import os

LICENSE_FILE = "data/license.key"

def check_license():
    """
    Checks if the license file exists and contains a valid key.
    A valid key must end with '-2025'.
    Returns: True if valid, False otherwise.
    """
    if not os.path.exists(LICENSE_FILE):
        return False
    
    try:
        with open(LICENSE_FILE, "r") as f:
            key = f.read().strip()
            
        if key.endswith("-2025"):
            return True
        else:
            return False
    except Exception:
        return False
