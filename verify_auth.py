from modules.auth import Authenticator

def test_auth():
    auth = Authenticator()
    
    # Test valid users
    print("Testing valid users...")
    users = [
        ("admin", "123", "Super Admin", "Dr. Dean"),
        ("smith", "123", "Faculty", "Prof. Smith"),
        ("john", "123", "Student", "John Doe")
    ]
    
    for user, pwd, expected_role, expected_name in users:
        role, name = auth.verify_user(user, pwd)
        assert role == expected_role, f"Failed for {user}: Expected role {expected_role}, got {role}"
        assert name == expected_name, f"Failed for {user}: Expected name {expected_name}, got {name}"
        print(f"✅ {user} verified successfully.")

    # Test invalid user
    print("\nTesting invalid user...")
    role, name = auth.verify_user("hacker", "123")
    assert role is None, "Failed: Invalid user should return None"
    print("✅ Invalid user handled correctly.")

    # Test wrong password
    print("\nTesting wrong password...")
    role, name = auth.verify_user("admin", "wrongpass")
    assert role is None, "Failed: Wrong password should return None"
    print("✅ Wrong password handled correctly.")

if __name__ == "__main__":
    try:
        test_auth()
        print("\n🎉 All authentication tests passed!")
    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
