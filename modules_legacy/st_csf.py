import math
import time
import logging
import random
from typing import Dict, Tuple, Optional, Any
from .state_manager import RedisStateManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ST-CSF")

class SpatiotemporalCSF:
    """
    Spatiotemporal Constraint Satisfaction Framework (ST-CSF) - Paper 7.
    A decoupled 'Logic Layer' that verifies event validity without accessing raw sensor data.
    
    Implements:
    1. Teleportation Heuristic (Impossible Travel Check)
    2. Conflict Resolution Matrix (Weighted Voting)
    3. Constraint Satisfaction (via OR-Tools or Heuristic Fallback)
    """
    
    def __init__(self, state_manager: RedisStateManager = None):
        # Dependence Injection for State Manager
        self.state = state_manager if state_manager else RedisStateManager()
        
        # Paper 7 Constants
        self.MAX_VELOCITY = 5.0  # m/s (Upper bound for human run)
        self.TIME_WINDOW = 300   # 5 minutes (+/- delta)
        
        # Conceptual Campus Topology (Coordinates in meters)
        # In a real deployment, this would load from a GeoJSON file
        self.ZONE_COORDS = {
            "Zone_1": (0, 0),        # Math Class (Origin)
            "Zone_2": (100, 0),      # Physics Lab (100m East)
            "Zone_3": (0, 100),      # Library (100m North)
            "Zone_4": (500, 500),    # Canteen (Far corner)
            "Main Hall": (50, 50),   # Central
            "Library": (0, 100),     # Alias
            "Canteen": (500, 500),   # Alias
            "Lab 1": (100, 0)        # Alias
        }

    def _calculate_distance(self, zone1: str, zone2: str) -> float:
        """Euclidean distance between two campus zones (meters)"""
        p1 = self.ZONE_COORDS.get(zone1, (0,0))
        p2 = self.ZONE_COORDS.get(zone2, (0,0))
        return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

    def validate_event(self, event: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Main entry point for Logic Layer Validation.
        Executes the O(1) Constraint Pipeline.
        
        Args:
            event: Dict with keys 'student_id', 'timestamp', 'zone'
            
        Returns:
            (is_valid: bool, reason: str)
        """
        student_id = event.get('student_id')
        current_time = float(event.get('timestamp', time.time()))
        current_zone = event.get('zone')
        
        if not student_id or not current_zone:
            return False, "INVALID_FORMAT"

        # -----------------------------------------------------
        # CONSTRAINT 1: Impossible Travel (The "Teleportation Heuristic")
        # -----------------------------------------------------
        state_key = f"state:{student_id}"
        prev_state = self.state.get(state_key)
        
        # Paper 4: Zone Weights for Conflict Resolution (Algorithm 2)
        # Higher priority = Academic zones. Lower = Leisure/Transit.
        ZONE_WEIGHTS = {
            "Lab": 0.9,
            "Classroom": 0.8, 
            "Library": 0.5,
            "Canteen": 0.4,
            "Corridor": 0.2,
            "Zone_1": 0.8, # Mapped to Math Class
            "Zone_2": 0.9, # Mapped to Physics Lab
            "Zone_3": 0.5, # Mapped to Library
            "Zone_4": 0.4  # Mapped to Canteen
        }

        if prev_state:
            prev_time = float(prev_state['timestamp'])
            prev_zone = prev_state['zone']
            
            time_diff = current_time - prev_time
            
            # Case A: Simultaneous Events (Conflict Resolution)
            if time_diff <= 0.5: # 500ms tolerance
                if prev_zone != current_zone:
                    # ALGORITHM 2: Conflict Resolution Matrix (Weighted Voting)
                    w_prev = ZONE_WEIGHTS.get(prev_zone, 0.5)
                    w_curr = ZONE_WEIGHTS.get(current_zone, 0.5)
                    
                    # Heuristic: Confidence assumed 1.0 for simplicity, or could pass in event['confidence']
                    score_prev = w_prev
                    score_curr = w_curr
                    
                    if score_curr > score_prev:
                        logger.info(f"[CONFLICT] Resolved: {current_zone} ({score_curr}) > {prev_zone} ({score_prev}). State Updated.")
                        # Allow update (current wins)
                        pass 
                    else:
                        logger.info(f"[CONFLICT] Resolved: {prev_zone} ({score_prev}) >= {current_zone} ({score_curr}). Event Ignored.")
                        return True, "CONFLICT_RESOLVED_IGNORED" # Treat as valid but ignored (don't alert)
                else:
                    return True, "DUPLICATE_EVENT"
            
            # Case B: Velocity Check with PCVF (Debounce)
            else:
                dist = self._calculate_distance(prev_zone, current_zone)
                velocity = dist / time_diff
                
                if velocity > self.MAX_VELOCITY:
                    # PAPER 4: Persistent Constraint Violation Filtering (PCVF)
                    # Don't alert immediately. Wait for persistence > 30s (5s for Demo).
                    
                    violation_key = f"violation:{student_id}"
                    violation_start = self.state.get(violation_key)
                    
                    current_violation_time = current_time
                    
                    if not violation_start:
                        # Start of possible violation
                        self.state.set(violation_key, {'start_time': current_time}, ex=60)
                        logger.warning(f"[PCVF] Potential violation detected for {student_id}. Debouncing...")
                        return True, "WARNING_POTENTIAL_VIOLATION" # Suppress alert
                    else:
                        # Check persistence
                        start_t = float(violation_start['start_time'])
                        duration = current_violation_time - start_t
                        
                        DEBOUNCE_THRESHOLD = 5.0 # Reduced from 30s for Demo responsiveness
                        
                        if duration > DEBOUNCE_THRESHOLD:
                            logger.error(f"[PCVF] CONFIRMED VIOLATION for {student_id}. Persisted {duration:.1f}s.")
                            return False, f"IMPOSSIBLE TRAVEL (CONFIRMED): v={velocity:.1f} m/s"
                        else:
                            logger.warning(f"[PCVF] Pending violation for {student_id}. Duration: {duration:.1f}s")
                            return True, "WARNING_PENDING_VIOLATION"

                else:
                    # Velocity OK - Clear any pending violation
                    self.state.delete(f"violation:{student_id}")

        # -----------------------------------------------------
        # CONSTRAINT 2: Schedule & Capacity (CSP Logic)
        # -----------------------------------------------------
        # Note: In a full integration, we'd pass the schedule context here.
        # For this standalone module, we focus on the spatiotemporal integrity.
        
        # Update State (Write-Through Pattern)
        new_state = {
            'timestamp': current_time,
            'zone': current_zone,
            'last_valid': True
        }
        # Expire state after 20 minutes to free memory (garbage collection)
        self.state.set(state_key, new_state, ex=1200) 
        
        return True, "VALID_TRANSITION"

    def solve_csp_schedule(self, student_id: str, time_slot: str, possible_rooms: list) -> str:
        """
        Uses Google OR-Tools to solve the 'Where should X be?' problem
        treating it as a local constraint satisfaction problem.
        
        (Paper 7 Claim: "We model the schedule as a CSP")
        """
        try:
            from ortools.sat.python import cp_model
            model = cp_model.CpModel()
            
            # Toy implementation of the solver logic claimed in the paper
            # Variables: Boolean 'is_in_room_i'
            # Constraint: Sum(is_in_room) == 1 (Must be in exactly one room)
            
            room_vars = {}
            for room in possible_rooms:
                room_vars[room] = model.NewBoolVar(f'in_{room}')
                
            model.Add(sum(room_vars.values()) == 1)
            
            # Solver would typically add strict constraints from timetable DB here
            # For prototype, we assume the first room is the valid one
            
            solver = cp_model.CpSolver()
            status = solver.Solve(model)
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                return possible_rooms[0] # Just a stub to prove import works
                
        except ImportError:
            # Fallback for environments where OR-Tools is not installed
            # This ensures "Freeze-Ready" stability even if dependency is missing
            pass
            
        return possible_rooms[0] if possible_rooms else "Unknown"
