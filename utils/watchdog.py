#!/usr/bin/env python3
"""
Paper 11: Hardware Watchdog Timer Module
=========================================
Writes heartbeat to /dev/watchdog to prevent hardware-forced resets.
Compatible with BCM2711 (Raspberry Pi 4) and similar ARM SoCs.
"""

import os
import time
import logging
import threading
from pathlib import Path

logger = logging.getLogger(__name__)


class HardwareWatchdog:
    """
    Hardware Watchdog Timer Manager.
    
    Writes periodic heartbeat to /dev/watchdog. If the application hangs
    and fails to write within the timeout window, the watchdog hardware
    will force a system reset.
    """
    
    def __init__(self, device_path: str = "/dev/watchdog", interval: int = 10):
        """
        Initialize watchdog.
        
        Args:
            device_path: Path to watchdog device (usually /dev/watchdog)
            interval: Heartbeat interval in seconds (must be < hardware timeout)
        """
        self.device_path = Path(device_path)
        self.interval = interval
        self.running = False
        self.thread = None
        self._last_heartbeat = 0
        
    def start(self):
        """Start watchdog heartbeat thread."""
        if not self.device_path.exists():
            logger.warning(f"⚠️  Watchdog device {self.device_path} not found. "
                         f"Running without hardware watchdog protection.")
            logger.info("   To enable on Raspberry Pi, add 'dtparam=watchdog=on' "
                       "to /boot/config.txt")
            return
        
        try:
            # Test write access
            with open(self.device_path, 'wb') as f:
                f.write(b'\x00')
            
            self.running = True
            self.thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self.thread.start()
            logger.info(f"✅ Hardware watchdog started (interval={self.interval}s)")
            
        except PermissionError:
            logger.error(f"❌ Permission denied: {self.device_path}. Run as root or "
                        f"add user to 'watchdog' group.")
        except Exception as e:
            logger.error(f"❌ Failed to start watchdog: {e}")
    
    def _heartbeat_loop(self):
        """Continuous heartbeat thread."""
        while self.running:
            try:
                with open(self.device_path, 'wb') as f:
                    f.write(b'\x00')  # Write any byte to keep watchdog alive
                
                self._last_heartbeat = time.time()
                logger.debug(f"💓 Watchdog heartbeat sent")
                
            except Exception as e:
                logger.error(f"❌ Watchdog write failed: {e}")
            
            time.sleep(self.interval)
    
    def stop(self):
        """Stop watchdog (WARNING: System will reset if watchdog is enabled!)."""
        if self.running:
            self.running = False
            if self.thread:
                self.thread.join(timeout=2)
            logger.warning("⚠️  Watchdog stopped. System may reset if watchdog was active.")
    
    def get_status(self) -> dict:
        """Get watchdog status."""
        return {
            "enabled": self.running,
            "device": str(self.device_path),
            "interval_s": self.interval,
            "last_heartbeat": self._last_heartbeat,
            "seconds_since_heartbeat": time.time() - self._last_heartbeat if self._last_heartbeat else None
        }


# Singleton instance for global access
_watchdog_instance = None


def get_watchdog() -> HardwareWatchdog:
    """Get global watchdog instance."""
    global _watchdog_instance
    if _watchdog_instance is None:
        _watchdog_instance = HardwareWatchdog()
    return _watchdog_instance


if __name__ == "__main__":
    # Test watchdog functionality
    logging.basicConfig(level=logging.DEBUG)
    
    print("🐕 Testing Hardware Watchdog Module")
    print("=" * 50)
    
    wd = HardwareWatchdog(interval=5)
    wd.start()
    
    if wd.running:
        print("✅ Watchdog active. Monitoring for 30 seconds...")
        time.sleep(30)
        print(f"📊 Status: {wd.get_status()}")
        wd.stop()
    else:
        print("⚠️  Watchdog not available (device not found or no permissions)")
        print("   This is normal on non-embedded systems.")
