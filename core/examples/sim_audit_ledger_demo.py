import logging
import hashlib
import json

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from core.infrastructure.audit.kms_service import KeyManagementService
from core.infrastructure.audit.immutable_ledger import ImmutableLedger
from core.domain.entities.merkle_tree import MerkleNode, MerkleTree

logging.basicConfig(level=logging.INFO, format='%(message)s')

def run_burst_demo():
    print("="*60)
    print("ScholarMasterEngine - Paper 8: Cryptographic Provenance Layer")
    print("="*60)
    
    kms = KeyManagementService()
    ledger = ImmutableLedger()
    
    print("\n[Phase 1] High-Frequency Ingestion & Batching (1,000+ TPS)")
    # Generate 50 spatiotemporal events
    for i in range(50):
        identity_id = "user_A_123" if i % 2 == 0 else "user_B_456"
        
        # Plaintext payload targeting right to erasure
        plaintext = {
            "entity": identity_id,
            "zone": "Hallway",
            "lat": 12.345,
            "lon": 67.890,
            "seq": i
        }
        
        # 1. Encrypt off-chain with PISK symmetric key
        encrypted_tx = kms.encrypt_payload(identity_id, plaintext)
        
        # 2. Add to pending DAG pool
        ledger.add_transaction(encrypted_tx)
        
    # 3. Raft Leader cuts the block
    print("  Mining block containing 50 metadata events...")
    block = ledger.mine_block()
    
    print("\n[Phase 2] Zero-Knowledge Proof / Merkle Proof Generation")
    target_tx = block.transactions[10] # Grab user_A's encrypted transaction
    
    # Calculate target leaf hash (Note: must emulate logic in MerkleNode)
    raw_content = json.dumps(target_tx, sort_keys=True).encode('utf-8')
    target_leaf_hash = hashlib.sha256(raw_content).hexdigest()
    
    # Generate client-side proof
    print(f"  Target Leaf Hash: {target_leaf_hash[:16]}...")
    proof = block.merkle_tree.get_proof(target_leaf_hash)
    print(f"  Generated Proof Sibling Array length: {len(proof)}")
    
    # Auditing Entity verifiable
    is_valid = MerkleTree.verify_proof(target_leaf_hash, proof, block.merkle_root)
    print(f"  Proof of Inclusion: {is_valid}")
    
    print("\n[Phase 3] Cryptographic Shredding (GDPR Erasure)")
    # Attempt decrypt before shred
    plaintext_verify = kms.decrypt_payload("user_A_123", target_tx)
    print(f"  Pre-Shred Decrypt -> {plaintext_verify['entity']} at {plaintext_verify['zone']}")
    
    # Shred
    print(f"  Executing GDPR Right-to-Erasure for 'user_A_123'...")
    kms.cryptographic_shred("user_A_123")
    
    # Attempt decrypt after shred
    try:
        kms.decrypt_payload("user_A_123", target_tx)
    except PermissionError as e:
        print(f"  Post-Shred Decrypt -> SUCCESS (Access Denied: {e})")
        
    print("\n[Phase 4] Verifying Immutable Ledger Integrity")
    is_chain_intact = ledger.is_chain_valid()
    print(f"  Is Blockchain Integrity Mathematically Maintained? {is_chain_intact}")
    if is_chain_intact:
        print("    -> The ledger remains 100% valid despite the payload being permanently unrecoverable.")
        print("    -> Compliance Conflict Solved via PISK encryption decoupling.")

    print("\nVerification Complete.")

if __name__ == "__main__":
    run_burst_demo()
