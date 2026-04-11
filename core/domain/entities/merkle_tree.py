import hashlib
from typing import List, Optional, Any
import json
from dataclasses import dataclass, asdict

class MerkleNode:
    def __init__(self, left: Optional['MerkleNode'] = None, right: Optional['MerkleNode'] = None, data: Any = None):
        self.left = left
        self.right = right
        self.data_hash = None
        
        if data is not None:
            # Leaf node
            if isinstance(data, dict):
                content = json.dumps(data, sort_keys=True).encode('utf-8')
            elif hasattr(data, "timestamp"):  # Handle dataclass/domain events
                content = json.dumps(asdict(data), default=str, sort_keys=True).encode('utf-8')
            else:
                content = str(data).encode('utf-8')
            self.data_hash = hashlib.sha256(content).hexdigest()
        else:
            # Internal node - enforce lexicographical sorting for Paper 8 Proof compatibility
            hash1 = left.data_hash if left else ""
            hash2 = right.data_hash if right else ""
            
            if hash1 < hash2:
                combined = hash1 + hash2
            else:
                combined = hash2 + hash1
                
            self.data_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()

class MerkleTree:
    """
    A Merkle Tree implementation for detecting sync discrepancies between nodes.
    Used for Edge-Cloud Synchronization (Paper 4 Proposed Architecture).
    """
    def __init__(self, items: List[Any]):
        self.leaves = [MerkleNode(data=item) for item in items]
        if not self.leaves:
            self.root = None
        else:
            self.root = self._build_tree(self.leaves)
            
    def _build_tree(self, nodes: List[MerkleNode]) -> MerkleNode:
        if len(nodes) == 1:
            return nodes[0]
            
        parents = []
        for i in range(0, len(nodes), 2):
            left = nodes[i]
            # If an odd number of nodes, duplicate the last one (standard Merkle approach)
            right = nodes[i + 1] if i + 1 < len(nodes) else left
            parents.append(MerkleNode(left=left, right=right))
            
        return self._build_tree(parents)
        
    @property
    def root_hash(self) -> Optional[str]:
        return self.root.data_hash if self.root else None
    
    @staticmethod
    def compare_trees(local_node: Optional[MerkleNode], remote_node: Optional[MerkleNode]) -> bool:
        """
        Compare two Merkle nodes. Returns True if they match, False if they mismatch.
        In a real sync protocol, a False return triggers recursive sub-tree requests until 
        the specific missing leaves are identified, significantly optimizing bandwidth.
        """
        if local_node is None and remote_node is None:
            return True
        if local_node is None or remote_node is None:
            return False
            
        return local_node.data_hash == remote_node.data_hash

    # --- Paper 8 Proof of Inclusion (Algorithm 1) ---
    def get_proof(self, target_hash: str) -> Optional[List[str]]:
        """
        Generates a Merkle Proof (list of sibling hashes) starting from the leaf up to the root.
        """
        path = []
        
        def _find_path(node: MerkleNode, target: str) -> bool:
            if not node:
                return False
            
            # If leaf node
            if not node.left and node.data_hash == target:
                return True
                
            # If internal node, check left child
            in_left = False
            if node.left:
                in_left = _find_path(node.left, target)
                if in_left:
                    # To verify the left child, we need the right child's hash (if it exists)
                    if node.right:
                        path.append(node.right.data_hash)
                    return True
                    
            # Check right child
            in_right = False
            if node.right:
                in_right = _find_path(node.right, target)
                if in_right:
                    # To verify the right child, we need the left child's hash
                    if node.left:
                        path.append(node.left.data_hash)
                    return True
                    
            return False

        if _find_path(self.root, target_hash):
            return path
        return None

    @staticmethod
    def verify_proof(target_hash: str, proof_path: List[str], root_hash: str) -> bool:
        """
        Paper 8: Algorithm 1 (Merkle Proof Verification - Client Side)
        Node ordering during hash concatenation is determined lexicographically.
        """
        current_hash = target_hash
        
        for sibling_hash in proof_path:
            # Lexicographical sort determines concatenation order for deterministic hashing
            if current_hash < sibling_hash:
                combined = current_hash + sibling_hash
            else:
                combined = sibling_hash + current_hash
                
            current_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
            
        return current_hash == root_hash

