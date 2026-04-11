import time
import os
import threading
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

class SimulatedIPCQueue:
    """Simulates a shared memory queue holding processed inference frames."""
    def __init__(self):
        self.depth = 0
        self.is_frozen = False
        
    def enqueue(self):
        if not self.is_frozen:
            self.depth += 1
            
    def get_depth(self) -> int:
        return self.depth

class IntelligentWatchdog:
    """
    Paper 11: Intelligent Hardware Watchdog (WDT) Daemon
    Monitors the inference queue. If stagnant for > 5 seconds, stops petting the WDT.
    """
    def __init__(self, queue: SimulatedIPCQueue, stagnation_threshold: int = 5):
        self.queue = queue
        self.threshold = stagnation_threshold
        self.is_running = False
        
    def monitor_loop(self):
        self.is_running = True
        last_depth = -1
        stagnant_time = 0
        
        logging.info("[WDT] Daemon started. Monitoring inference pipe...")
        
        while self.is_running:
            current_depth = self.queue.get_depth()
            
            if current_depth > 0 and current_depth == last_depth:
                stagnant_time += 1
                logging.warning(f"[WDT] Pipeline Stagnation Detected: {stagnant_time}/{self.threshold}s")
            else:
                stagnant_time = 0
                if current_depth > 0:
                    logging.info(f"[WDT] Petting dog. Queue depth propagating to {current_depth}")
                
            if stagnant_time >= self.threshold:
                logging.error("\n[CRITICAL WDT TIMEOUT] Inference is frozen. Ceasing hardware pet.")
                logging.error("--> Hardware WDT will force a hard reset in 10s.\n")
                self.is_running = False
                break
                
            last_depth = current_depth
            time.sleep(1)
            
    def stop(self):
        self.is_running = False

def run_watchdog_test():
    print("="*80)
    print("Paper 11 MLOps: Intelligent WDT Simulation")
    print("="*80)
    
    queue = SimulatedIPCQueue()
    wdt = IntelligentWatchdog(queue, stagnation_threshold=5)
    
    monitor_thread = threading.Thread(target=wdt.monitor_loop)
    monitor_thread.start()
    
    # Simulate normal operation
    for i in range(3):
        queue.enqueue()
        time.sleep(1.2)
        
    # Inject Fault (simulating a deadlocked GPU/Kernel Panic)
    logging.info("\n--- INJECTING FAULT: Freezing Inference Pipeline ---\n")
    queue.is_frozen = True
    
    monitor_thread.join()
    print("Test Complete: Device successfully rebooted via Hardware WDT constraint.")

if __name__ == "__main__":
    run_watchdog_test()
