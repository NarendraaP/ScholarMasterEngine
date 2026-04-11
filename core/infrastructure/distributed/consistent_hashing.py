import hashlib
import bisect
import logging

class ConsistentHashRing:
    """
    Virtual-Node Consistent Hashing using deterministic hashing.
    Resolves "State Locality" by ensuring specific entities always map to the same node for O(1) state lookups.
    """
    def __init__(self, num_replicas=100):
        self.num_replicas = num_replicas
        self.ring = dict()
        self.sorted_keys = []
        self.nodes = set()

    def _hash(self, key: str) -> int:
        # Simulate MurmurHash3 with MD5 for deterministic 32-bit integer routing
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16) % (2**32)

    def add_node(self, node_id: str):
        self.nodes.add(node_id)
        for i in range(self.num_replicas):
            v_node_key = f"{node_id}#{i}"
            h = self._hash(v_node_key)
            self.ring[h] = node_id
            bisect.insort(self.sorted_keys, h)
        logging.info(f"Node '{node_id}' added to the hash ring with {self.num_replicas} virtual nodes.")

    def remove_node(self, node_id: str):
        if node_id not in self.nodes:
            return
        self.nodes.remove(node_id)
        for i in range(self.num_replicas):
            v_node_key = f"{node_id}#{i}"
            h = self._hash(v_node_key)
            del self.ring[h]
            self.sorted_keys.remove(h)
        logging.info(f"Node '{node_id}' removed from the hash ring.")

    def get_node(self, entity_id: str) -> str:
        """
        O(log N) routing function to deterministically resolve which node owns a specific entity's partition.
        """
        if not self.ring:
            return None
        h = self._hash(entity_id)
        idx = bisect.bisect_right(self.sorted_keys, h)
        if idx == len(self.sorted_keys):
            idx = 0
        return self.ring[self.sorted_keys[idx]]
