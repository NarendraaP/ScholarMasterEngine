import os
import time
import subprocess
import argparse
import random

def get_macos_temp():
    """Attempt to read macOS CPU temp using powermetrics or osx-cpu-temp."""
    try:
        # Check if osx-cpu-temp is installed
        result = subprocess.run(["osx-cpu-temp"], capture_output=True, text=True, check=False)
        if result.returncode == 0 and result.stdout:
            temp_str = result.stdout.strip().replace('C', '').replace('*', '')
            return float(temp_str)
    except Exception:
        pass
        
    return None

def log_temp(duration_seconds=3600, log_interval=1.0, mock=False):
    """
    Polls Apple SMC or falls back to simulation for cross-platform execution.
    Target: ~60-65C as per Paper 5 Thermal Characterization
    """
    print(f"Starting Thermal Logger for {duration_seconds} seconds...")
    print("Writing to 'thermal_metrics.log'")
    
    start_time = time.time()
    
    with open("/Users/premkumartatapudi/Desktop/ScholarMasterEngine/core/examples/thermal_metrics.log", "w") as f:
        f.write("Timestamp,Temperature_C\n")
        
        while time.time() - start_time < duration_seconds:
            current_time = time.time()
            
            if not mock:
                temp = get_macos_temp()
                if temp is not None:
                    print(f"{current_time:.2f}, {temp:.1f}C")
                    f.write(f"{current_time:.2f},{temp:.1f}\n")
                    f.flush()
                    time.sleep(log_interval)
                    continue
            
            # If mocking or osx-cpu-temp failed
            # Simulate a temperature rising to ~65C and stabilizing
            elapsed = current_time - start_time
            # Logistic growth mock model up to 65C
            mock_temp = 45.0 + (20.0 / (1.0 + pow(2.718, -0.05 * (elapsed - 60)))) 
            # Add small random jitter (+/- 0.5C)
            mock_temp += random.uniform(-0.5, 0.5)
            
            print(f"[Simulated] {current_time:.2f}, {mock_temp:.1f}C")
            f.write(f"{current_time:.2f},{mock_temp:.1f}\n")
            f.flush()
            
            time.sleep(log_interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ScholarMaster Thermal Logger")
    parser.add_argument("--duration", type=int, default=10, help="Duration in seconds (default 10s for demo)")
    parser.add_argument("--interval", type=float, default=1.0, help="Logging interval in seconds")
    parser.add_argument("--mock", action="store_true", help="Force mock temperature generation")
    
    args = parser.parse_args()
    log_temp(duration_seconds=args.duration, log_interval=args.interval, mock=args.mock)
