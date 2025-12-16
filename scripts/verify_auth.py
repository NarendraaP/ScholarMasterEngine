from modules.auth import Authenticator
import hashlib
import os
import json
import pytest

def test_auth():
    print("🧪 Testing Authenticator...")
    
    # Setup dummy users file
    test_users_file = "data/test_users.json"
    users_data = {
        "admin": {"password": hashlib.sha256("admin123".encode()).hexdigest(), "role": "Super Admin"},
        "user_salt": {"password": f"{hashlib.sha256(('pass123' + 'somesalt').encode()).hexdigest()}:somesalt", "role": "Student"}
    }
    
    with open(test_users_file, "w") as f:
        json.dump(users_data, f)
        
    auth = Authenticator(users_file=test_users_file)
    
    # Test 1: Legacy SHA256
    print("Test 1: Legacy SHA256 Login...")
    valid, user = auth.verify_user("admin", "admin123")
    assert valid == True
    assert user["role"] == "Super Admin"
    print("✅ Legacy Login Passed")
    
    # Test 2: Salted SHA256
    print("Test 2: Salted SHA256 Login...")
    valid, user = auth.verify_user("user_salt", "pass123")
    assert valid == True
    assert user["role"] == "Student"
    print("✅ Salted Login Passed")
    
    # Test 3: Invalid Password
    print("Test 3: Invalid Password...")
    valid, _ = auth.verify_user("admin", "wrongpass")
    assert valid == False
    print("✅ Invalid Password Rejected")
    
    # Cleanup
    if os.path.exists(test_users_file):
        os.remove(test_users_file)

if __name__ == "__main__":
    test_auth()
