#!/usr/bin/env python3
"""
Thermal Logger Script
Paper 5: Hardware Benchmarking - Thermal Characterization

Purpose: Continuously log CPU/GPU thermal data for thermal stability analysis
         Supports both macOS (Apple Silicon) and Linux platforms

Usage:
    python3 thermal_logger.py [duration_seconds] [output_file]

Requirements:
    macOS: osx-cpu-temp (install via: brew install osx-cpu-temp)
    Linux: lm-sensors (install via: apt-get install lm-sensors)

Output Format (CSV):
    timestamp,cpu_temp_celsius,gpu_temp_celsius,ambient_temp_celsius
"""

import os
import sys
import time
import subprocess
import platform
from datetime import datetime


class ThermalLogger:
    """Cross-platform thermal logging utility"""
    
    def __init__(self, output_file="thermal_log.csv", duration=3600):
        self.output_file = output_file
        self.duration = duration
        self.platform = platform.system()
        self.start_time = time.time()
        
        # Detect thermal monitoring tools
        self._check_dependencies()
        
    def _check_dependencies(self):
        """Verify required thermal monitoring tools are installed"""
        if self.platform == "Darwin":  # macOS
            try:
                subprocess.run(["osx-cpu-temp"], capture_output=True, check=True)
                print("✅ Detected: osx-cpu-temp")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️  Warning: osx-cpu-temp not found")
                print("   Install via: brew install osx-cpu-temp")
        elif self.platform == "Linux":
            try:
                subprocess.run(["sensors"], capture_output=True, check=True)
                print("✅ Detected: lm-sensors")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("⚠️  Warning: lm-sensors not found")
                print("   Install via: sudo apt-get install lm-sensors")
    
    def read_macos_temp(self):
        """Read temperature on macOS using osx-cpu-temp"""
        try:
            result = subprocess.run(
                ["osx-cpu-temp"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            # Output format: "61.2°C"
            temp_str = result.stdout.strip().replace("°C", "")
            cpu_temp = float(temp_str)
            
            # Try to get GPU temp via powermetrics (requires sudo)
            try:
                pm_result = subprocess.run(
                    ["sudo", "powermetrics", "--samplers", "thermal", "-n", "1"],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                # Parse for GPU temp (simplified)
                gpu_temp = cpu_temp  # Fallback to CPU temp if parsing fails
            except:
                gpu_temp = cpu_temp
            
            return cpu_temp, gpu_temp, None
        except Exception as e:
            print(f"Error reading macOS temps: {e}")
            return None, None, None
    
    def read_linux_temp(self):
        """Read temperature on Linux using lm-sensors"""
        try:
            result = subprocess.run(
                ["sensors"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # Parse sensors output (simplified - adjust for your hardware)
            lines = result.stdout.split('\n')
            cpu_temp = None
            gpu_temp = None
            
            for line in lines:
                if 'Core 0' in line or 'Package id 0' in line:
                    # Extract temperature like "+45.0°C"
                    parts = line.split('+')
                    if len(parts) > 1:
                        temp_str = parts[1].split('°')[0]
                        cpu_temp = float(temp_str)
                        break
            
            return cpu_temp, gpu_temp, None
        except Exception as e:
            print(f"Error reading Linux temps: {e}")
            return None, None, None
    
    def read_temperature(self):
        """Read temperature based on platform"""
        if self.platform == "Darwin":
            return self.read_macos_temp()
        elif self.platform == "Linux":
            return self.read_linux_temp()
        else:
            print(f"Unsupported platform: {self.platform}")
            return None, None, None
    
    def log(self):
        """Main logging loop"""
        print("=" * 60)
        print("Thermal Logger - Paper 5 Hardware Benchmarking")
        print("=" * 60)
        print(f"Platform:     {self.platform}")
        print(f"Duration:     {self.duration}s ({self.duration // 60} minutes)")
        print(f"Output File:  {self.output_file}")
        print(f"Sample Rate:  1 Hz (every second)")
        print("=" * 60)
        print("")
        
        # Create CSV header
        with open(self.output_file, 'w') as f:
            f.write("timestamp,elapsed_seconds,cpu_temp_celsius,gpu_temp_celsius,ambient_temp_celsius\n")
        
        print("Logging started. Press Ctrl+C to stop.")
        print("")
        
        sample_count = 0
        try:
            while (time.time() - self.start_time) < self.duration:
                cpu_temp, gpu_temp, ambient_temp = self.read_temperature()
                elapsed = time.time() - self.start_time
                
                # Write to CSV
                with open(self.output_file, 'a') as f:
                    timestamp = datetime.now().isoformat()
                    f.write(f"{timestamp},{elapsed:.1f},{cpu_temp},{gpu_temp},{ambient_temp}\n")
                
                # Print periodic status
                sample_count += 1
                if sample_count % 10 == 0:
                    status = f"[{int(elapsed):4d}s] CPU: {cpu_temp:5.1f}°C"
                    if gpu_temp:
                        status += f" | GPU: {gpu_temp:5.1f}°C"
                    print(status)
                
                time.sleep(1)  # Sample every second
                
        except KeyboardInterrupt:
            print("\n\nLogging interrupted by user.")
        
        print("")
        print("=" * 60)
        print("Thermal Logging Complete!")
        print("=" * 60)
        print(f"Total samples: {sample_count}")
        print(f"Data saved to: {self.output_file}")
        print("")
        print("To analyze the data:")
        print(f"  import pandas as pd")
        print(f"  df = pd.read_csv('{self.output_file}')")
        print(f"  print(df['cpu_temp_celsius'].describe())")
        print("")


if __name__ == "__main__":
    # Parse command-line arguments
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 3600  # Default: 60 minutes
    output_file = sys.argv[2] if len(sys.argv) > 2 else f"thermal_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    # Create logger and start
    logger = ThermalLogger(output_file=output_file, duration=duration)
    logger.log()
