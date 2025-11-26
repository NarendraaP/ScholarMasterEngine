import json
import os
import hashlib

class Authenticator:
    def __init__(self, users_file="data/users.json"):
        self.users_file = users_file
        self.users = self._load_users()

    def _load_users(self):
        if os.path.exists(self.users_file):
            with open(self.users_file, "r") as f:
                return json.load(f)
        return {}

    def verify_user(self, username, password):
        """
        Verifies user credentials using Salted SHA-256.
        Returns (role, name) if valid, else (None, None).
        """
        # Reload users to ensure we have the latest data
        self.users = self._load_users()
        
        if username in self.users:
            user_data = self.users[username]
            stored_password = user_data.get("password", "")
            
            # Check for Salted Hash format "HASH:SALT"
            if ":" in stored_password:
                try:
                    stored_hash, salt = stored_password.split(":")
                    # Calculate hash of input + salt
                    input_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                    
                    if input_hash == stored_hash:
                        return user_data["role"], user_data["name"]
                except ValueError:
                    # Handle malformed password string
                    pass
            
            # Fallback for legacy (plain SHA-256 or plain text)
            else:
                # Try plain SHA-256
                if stored_password == hashlib.sha256(password.encode()).hexdigest():
                     return user_data["role"], user_data["name"]
                # Try plain text
                if stored_password == password:
                     return user_data["role"], user_data["name"]
                     
        return None, None
