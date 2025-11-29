import json
import os
import sys
import getpass

# Add project root to path to import utils
sys.path.append(os.getcwd())

try:
    from utils.hasher import hash_password
except ImportError:
    # Fallback if run from utils dir
    sys.path.append(os.path.join(os.getcwd(), ".."))
    from utils.hasher import hash_password

USERS_FILE = "data/users.json"

def create_superuser():
    print("--- Create Super Admin ---")
    username = input("Username: ").strip()
    if not username:
        print("Username cannot be empty.")
        return

    password = getpass.getpass("Password: ")
    confirm_password = getpass.getpass("Confirm Password: ")

    if password != confirm_password:
        print("Passwords do not match.")
        return

    if len(password) < 4:
        print("Password is too short (min 4 chars).")
        return

    # Load existing users
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                users = {}
    else:
        users = {}

    if username in users:
        overwrite = input(f"User '{username}' already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Operation cancelled.")
            return

    # Hash password
    hashed, salt = hash_password(password)
    
    # Save user
    users[username] = {
        "password": f"{hashed}:{salt}",
        "role": "Super Admin",
        "name": username.capitalize() # Default name
    }

    # Ensure directory exists
    os.makedirs(os.path.dirname(USERS_FILE), exist_ok=True)

    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

    print(f"✅ Super Admin '{username}' created successfully.")

if __name__ == "__main__":
    create_superuser()
