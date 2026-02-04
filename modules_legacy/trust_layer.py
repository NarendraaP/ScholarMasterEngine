import hashlib
import json
import os
import time
from typing import Dict, Any

class TrustLogger:
    """
    Implements a simplified 'Immutable Ledger' using SHA-256 hash chaining.
    This satisfies the requirements of Paper 8 (Trust-Aware Metadata Provenance)
    without requiring a full blockchain node.
    
    Structure:
    Block N = {
        "timestamp": ...,
        "data": ...,
        "prev_hash": Hash(Block N-1),
        "curr_hash": SHA256(timestamp + data + prev_hash)
    }
    """
    
    def __init__(self, ledger_path="logs/immutable_ledger.json"):
        self.ledger_path = ledger_path
        self.ensure_ledger_exists()
        
    def ensure_ledger_exists(self):
        """Creates the ledger file and Genesis Block if missing."""
        # Only create directory if path includes one
        directory = os.path.dirname(self.ledger_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        
        if not os.path.exists(self.ledger_path):
            genesis_block = {
                "index": 0,
                "timestamp": time.time(),
                "event": "GENESIS_BLOCK",
                "data": {"message": "System Boot - Trust Layer Initialized"},
                "prev_hash": "0" * 64,
                "curr_hash": self._calculate_hash(0, time.time(), "GENESIS_BLOCK", {"message": "System Boot - Trust Layer Initialized"}, "0" * 64)
            }
            with open(self.ledger_path, "w") as f:
                json.dump([genesis_block], f, indent=2)
                
    def _calculate_hash(self, index, timestamp, event, data, prev_hash):
        """Creates a SHA-256 hash of the block content."""
        payload = f"{index}{timestamp}{event}{json.dumps(data, sort_keys=True)}{prev_hash}"
        return hashlib.sha256(payload.encode()).hexdigest()
        
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """
        Appends a new event to the ledger with cryptographic linkage.
        """
        # Load existing chain (in production, we'd cache the tail in memory)
        try:
            with open(self.ledger_path, "r") as f:
                chain = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ensure_ledger_exists()
            with open(self.ledger_path, "r") as f:
                chain = json.load(f)
                
        last_block = chain[-1]
        new_index = last_block["index"] + 1
        timestamp = time.time()
        prev_hash = last_block["curr_hash"]
        
        # Calculate new hash (The "Proof of Integrity")
        curr_hash = self._calculate_hash(new_index, timestamp, event_type, data, prev_hash)
        
        new_block = {
            "index": new_index,
            "timestamp": timestamp,
            "event": event_type,
            "data": data,
            "prev_hash": prev_hash,
            "curr_hash": curr_hash
        }
        
        chain.append(new_block)
        
        # Atomic Write (Simulated via write-replace)
        temp_path = self.ledger_path + ".tmp"
        with open(temp_path, "w") as f:
            json.dump(chain, f, indent=2)
        os.replace(temp_path, self.ledger_path)
        
        return curr_hash

    def verify_integrity(self) -> bool:
        """
        Audits the entire chain to detect tampering.
        Returns True if valid, False if tampering detected.
        """
        with open(self.ledger_path, "r") as f:
            chain = json.load(f)
            
        for i in range(1, len(chain)):
            current = chain[i]
            previous = chain[i-1]
            
            # Check 1: Linkage
            if current["prev_hash"] != previous["curr_hash"]:
                print(f"❌ TAMPER DETECTED: Broken Link at Block {i}")
                return False
                
            # Check 2: Content
            recalc_hash = self._calculate_hash(
                current["index"],
                current["timestamp"],
                current["event"],
                current["data"],
                current["prev_hash"]
            )
            if recalc_hash != current["curr_hash"]:
                print(f"❌ TAMPER DETECTED: Content Modified at Block {i}")
                return False
                
        return True

# Simple Usage Test
if __name__ == "__main__":
    trust = TrustLogger("test_ledger.json")
    print("Writing Test Events...")
    trust.log_event("TEST_EVENT", {"user": "Alice", "action": "Login"})
    trust.log_event("TEST_EVENT", {"user": "Bob", "action": "Access"})
    
    print("Verifying Integrity...")
    if trust.verify_integrity():
        print("✅ CHAIN VALID")
    else:
        print("❌ CHAIN INVALID")
    
    # Cleanup
    if os.path.exists("test_ledger.json"):
        os.remove("test_ledger.json")
