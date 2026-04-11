import hashlib
import time
import json
import logging
from typing import List, Dict, Any, Optional

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from core.domain.entities.merkle_tree import MerkleTree, MerkleNode

class Block:
    """
    Batched Merkle-Tree Block representing a single chunk in the Directed Acyclic Graph.
    """
    def __init__(self, index: int, previous_hash: str, transactions: List[Dict[str, Any]]):
        self.index = index
        self.timestamp = int(time.time() * 1000)
        self.transactions = transactions
        self.previous_hash = previous_hash
        
        # Generate Merkle Tree from the transactions
        self.merkle_tree = MerkleTree(self.transactions)
        self.merkle_root = self.merkle_tree.root_hash if self.merkle_tree.root_hash else "0"
        
        self.hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """
        Section III A: SHA256( MerkleRoot(TX_set) || H_{i-1} || T_i )
        """
        block_content = f"{self.merkle_root}{self.previous_hash}{self.timestamp}".encode('utf-8')
        return hashlib.sha256(block_content).hexdigest()
        
    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "merkle_root": self.merkle_root,
            "previous_hash": self.previous_hash,
            "hash": self.hash,
            "tx_count": len(self.transactions)
        }

class ImmutableLedger:
    """
    Cryptographic Provenance Layer (CPL) - Validates and appends blocks immutably.
    """
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict[str, Any]] = []
        self._create_genesis_block()
        
    def _create_genesis_block(self):
        genesis_block = Block(0, "0"*64, [{"type": "GENESIS"}])
        self.chain.append(genesis_block)
        
    def add_transaction(self, tx: Dict[str, Any]):
        self.pending_transactions.append(tx)
        
    def mine_block(self) -> Optional[Block]:
        """
        Simulates Raft Consensus gathering pending TXs into a Block.
        """
        if not self.pending_transactions:
            return None
            
        previous_block = self.chain[-1]
        
        # Batch bounded by size to ensure consistent TPS without Raft timeouts
        batch = self.pending_transactions[:100]
        self.pending_transactions = self.pending_transactions[100:]
        
        new_block = Block(
            index=previous_block.index + 1,
            previous_hash=previous_block.hash,
            transactions=batch
        )
        
        self.chain.append(new_block)
        logging.info(f"LEDGER: Block {new_block.index} minted. Hash: {new_block.hash[:16]}... MerkleRoot: {new_block.merkle_root[:16]}...")
        return new_block

    def is_chain_valid(self) -> bool:
        """
        Strict cryptographic verification of the entire history DAG.
        """
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # 1. Structural Link Integrity
            if current_block.previous_hash != previous_block.hash:
                return False
                
            # 2. Cryptographic Hash Validity
            if current_block.hash != current_block._calculate_hash():
                return False
                
            # 3. Merkle Root Integrity
            test_tree = MerkleTree(current_block.transactions)
            if current_block.merkle_root != test_tree.root_hash:
                return False
                
        return True
