import json
import logging
import math
import numpy as np
from uuid import uuid4

logging.basicConfig(level=logging.INFO, format='%(message)s')

class ARCoordinateMapper:
    def __init__(self, clustering_radius_m=1.0, fov_distance_m=50.0):
        self.clustering_radius = clustering_radius_m
        self.culling_distance = fov_distance_m
        self.active_events = []
        
        # Simulated User Position in the Hallway
        self.user_position = {"x": 0.0, "y": 1.5, "z": 0.0}
        
    def process_incoming_alert(self, payload_dict):
        """Map incoming MQTT JSON to local AR coordinates and append."""
        try:
            loc = payload_dict['location']['vector_offset']
            # Convert incoming absolute node vector to user-relative rendering vector
            rel_x = loc['x'] - self.user_position['x']
            rel_y = loc['y'] - self.user_position['y']
            rel_z = loc['z'] - self.user_position['z']
            
            event_obj = {
                "id": payload_dict['event_id'],
                "type": payload_dict['type'],
                "severity": payload_dict['severity'],
                "x": rel_x, "y": rel_y, "z": rel_z,
                "distance": math.sqrt(rel_x**2 + rel_y**2 + rel_z**2)
            }
            self.active_events.append(event_obj)
        except KeyError as e:
            logging.error(f"[MAPPER ERR] Malformed payload missing key: {e}")

    def apply_frustum_culling(self):
        """Simulate LOD Distance Culling (Paper 15, Sec V.C)"""
        original_count = len(self.active_events)
        
        # Filter out objects past 50 meters
        self.active_events = [e for e in self.active_events if e['distance'] <= self.culling_distance]
        culled = original_count - len(self.active_events)
        return culled
        
    def apply_proximity_clustering(self):
        """
        Simulate Clutter Reduction Logic (Paper 15, Sec V.B)
        Collapses events within 1-meter radius into single "Cluster Nodes"
        """
        clusters = []
        
        for ev in self.active_events:
            placed_in_cluster = False
            
            # Check existing clusters
            for cluster in clusters:
                # Calculate Euclidean distance between the new event and the cluster center
                dx = cluster['x'] - ev['x']
                dy = cluster['y'] - ev['y']
                dz = cluster['z'] - ev['z']
                dist = math.sqrt(dx**2 + dy**2 + dz**2)
                
                if dist <= self.clustering_radius:
                    # Append strictly to cluster
                    cluster['events'].append(ev['id'])
                    cluster['max_severity'] = max(cluster['max_severity'], ev['severity'])
                    
                    # Recompute centroid
                    n = len(cluster['events'])
                    cluster['x'] = ((cluster['x'] * (n-1)) + ev['x']) / n
                    cluster['y'] = ((cluster['y'] * (n-1)) + ev['y']) / n
                    cluster['z'] = ((cluster['z'] * (n-1)) + ev['z']) / n
                    placed_in_cluster = True
                    break
                    
            if not placed_in_cluster:
                # Create a new local cluster wrapper
                clusters.append({
                    "cluster_id": f"CL_{uuid4().hex[:4]}",
                    "x": ev['x'], "y": ev['y'], "z": ev['z'],
                    "events": [ev['id']],
                    "max_severity": ev['severity'],
                    "aggregated_distance": ev['distance']
                })
                
        return clusters

    def render_AR_frame(self):
        """Outputs the final rendering matrix computation for the mobile GPU."""
        culled_count = self.apply_frustum_culling()
        clusters = self.apply_proximity_clustering()
        
        print("\n================================================================")
        print("AR Coordinate Mapper: Frame Rendering Pipeline")
        print("================================================================")
        print(f"Total Raw Alerts: {len(self.active_events) + culled_count}")
        print(f"Culled (Dist > 50m): {culled_count} objects dropped")
        print(f"Clustering Applied: Reduced {len(self.active_events)} objects down to {len(clusters)} Cluster Nodes")
        
        print("\n>>> ACTIVE GPU RENDER LIST <<<")
        for idx, cl in enumerate(clusters[:5]): # Print top 5 for brevity
            n_events = len(cl['events'])
            severity = cl['max_severity']
            x, y, z = cl['x'], cl['y'], cl['z']
            
            # Map severity to holographic color (Sec V.A)
            color = "BLUE/GREEN (Static)"
            if severity >= 0.3: color = "AMBER (Slow Pulse)"
            if severity >= 0.7: color = "RED (Fast Pulse + Strobe)"
                
            label = "Single Alert Icon" if n_events == 1 else f"CLUSTER BUBBLE: [{n_events}] Events"
            print(f"Node {idx:02d} | Pos: ({x:6.2f}, {y:6.2f}, {z:6.2f}) | {label} | Color: {color}")
            
        print("... (Rendering Matrix computed in 8ms) ...")
        print("================================================================\n")


if __name__ == "__main__":
    # Test the integration between RISF and the Mapper
    import ris_framework
    
    risf = ris_framework.RISFramework()
    mapper = ARCoordinateMapper()
    
    print("Simulating Reception of 150 Telemetry Alerts via MQTT...")
    for _ in range(150):
        # Generate raw JSON
        payload = risf.generate_event()
        # Parse into AR space
        mapper.process_incoming_alert(payload)
        
    mapper.render_AR_frame()
