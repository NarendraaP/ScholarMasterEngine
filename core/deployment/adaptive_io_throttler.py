import time
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')


class AdaptiveThrottlingDaemon:
    """
    Paper 12: Adaptive Write Throttling Daemon (Algorithm 1)
    Simulates monitoring /sys/block/mmcblk0/stat and restricting OS IO 
    (logging level, dirty cache) dynamically based on daily budget.
    """
    def __init__(self, daily_budget_bytes: int):
        self.budget = daily_budget_bytes
        self.current_used = 0
        self.start_time = time.time()
        self.log_level = "INFO"
        self.dirty_expire_centisecs = 360000
    
    def simulate_sys_block_read(self) -> int:
        """Mock reading cumulative bytes written from the block device."""
        return self.current_used
        
    def add_write_load(self, bytes_written: int):
        """Mock the application generating I/O load."""
        self.current_used += bytes_written
        
    def evaluation_tick(self):
        """Algorithm 1 Evaluation Tick"""
        current_time = time.time()
        elapsed_seconds = current_time - self.start_time
        
        # Prevent zero-division in very fast simulation loops
        if elapsed_seconds < 0.1:
            return self.log_level
            
        w_used = self.simulate_sys_block_read()
        w_rate = w_used / elapsed_seconds # Bytes per second
        w_projected = w_rate * 86400 # Bytes per 24 hours
        
        usage_pct = (w_projected / self.budget) * 100
        
        if w_projected > self.budget:
            logging.error(f"[IO THROTTLE] Projected Budget Exceeded! ({usage_pct:.1f}%). Throttling Activated.")
            self.log_level = "ERROR_ONLY"
            self.dirty_expire_centisecs = 720000 # 2 hours
        else:
            if usage_pct > 80:
                logging.warning(f"[IO MONITOR] Budget warning: {usage_pct:.1f}%. Approaching limits.")
            self.log_level = "INFO"
            self.dirty_expire_centisecs = 360000 # 1 hour
            
        return self.log_level

def run_adaptive_throttle_test():
    print("="*80)
    print("Paper 12 MLOps: Adaptive IO Throttling (Algorithm 1)")
    print("="*80)
    
    # Set a small daily budget for the test: 1GB (1 * 1024^3 bytes)
    BUDGET = 1_073_741_824 
    
    daemon = AdaptiveThrottlingDaemon(daily_budget_bytes=BUDGET)
    
    # 1. Normal Load (Should be fine)
    print("\n--- PHASE 1: NORMAL TELEMETRY LOAD ---")
    daemon.start_time = time.time() - 3600 # Assume running for 1 hour
    # 20MB written in 1 hour (projects to ~480MB daily)
    daemon.add_write_load(20_000_000) 
    level = daemon.evaluation_tick()
    print(f"System State -> Log Level: {level}, Cache Expiry: {daemon.dirty_expire_centisecs/1000}s")
    
    # 2. Burst Load (Simulate large container update downloading)
    print("\n--- PHASE 2: MASSIVE IO BURST (CONTAINER UPDATE) ---")
    daemon.start_time = time.time() - 3600 # Still hour 1
    # 500MB written very suddenly (projects to 12.4GB daily -> way over budget)
    daemon.add_write_load(500_000_000) 
    level = daemon.evaluation_tick()
    print(f"System State -> Log Level: {level}, Cache Expiry: {daemon.dirty_expire_centisecs/1000}s")
    print(f"Outcome: System dynamically restricted I/O to protect hardware limits.")

if __name__ == "__main__":
    run_adaptive_throttle_test()
