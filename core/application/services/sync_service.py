from typing import List, Tuple, Optional
import logging
from core.domain.events.domain_events import DomainEvent
from core.domain.entities.merkle_tree import MerkleTree, MerkleNode

logger = logging.getLogger(__name__)

class ScheduleSyncService:
    """
    Application service that implements the Merkle Tree Synchronization Protocol
    described in Paper 4 (Edge-Cloud Synchronization).
    
    This service allows distributed Edge nodes to securely and efficiently sync 
    their local event logs with a Central Server, identifying missing records
    without transmitting the entire database over constrained networks.
    """
    
    @staticmethod
    def generate_sync_tree(events: List[DomainEvent]) -> MerkleTree:
        """
        Generates a Merkle Tree from a list of local domain events.
        """
        # Sort events by timestamp to ensure deterministic tree generation
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        return MerkleTree(sorted_events)
        
    @staticmethod
    def detect_desync(local_tree: MerkleTree, remote_root_hash: str) -> bool:
        """
        Fast O(1) check to see if the local edge node is out of sync with the central server.
        """
        if not local_tree or not local_tree.root_hash:
            return remote_root_hash is not None
            
        return local_tree.root_hash != remote_root_hash
        
    @staticmethod
    def find_missing_events(local_node: Optional[MerkleNode], remote_node: Optional[MerkleNode]) -> List[str]:
        """
        Recursively traverses the Merkle tree to find specific mismatched leaf nodes (event hashes).
        This is the core efficiency of the Merkle sync protocol.
        
        Returns a list of missing/mismatched data hashes.
        """
        missing_hashes = []
        
        # If both are None, trees are empty and match
        if local_node is None and remote_node is None:
            return missing_hashes
            
        # If local is missing but remote has data, we are missing this entire branch
        if local_node is None and remote_node is not None:
            # In a full implementation, we'd request all leaves of remote_node.
            # Here we just mark the root of the missing branch.
            missing_hashes.append(remote_node.data_hash)
            return missing_hashes
            
        # If local has data but remote doesn't, we have unsynced local events!
        if local_node is not None and remote_node is None:
            missing_hashes.append(local_node.data_hash)
            return missing_hashes
            
        # If hashes match, this entire sub-tree is perfectly in sync
        if local_node.data_hash == remote_node.data_hash:
            return missing_hashes
            
        # Hashes mismatch. If we are at a leaf node, this is the specific missing/corrupted event
        if local_node.left is None and local_node.right is None:
            missing_hashes.append(local_node.data_hash)
            return missing_hashes
            
        # Hashes mismatch, and we are at an internal node. Recurse down both branches.
        missing_hashes.extend(ScheduleSyncService.find_missing_events(local_node.left, remote_node.left))
        missing_hashes.extend(ScheduleSyncService.find_missing_events(local_node.right, remote_node.right))
        
        return missing_hashes
