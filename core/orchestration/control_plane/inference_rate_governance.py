import time
import logging
from typing import Dict, Any, Tuple

class IRGScheduler:
    """
    Paper 9: Inference Rate Governance (IRG) Scheduler
    Dynamically activates/deactivates perception modules based on lecture phase 
    and operational budgets to suppress unjustified compute cycles (Ethical Compute).
    """
    def __init__(self, lecture_duration_minutes: int = 60):
        self.lecture_duration = lecture_duration_minutes
        self.current_minute = 0
        
        # Operational Budgets (Max triggers per day/session)
        self.budgets = {
            "heavy_vision": 100,
            "asr": 200,
            "pose": 5000 # Lightweight
        }
        
        # Tracking metrics for Paper 9 eval
        self.metrics = {
            "scheduled_cycles": { "heavy_vision": 0, "asr": 0, "pose": 0 },
            "executed_cycles": { "heavy_vision": 0, "asr": 0, "pose": 0 },
            "justified_cycles": 0,
            "active_minutes": { "heavy_vision": 0, "asr": 0, "pose": 0 }
        }
        
        # Base framerates (cycles per minute)
        self.BASE_FPS_P_MIN = 30 * 60
        
    def determine_phase(self, minute: int) -> str:
        """Heuristic for determining logical lecture phase based on time contour."""
        if minute < 10:
            return "ATTENDANCE" # 0-10 min
        elif minute < 40:
            return "VIDEO_PLAYBACK" # 10-40 min (low active participation)
        elif minute < 55:
            return "QA_SESSION"   # 40-55 min (high engagement)
        else:
            return "DISMISSAL"    # 55-60 min
            
    def step_minute(self, phase_override: str = None) -> Dict[str, bool]:
        """
        Advances the scheduler by one minute, calculating duty cycles and suppressing modules.
        Returns the active state of each module for this minute.
        """
        self.current_minute += 1
        phase = phase_override or self.determine_phase(self.current_minute)
        
        # State Vector: [Heavy Vision (Face), ASR (Audio), Pose (Lightweight)]
        active = { "heavy_vision": False, "asr": False, "pose": False }
        is_justified = False
        
        if phase == "ATTENDANCE":
            active["heavy_vision"] = True
            active["pose"] = True
            is_justified = True
        elif phase == "VIDEO_PLAYBACK":
            # Suppress heavy sensing
            active["pose"] = True 
        elif phase == "QA_SESSION":
            active["pose"] = True
            active["asr"] = True
            is_justified = True
        elif phase == "DISMISSAL":
            pass # All suppressed
            
        # Check budgets & update metrics
        for module, is_active in active.items():
            self.metrics["scheduled_cycles"][module] += self.BASE_FPS_P_MIN
            
            if is_active:
                if self.budgets[module] > 0:
                    self.budgets[module] -= 1
                    self.metrics["executed_cycles"][module] += self.BASE_FPS_P_MIN
                    self.metrics["active_minutes"][module] += 1
                    
                    if is_justified:
                        self.metrics["justified_cycles"] += self.BASE_FPS_P_MIN
                else:
                    logging.warning(f"[IRG] budget exhausted for {module}. Forced suppression.")
                    active[module] = False
                    
        return active
        
    def compute_metrics(self) -> Dict[str, float]:
        """
        Calculates the 3 functional orchestration metrics defined in Paper 9.
        """
        # 1. Inference Suppression Ratio (ISR)
        total_scheduled = sum(self.metrics["scheduled_cycles"].values())
        total_executed = sum(self.metrics["executed_cycles"].values())
        suppressed = total_scheduled - total_executed
        
        isr = (suppressed / total_scheduled) * 100 if total_scheduled > 0 else 0
        
        # 2. Ethical Compute Utilization (ECU)
        ecu = (self.metrics["justified_cycles"] / total_executed) * 100 if total_executed > 0 else 0
        
        # 3. Context-Aware Duty Cycle (CADC)
        cadc = {
            mod: (mins / self.lecture_duration) * 100 
            for mod, mins in self.metrics["active_minutes"].items()
        }
        
        return {
            "ISR_Total": isr,
            "ISR_HeavyVision": ( (self.metrics["scheduled_cycles"]["heavy_vision"] - self.metrics["executed_cycles"]["heavy_vision"]) / self.metrics["scheduled_cycles"]["heavy_vision"] ) * 100,
            "ECU": ecu,
            "CADC": cadc
        }
