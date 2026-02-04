import time
import datetime
from enum import Enum
import threading

class SystemState(Enum):
    NORMAL = "NORMAL"         # All modules active
    DEGRADED = "DEGRADED"     # Biometrics disabled (failover, budget, or low priority)
    SAFE = "SAFE"             # Only Safety sensors (Occupancy/Audio) active

class GovernanceEngine:
    """
    Implements the 'Hierarchical Control Plane' and 'Inference Rate Governance' (IRG)
    described in the Orchestration Paper.
    
    Responsibilities:
    1. Manage System State (NORMAL -> DEGRADED -> SAFE) based on health.
    2. Enforce Privacy Budgets (Max 100 biometric captures/day).
    3. Decide Inference Strategy (which modules run) based on Context.
    """
    
    def __init__(self, max_captures_per_day=100):
        self.state = SystemState.NORMAL
        self.max_biometric_captures = max_captures_per_day
        self.current_biometric_captures = 0
        self.last_reset = datetime.date.today()
        
        # Watchdog Timers (Last heartbeat timestamp)
        self.watchdogs = {
            "face_module": time.time(),
            "audio_module": time.time(),
            "pose_module": time.time()
        }
        
        # Timeout Thresholds (Paper Table I)
        self.timeouts = {
            "face_module": 5.0,  # 5s failover
            "audio_module": 3.0, # 3s timeout
            "pose_module": 2.0   # 2s timeout
        }
        
        # IRG Metrics
        self.metrics = {
            "total_cycles": 0,
            "suppressed_cycles": 0,
            "justified_cycles": 0
        }

        print("⚖️  GovernanceEngine Initialized (IRG Active)")
        
    def heartbeat(self, module_name):
        """Update heartbeat for a module."""
        self.watchdogs[module_name] = time.time()
        
    def _check_health(self):
        """
        Internal Watchdog Logic (Algorithm 1).
        Transitions state if modules time out.
        """
        now = time.time()
        
        # Check Face Module
        if now - self.watchdogs["face_module"] > self.timeouts["face_module"]:
            if self.state == SystemState.NORMAL:
                print("⚠️ WATCHDOG: Face Module Unresponsive! Transitioning to DEGRADED.")
                self.state = SystemState.DEGRADED
                
        # Check Pose Module (Critical fallback)
        if now - self.watchdogs["pose_module"] > self.timeouts["pose_module"]:
           print("🚨 WATCHDOG: Pose Module Unresponsive! Transitioning to SAFE.")
           self.state = SystemState.SAFE
           
    def _check_privacy_budget(self):
        """Resets budget daily and enforces limit."""
        today = datetime.date.today()
        if today > self.last_reset:
            self.current_biometric_captures = 0
            self.last_reset = today
            
        if self.current_biometric_captures >= self.max_biometric_captures:
            if self.state == SystemState.NORMAL:
                print("🔒 PRIVACY BUDGET EXHAUSTED. Disabling Biometrics.")
                self.state = SystemState.DEGRADED
                
    def get_inference_strategy(self, context_state):
        """
        IRG Core Logic: Decides what runs this frame.
        
        Args:
            context_state (dict): Current understanding (e.g., {'phase': 'Q&A', 'active_speech': True})
            
        Returns:
            dict: { 'enable_face': bool, 'enable_audio': bool, 'enable_pose': bool }
        """
        self._check_health()
        self._check_privacy_budget()
        
        self.metrics["total_cycles"] += 1
        
        # Default Strategy based on State
        strategy = {
            "enable_face": False,
            "enable_audio": False,
            "enable_pose": True # Always run pose unless SAFE mode fails
        }
        
        # SAFE Mode: Only bare minimum
        if self.state == SystemState.SAFE:
            strategy["enable_pose"] = False # Even pose failed
            strategy["enable_audio"] = True # Keep audio for screams
            return strategy
            
        # DEGRADED Mode: No heavy biometrics
        if self.state == SystemState.DEGRADED:
            strategy["enable_face"] = False
            strategy["enable_audio"] = True
            return strategy
            
        # NORMAL Mode: Apply Inference Rate Governance (IRG)
        # Evaluate Justification
        justification = False
        
        # 1. Phase-based Activation
        phase = context_state.get("phase", "Lecture")
        if phase in ["Q&A", "Attendance", "Discussion"]:
            justification = True
            
        # 2. Activity-based Activation
        if context_state.get("is_speaking", False) or context_state.get("hand_raised", False):
            justification = True
            
        if justification:
            strategy["enable_face"] = True
            strategy["enable_audio"] = True
            self.metrics["justified_cycles"] += 1
            
            # Increment budget usage if face active
            self.current_biometric_captures += 1
        else:
            # Suppress Biometrics
            strategy["enable_face"] = False
            strategy["enable_audio"] = True # Keep audio for wake-word/safety
            self.metrics["suppressed_cycles"] += 1
            
        return strategy

    def get_metrics(self):
        """Returns ISR and ECU metrics for reporting."""
        total = self.metrics["total_cycles"] if self.metrics["total_cycles"] > 0 else 1
        
        isr = (self.metrics["suppressed_cycles"] / total) * 100
        ecu = (self.metrics["justified_cycles"] / total) * 100
        
        return {
            "ISR": isr,
            "ECU": ecu,
            "State": self.state.value
        }
