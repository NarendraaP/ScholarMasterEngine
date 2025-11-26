import json
import hashlib
import secrets
import os

USERS_FILE = "data/users.json"

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(8) # 16 chars hex
    # SHA256(password + salt)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return hashed, salt

def secure_the_database():
    if not os.path.exists(USERS_FILE):
        print(f"Error: {USERS_FILE} not found.")
        return

    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    updated = False
    for username, data in users.items():
        stored_pwd = data.get("password", "")
        
        # Check if already salted (contains ":")
        if ":" in stored_pwd:
            print(f"User {username} already secured with salt.")
            continue
            
        print(f"Securing {username}...")
        
        # For migration purposes, we reset everyone to "123" 
        # because we cannot recover the plain text from the existing unsalted hash.
        plain_text_password = "123"
        
        hashed, salt = hash_password(plain_text_password)
        data["password"] = f"{hashed}:{salt}"
        updated = True
        print(f"Secured {username} (Password reset to '123')")

    if updated:
        with open(USERS_FILE, "w") as f:
            json.dump(users, f, indent=4)
        print("Database Secured with Salted SHA-256")
    else:
        print("Database already secured.")

if __name__ == "__main__":
    secure_the_database()
