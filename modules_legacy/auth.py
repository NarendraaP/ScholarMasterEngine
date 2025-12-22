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
        Verifies username and password.
        Returns: (is_valid, user_data_dict)
        """
        # Reload users to ensure we have the latest data
        self.users = self._load_users()
        
        if username not in self.users:
            return False, {}
        
        user = self.users[username]
        stored_pass = user.get("password", "")
        
        # Check if password is salted (contains ':')
        if ':' in stored_pass:
            try:
                stored_hash, salt = stored_pass.split(':')
                input_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                
                if input_hash == stored_hash:
                    return True, user
            except ValueError:
                pass
        else:
            # Legacy unsalted password (direct SHA256 or plain text)
            if stored_pass == hashlib.sha256(password.encode()).hexdigest():
                return True, user
            if stored_pass == password:
                return True, user
        
        return False, {}


# --- Role-Based Access Control Decorator ---

def requires_role(*allowed_roles):
    """
    Decorator to restrict access based on user role.
    
    Usage:
        @requires_role('Super Admin', 'Faculty Manager')
        def protected_function():
            # Function code here
            pass
    
    Args:
        *allowed_roles: Variable number of role names that are allowed to access the function
    
    Returns:
        Decorator function that checks user role before executing the wrapped function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import streamlit as st
            
            # Check if user is logged in
            if not st.session_state.get('logged_in', False):
                st.error("🔒 Access Denied: You must be logged in to access this feature.")
                st.stop()
                return None
            
            # Get current user's role
            current_role = st.session_state.get('role', None)
            
            # Check if user has required role
            if current_role not in allowed_roles:
                st.error(f"🚫 Access Denied: This feature requires {' or '.join(allowed_roles)} role. Your role: {current_role}")
                st.stop()
                return None
            
            # User has required role, execute the function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def check_role(allowed_roles):
    """
    Helper function to check if current user has one of the allowed roles.
    Returns True if user is logged in and has required role, False otherwise.
    
    Args:
        allowed_roles: List of role strings (e.g., ['Admin', 'Faculty'])
    
    Returns:
        bool: True if authorized, False otherwise
    """
    import streamlit as st
    
    if not st.session_state.get('logged_in', False):
        return False
    
    current_role = st.session_state.get('role', None)
    return current_role in allowed_roles

def validate_role(allowed_roles, user_role=None):
    """
    Backend role validation function that raises PermissionError.
    Use this in backend functions to enforce access control.
    
    Args:
        allowed_roles: List of role strings (e.g., ['Admin', 'Faculty'])
        user_role: Role to check (if None, tries to get from session_state)
    
    Raises:
        PermissionError: If user doesn't have required role
    """
    import streamlit as st
    
    # Try to get role from session state if not provided
    if user_role is None:
        if not st.session_state.get('logged_in', False):
            raise PermissionError("Authentication required: User not logged in")
        user_role = st.session_state.get('role', None)
    
    # Validate role
    if user_role not in allowed_roles:
        raise PermissionError(
            f"Access Denied: This operation requires {' or '.join(allowed_roles)} role. "
            f"Current role: {user_role}"
        )
