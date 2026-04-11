import time
import logging
from enum import Enum, auto
from typing import Dict, Optional

class SystemState(Enum):
    NORMAL = auto()
    DEGRADED = auto()
    SAFE = auto()

class ModuleWatchdog:
    """Tracks heartbeats for specific perception modules."""
    def __init__(self, name: str, timeout_sec: float = 5.0):
        self.name = name
        self.timeout_sec = timeout_sec
        self.last_heartbeat = time.time()
        self.is_healthy = True
        
    def ping(self):
        self.last_heartbeat = time.time()
        self.is_healthy = True
        
    def check_health(self) -> bool:
        if time.time() - self.last_heartbeat > self.timeout_sec:
            if self.is_healthy:
                logging.warning(f"[WATCHDOG] Module {self.name} TIMEOUT (> {self.timeout_sec}s). Marking as failed.")
                self.is_healthy = False
            return False
        return True

class OrchestrationStateMachine:
    """
    Paper 9: Failure Containment State Machine.
    Ensures gracefully degraded operations and explicit isolation between 
    perception failure and governance logic.
    """
    def __init__(self):
        self.state = SystemState.NORMAL
        self.watchdogs: Dict[str, ModuleWatchdog] = {
            "heavy_vision": ModuleWatchdog("Heavy_Vision", timeout_sec=5.0),
            "pose": ModuleWatchdog("Pose_Estimation", timeout_sec=5.0),
            "asr": ModuleWatchdog("Audio_Semantics", timeout_sec=3.0)
        }
        
        # Metrics
        self.failures_caught = 0
        self.failures_cascaded = 0 # Simulating Layer Isolation Factor
        self.recovery_times = []
        
    def pulse_module(self, module_name: str):
        if module_name in self.watchdogs:
            self.watchdogs[module_name].ping()
            
    def evaluate_state(self) -> SystemState:
        """
        Algorithm 1: Evaluate Watchdogs and Transition State Machine
        """
        vision_health = self.watchdogs["heavy_vision"].check_health()
        pose_health = self.watchdogs["pose"].check_health()
        asr_health = self.watchdogs["asr"].check_health()
        
        previous_state = self.state
        
        if not vision_health and not pose_health:
            # Both vision layers failed -> SAFE mode (Audio/Occupancy only)
            self.state = SystemState.SAFE
            if previous_state != SystemState.SAFE:
                logging.error("[CONTAINMENT] Critical vision failure. Transitioning to SAFE Mode.")
                self.failures_caught += 1
                
        elif not vision_health and pose_health:
            # Heavy vision OOM/Crashed -> DEGRADED mode (Pose + Audio)
            self.state = SystemState.DEGRADED
            if previous_state != SystemState.DEGRADED:
                logging.warning("[CONTAINMENT] Heavy Vision failed. Transitioning to DEGRADED Mode (Pose-Only).")
                self.failures_caught += 1
                
        elif vision_health and pose_health:
             self.state = SystemState.NORMAL
             if previous_state != SystemState.NORMAL:
                 logging.info("[CONTAINMENT] All sensors operating. Transitioning to NORMAL Mode.")
                 
        return self.state
        
    def calculate_lif(self) -> float:
        """Calculate Layer Isolation Factor (LIF) metric."""
        total = self.failures_caught + self.failures_cascaded
        if total == 0:
            return 100.0
        return (self.failures_caught / total) * 100.0
