import logging
from typing import Dict, Any

class MigrationManager:
    """
    Implements the Lazy State Migration Protocol to dynamically balance load.
    Prevents "stop-the-world" latency spikes caused by Eager bulk migration.
    """
    def __init__(self):
        # Simulate network RPC access to old node states
        self.simulated_cluster_state = {}

    def fetch_state_lazy(self, old_node_id: str, new_node_id: str, entity_id: str) -> Dict[str, Any]:
        """
        Synchronous RPC to fetch state from old node ONLY when an event arrives.
        """
        logging.info(f"LAZY MIGRATION: Fetching state for '{entity_id}' from '{old_node_id}' to '{new_node_id}'")
        
        # Simulate synchronous RPC fetch
        if old_node_id in self.simulated_cluster_state and entity_id in self.simulated_cluster_state[old_node_id]:
            state = self.simulated_cluster_state[old_node_id][entity_id]
            # Free memory on old node (mimics RPC_DeleteState)
            del self.simulated_cluster_state[old_node_id][entity_id]
            
            # Store on new node
            if new_node_id not in self.simulated_cluster_state:
                self.simulated_cluster_state[new_node_id] = {}
            self.simulated_cluster_state[new_node_id][entity_id] = state
            return state
            
        return None

    def store_simulated_state(self, node_id: str, entity_id: str, state: Dict[str, Any]):
        """Helper to prepopulate state for simulation."""
        if node_id not in self.simulated_cluster_state:
            self.simulated_cluster_state[node_id] = {}
        self.simulated_cluster_state[node_id][entity_id] = state
        
    def get_simulated_state(self, node_id: str, entity_id: str) -> Dict[str, Any]:
        """Helper to dump state for simulation."""
        return self.simulated_cluster_state.get(node_id, {}).get(entity_id)
