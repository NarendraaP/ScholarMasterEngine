import os
import datetime

class SystemLogger:
    """
    System Audit Logger for tracking administrative actions.
    Logs all critical operations for compliance and security auditing.
    """
    
    def __init__(self, log_dir="data"):
        """
        Initialize System Logger.
        Args:
            log_dir: Directory to store audit logs (default: data/)
        """
        self.log_dir = log_dir
        self.audit_log_path = os.path.join(log_dir, "system_audit.log")
        
        # Ensure directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Create log file if it doesn't exist
        if not os.path.exists(self.audit_log_path):
            with open(self.audit_log_path, 'w', encoding='utf-8') as f:
                f.write("# System Audit Log\n")
                f.write("# Format: [TIMESTAMP] [USER] ACTION -> TARGET\n")
                f.write("="*70 + "\n")
    
    def log_audit(self, user, action, target):
        """
        Log an administrative action to system_audit.log.
        
        Args:
            user: Username performing the action
            action: Action being performed (e.g., "CREATE_USER", "DELETE_RECORD")
            target: Target of the action (e.g., "student_id:S12345", "zone:CAM_01")
            
        Example:
            logger.log_audit("admin", "CREATE_USER", "student_id:S12345")
            Output: [2025-12-02 02:03:45] [admin] CREATE_USER -> student_id:S12345
        """
        try:
            # Create timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Format log entry
            log_entry = f"[{timestamp}] [{user}] {action} -> {target}\n"
            
            # Append to log file (atomic operation)
            with open(self.audit_log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
            
            # Also print to console for immediate feedback
            print(f"📝 AUDIT: {log_entry.strip()}")
            
        except Exception as e:
            print(f"❌ Failed to log audit entry: {e}")
    
    def log_security_event(self, event_type, details, zone="Unknown"):
        """
        Log security events (e.g., intrusion, spoof attempts).
        
        Args:
            event_type: Type of security event (e.g., "INTRUSION", "SPOOF_ATTEMPT")
            details: Details about the event
            zone: Zone where event occurred
        """
        self.log_audit("SYSTEM", f"SECURITY:{event_type}:{zone}", details)

    def log_event(self, event_type, zone, details="Event Logged"):
        """
        Generic event logger to align with newer calling conventions.
        """
        self.log_audit("SYSTEM", event_type, f"{zone} - {details}")
    
    def log_access(self, user, resource, access_type="READ"):
        """
        Log data access for compliance.
        
        Args:
            user: User accessing the data
            resource: Resource being accessed (e.g., "students.json", "attendance.csv")
            access_type: Type of access (READ, WRITE, DELETE)
        """
        self.log_audit(user, f"ACCESS:{access_type}", resource)
    
    def get_recent_logs(self, num_lines=50):
        """
        Retrieve recent audit log entries.
        
        Args:
            num_lines: Number of recent lines to retrieve (default: 50)
            
        Returns:
            list: List of recent log entries
        """
        try:
            with open(self.audit_log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # Return last num_lines (excluding header)
                return [line.strip() for line in lines[-num_lines:] if line.strip() and not line.startswith('#')]
        except Exception as e:
            print(f"❌ Failed to read audit log: {e}")
            return []

if __name__ == "__main__":
    # Test
    logger = SystemLogger()
    logger.log_audit("admin", "CREATE_USER", "student_id:S12345")
    logger.log_audit("faculty_manager", "UPDATE_ATTENDANCE", "room:LH-A")
    logger.log_security_event("INTRUSION", "Unidentified person detected", "Corridor")
    
    print("\n📜 Recent Logs:")
    for log in logger.get_recent_logs(10):
        print(f"   {log}")
