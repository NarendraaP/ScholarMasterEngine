import time
from typing import List, Dict, Any

class TemporalJitterBuffer:
    """
    Simulates a Time-Indexed Skip List for out-of-order event delivery (Sliding Window).
    Maintains a chronologically sorted buffer up to a max temporal jitter threshold.
    """
    def __init__(self, max_jitter_ms=5000):
        self.max_jitter_ms = max_jitter_ms
        # Simulated Time-Indexed Skip List for out-of-order packets
        self.buffer: List[Dict[str, Any]] = []

    def insert_event(self, event: Dict[str, Any]) -> bool:
        """
        Inserts event in O(N) list insertion, simulating O(log K) Skip List insertion.
        Resolves the "Temporal Jitter" challenge without halting the stream.
        """
        tau_occ = event.get('timestamp_ms', 0)
        
        current_time_ms = int(time.time() * 1000)
        # Drop if exceeding jitter threshold completely
        if current_time_ms - tau_occ > self.max_jitter_ms:
            return False

        # Fast traversal to find insertion point (simulating skip list upper levels)
        insert_idx = len(self.buffer)
        for i in range(len(self.buffer) - 1, -1, -1):
            if self.buffer[i]['timestamp_ms'] <= tau_occ:
                insert_idx = i + 1
                break
            else:
                insert_idx = i
                
        self.buffer.insert(insert_idx, event)
        self._flush_old_events(current_time_ms)
        return True
        
    def _flush_old_events(self, current_time_ms: int):
        cutoff = current_time_ms - self.max_jitter_ms
        keep_idx = 0
        for i, ev in enumerate(self.buffer):
            if ev['timestamp_ms'] >= cutoff:
                keep_idx = i
                break
            keep_idx = len(self.buffer)
            
        if keep_idx > 0:
            self.buffer = self.buffer[keep_idx:]

    def get_latest_state(self) -> Dict[str, Any]:
        if not self.buffer:
            return None
        return self.buffer[-1]
        
    def get_all_events(self) -> List[Dict[str, Any]]:
        return self.buffer
