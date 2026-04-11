import os
import json
import logging
from typing import Dict, Any

class ForkSnapshotManager:
    """
    Implements the Asynchronous State Snapshot via Fork.
    Leverages OS-level Copy-on-Write for durable point-in-time recovery without stalling.
    """
    def __init__(self, snapshot_dir="/tmp/scholarmaster_snapshots"):
        self.snapshot_dir = snapshot_dir
        if not os.path.exists(self.snapshot_dir):
            os.makedirs(self.snapshot_dir, exist_ok=True)

    def trigger_snapshot(self, process_memory: Dict[str, Any]) -> int:
        """
        Triggers an asynchronous snapshot. Returns the child PID.
        The parent process returns immediately and continues processing events.
        """
        logging.info("Triggering Asynchronous Chandy-Lamport Snapshot...")
        
        try:
            pid = os.fork()
        except OSError as e:
            logging.error(f"Fork failed: {e}")
            # Degraded operation: skip snapshot if fork fails
            return -1

        if pid == 0:
            # Child Process Execution: Inherits full memory map instantly via CoW
            temp_file = os.path.join(self.snapshot_dir, "snapshot_temp.bin")
            final_file = os.path.join(self.snapshot_dir, "snapshot.bin")
            
            try:
                # Flush inherited RAM partition to disk
                with open(temp_file, 'w') as f:
                    json.dump(process_memory, f)
                
                # Atomic rename ensures snapshot file is never corrupted mid-write
                os.rename(temp_file, final_file)
                logging.info(f"Child [PID: {os.getpid()}]: Snapshot serialization complete. Exiting gracefully.")
            except Exception as e:
                logging.error(f"Child snapshot error: {e}")
            finally:
                # Crucial: child MUST exit immediately so it doesn't continue main script logic
                os._exit(0)
        else:
            # Parent Process Execution: Returns immediately
            logging.info(f"Parent [PID: {os.getpid()}]: Fork successful. Child {pid} is flushing memory to disk.")
            logging.info("Parent: Continuing event evaluation with zero downtime via Copy-on-Write.")
            return pid
