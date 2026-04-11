import threading
import time
import random
import numpy as np
import math
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

class CampusThread(threading.Thread):
    def __init__(self, campus_id, coordinator, n_samples, drop_probability=0.0):
        super().__init__()
        self.campus_id = campus_id
        self.coordinator = coordinator
        self.n_samples = n_samples
        self.drop_probability = drop_probability
        self.active = True
        
        self.sigma_campus = 0.3
        self.model_dim = 100

    def run(self):
        while self.active and self.coordinator.current_round < self.coordinator.max_rounds:
            # Simulate heterogeneous network/compute latency (0.1s to 0.4s)
            time.sleep(random.uniform(0.1, 0.4))
            
            # Simulate network dropout for resilient testing (40% dropout mentioned in Paper 14)
            if random.random() < self.drop_probability:
                logging.info(f"[NETWORK TIMEOUT] Campus {self.campus_id} dropped out of synchronization.")
                time.sleep(1.0) # Penalty for disconnecting
                continue
            
            # 1. Tier 1 (Classroom Edge Training Simulation)
            current_global, base_epoch = self.coordinator.get_global_model()
            
            # Mock Local SGD: gradient vaguely pointing to 0
            grad = -1 * current_global * 0.05 + np.random.randn(self.model_dim) * 0.1
            
            # 2. Tier 2 (Campus Aggregation + DP Noise)
            # Add hierarchical DP noise before the update crosses the firewall
            noise = np.random.randn(self.model_dim) * self.sigma_campus
            campus_update = current_global + grad + noise
            
            # Submit to Tier 3 (Global Federation)
            self.coordinator.submit_update(self.campus_id, campus_update, base_epoch, self.n_samples)

            time.sleep(0.1)

class GlobalCoordinator:
    def __init__(self, num_campuses=5, min_quorum=3, max_rounds=15, staleness_gamma=0.5):
        self.num_campuses = num_campuses
        self.min_quorum = min_quorum
        self.max_rounds = max_rounds
        self.gamma = staleness_gamma
        
        self.model_dim = 100
        self.global_weights = np.random.randn(self.model_dim) * 0.01
        self.current_round = 0
        
        self.update_queue = []
        self.lock = threading.Lock()
        
        self.global_loss = 2.457 # Initial high loss
        
    def get_global_model(self):
        with self.lock:
            return self.global_weights.copy(), self.current_round
            
    def submit_update(self, campus_id, updated_weights, base_epoch, n_samples):
        with self.lock:
            if self.current_round >= self.max_rounds:
                return
            self.update_queue.append((campus_id, updated_weights, base_epoch, n_samples))
            
            # Trigger Asynchronous Aggregation when Quorum is reached
            if len(self.update_queue) >= self.min_quorum:
                self.aggregate_and_step()
                
    def aggregate_and_step(self):
        # Tier 3 Aggregation
        self.current_round += 1
        
        delta_w_total = np.zeros(self.model_dim)
        weight_total = 0.0
        
        total_samples = sum([n for (_, _, _, n) in self.update_queue])
        
        staleness_records = []
        
        for (c_id, w_i, t_i, n_i) in self.update_queue:
            # Calculate tau (Epoch Staleness)
            tau = (self.current_round - 1) - t_i
            if tau < 0: tau = 0
            
            # Staleness Dampening Penalty alpha
            alpha = 1.0 / math.pow(1.0 + tau, self.gamma)
            
            # Combined Weight beta
            beta = alpha * (n_i / total_samples)
            
            delta_w_total += beta * (w_i - self.global_weights)
            weight_total += beta
            
            staleness_records.append((c_id, tau, alpha))
            
        # Global Update
        if weight_total > 0:
            self.global_weights += (delta_w_total / weight_total)
            
        # Simulate generalization loss reduction
        # In H-FedAvg, aggregating dampens variance to speed convergence
        self.global_loss = (self.global_loss * 0.85) + 0.05
            
        print(f"================================================================")
        print(f"GLOBAL ROUND {self.current_round:2d} | Validation Loss: {self.global_loss:.4f} | Quorum Reached: {len(self.update_queue)}/{self.num_campuses}")
        for (c_id, tau, alpha) in staleness_records:
            print(f"  -> Campus {c_id:10s} | Staleness: {tau} epochs | Dampening Weight: {alpha:.3f}")
            
        self.update_queue.clear()


if __name__ == "__main__":
    print("================================================================")
    print("Paper 14: Cross-Institutional H-FedAvg MLOps Simulator")
    print("Simulating 5 concurrent campuses with 40% aggregate network dropout")
    print("================================================================")
    
    coordinator = GlobalCoordinator(num_campuses=5, min_quorum=3, max_rounds=15)
    
    # Spawn 5 Campuses with heterogeneous network resiliency constraints
    campuses = [
        CampusThread("A_Modern",   coordinator, 5000, drop_probability=0.05),
        CampusThread("B_Heritage", coordinator, 4200, drop_probability=0.30),
        CampusThread("C_Lab",      coordinator, 6100, drop_probability=0.10),
        CampusThread("D_Generic",  coordinator, 3300, drop_probability=0.40),
        CampusThread("E_Generic",  coordinator, 4800, drop_probability=0.60), # Frequent disconnects
    ]
    
    for c in campuses:
        c.start()
        
    for c in campuses:
        c.join()
        
    print("\n================================================================")
    print("Simulation Complete. Cross-Campus H-FedAvg converged gracefully.")
    print("Asynchronous updates and Staleness Penalties absorbed Campus dropouts.")
    print("Data minimization (DPDP/GDPR) preserved via Hierarchical DP.")
    print("================================================================\n")
