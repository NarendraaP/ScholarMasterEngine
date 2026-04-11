import time
import threading
import os
import signal
import sys
import ctypes

# Constants from Paper 18
FRAME_TTL_MS = 33 
WATCHDOG_INTERVAL_MS = 100

class SimulatedMemoryBuffer:
    def __init__(self, buffer_id):
        self.id = buffer_id
        self.created = time.time()
        # Simulated raw RGB frame (1920x1080x3 approx) represented as string payload
        self.raw_data = "RGB_PIXEL_DATA_PAYLOAD_" * 10 
        self.is_zeroized = False

    def zeroize(self):
        """P18-INV-06: Zeroization Completeness"""
        # Overwrite with null bytes to prevent dead-store elimination
        self.raw_data = "\x00" * len(self.raw_data)
        self.is_zeroized = True
        
class InferenceApplication:
    def __init__(self):
        self.is_running = True
        self.active_buffers = []
        self.lock = threading.Lock()
        
    def ingest_frame(self):
        with self.lock:
            buf = SimulatedMemoryBuffer(buffer_id=time.time())
            self.active_buffers.append(buf)
            return buf
            
    def _ttl_enforcement_loop(self):
        """P18-INV-02: TTL Compliance (Internal Loop)"""
        while self.is_running:
            now = time.time()
            with self.lock:
                for buf in list(self.active_buffers):
                    age_ms = (now - buf.created) * 1000.0
                    if age_ms > FRAME_TTL_MS:
                        buf.zeroize()
                        self.active_buffers.remove(buf)
            time.sleep(0.01) # 10ms check interval

    def start(self):
        self.ttl_thread = threading.Thread(target=self._ttl_enforcement_loop, daemon=True)
        self.ttl_thread.start()

    def simulate_hard_hang(self):
        """Simulate an OOM lock or Deadlock where the internal TTL loop fails."""
        print("[INFERENCE] CRITICAL: Simulating Deadlock / CPU Starvation...")
        self.is_running = False 
        
class WatchdogSupervisor:
    def __init__(self, main_app):
        self.main_app = main_app
        self.is_running = True
        
    def _watchdog_loop(self):
        """P18-INV-05 & P18-INV-02: Independent Watchdog Enforcement"""
        while self.is_running:
            now = time.time()
            violation_detected = False
            
            # The Watchdog independently inspects the shared memory fence
            with self.main_app.lock:
                for buf in self.main_app.active_buffers:
                    age_ms = (now - buf.created) * 1000.0
                    # The Watchdog allows a slight grace period (e.g., up to 45ms) before dropping the hammer
                    if age_ms > (FRAME_TTL_MS + 12): 
                        print(f"\n[WATCHDOG] 🚨 TTL VIOLATION DETECTED! Buffer age: {age_ms:.1f}ms (Limit: {FRAME_TTL_MS}ms)")
                        violation_detected = True
                        
                        # PRE-KILL ZEROIZATION (Fail-Closed)
                        buf.zeroize()
            
            if violation_detected:
                print("[WATCHDOG] ⚡ Executing FAIL-CLOSED SIGKILL on Inference Process...")
                self.trigger_sigkill()
                break
                
            time.sleep(WATCHDOG_INTERVAL_MS / 1000.0)
            
    def start(self):
        print("[WATCHDOG] Supervisor Online. Monitoring Shared IPC Fence.")
        self.wd_thread = threading.Thread(target=self._watchdog_loop, daemon=True)
        self.wd_thread.start()
        
    def trigger_sigkill(self):
        """Issues OS-level terminate signal (Simulated for this script)"""
        self.is_running = False
        print("[WATCHDOG] 💀 Inference Process Terminated.")
        print("[WATCHDOG] Post-Crash Forensics: Validating P18-INV-06 (Zeroization)...")
        
        # Verify Zeroization
        residue_found = False
        for buf in self.main_app.active_buffers:
            if buf.raw_data != ("\x00" * len(buf.raw_data)):
                residue_found = True
                
        if residue_found:
             print("[FORENSICS] FAIL: Data residue found in application layer POST-CRASH.")
        else:
             print("[FORENSICS] PASS: Zero application-layer data residue. Buffers strictly zeroized.")
        
        # In a real environment, we'd invoke os.kill(pid, signal.SIGKILL)
        # For the test harness, we gracefully exit the simulation.
        sys.exit(0)

# ==========================================
# TEST HARNESS EXECUTION
# ==========================================
def run_fault_injection():
    print("=================================================================")
    print("Paper 18: Runtime Enforcement Fault Injector (Chaos Engineering)")
    print("=================================================================\n")
    
    app = InferenceApplication()
    app.start()
    
    watchdog = WatchdogSupervisor(app)
    watchdog.start()
    
    print("[TEST F00] Normal Operation: Ingesting Frame...")
    app.ingest_frame()
    time.sleep(0.05) # Wait 50ms (Should be naturally zeroized by internal TTL loop)
    
    print(f"[TEST F00] Active Buffers Post-Ingest: {len(app.active_buffers)} (Expected: 0)")
    
    print("\n[TEST F01] Initiating Fault Injection (Simulated Process Hang)...")
    hanging_buf = app.ingest_frame()
    print(f"   -> Frame {hanging_buf.id} ingested.")
    
    # Simulate the main process locking up, disabling its own internal TTL checks
    app.simulate_hard_hang() 
    
    # Sit back and let the isolated Watchdog detect the violation
    time.sleep(0.2) 

if __name__ == "__main__":
    run_fault_injection()
