# ScholarMasterEngine: Unified Integration Architecture (20 Papers)

This document visualizes the cohesive, event-driven architecture that unifies the 20 distinct research papers of the ScholarMaster series into a single, conflict-free "System of Systems."

## The "Dependency Inversion" Integration Strategy

The core of the ScholarMaster integration strategy relies on **Dependency Inversion** and the **UnifiedOrchestrator** acting as a central Event Bus. 

Instead of Paper 2 (Fusion) explicitly depending on the code of Paper 3 (Pose), both papers depend on a shared abstraction: the `CrossPaperEvent`. 
- **Upstream (Sensing):** Papers 1-6 act as isolated producers. They process raw physical data (video, audio) and publish anonymous, validated events to the bus. They immediately securely delete the raw data.
- **The Orchestrator:** Validates the payload against strict privacy allowlists before routing.
- **Downstream (Governance, Learning, UI):** Papers 7-20 act as consumers. They subscribe to specific event types, completely agnostic to how the events were generated.

This architecture ensures that implementing a new paper (e.g., adding Federated Learning in Paper 12) requires zero modifications to the core sensing logic, preventing architectural degradation.

## Unified Architecture Diagram

```mermaid
graph TD
    %% Define styles
    classDef sensing fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef orchestrator fill:#f3e5f5,stroke:#4a148c,stroke-width:3px;
    classDef governance fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px;
    classDef learning fill:#fff3e0,stroke:#e65100,stroke-width:2px;
    classDef observer fill:#eceff1,stroke:#263238,stroke-width:2px;
    
    %% Upstream Sensing Papers
    subgraph SensingLayer ["Sensing & Abstraction Layer (Papers 1-6)"]
        P1["Paper 1: Adaptive Face ID"]:::sensing
        P3["Paper 3: Pose Vectorization"]:::sensing
        P6["Paper 6: Acoustic Sentinel"]:::sensing
        P5["Paper 5: Hardware Profiling"]:::sensing
    end

    %% Central Orchestrator
    subgraph CoreOrchestrator ["Central Event Bus (UnifiedOrchestrator)"]
        EB{"CrossPaperEvent Router
        (Strict Privacy Allowlist)"}:::orchestrator
    end

    %% Event Types
    E1((FACE_<br>DETECTED))
    E2((POSE_<br>DETECTED))
    E3((AUDIO_<br>ANOMALY))
    
    %% Downstream Governance
    subgraph GovernanceLayer ["Governance & Audit Layer (Papers 7-11)"]
        P7["Paper 7: Spatiotemporal Constraints"]:::governance
        P8["Paper 8: Blockchain Audit"]:::governance
        P4["Paper 4: Context Awareness"]:::governance
        P2["Paper 2: Multi-Modal Fusion"]:::governance
    end

    %% Downstream Federated Learning
    subgraph FLLayer ["Federated Learning Layer (Papers 12-14)"]
        P12["Paper 12: Edge Topology"]:::learning
        P13["Paper 13: Local FL Training"]:::learning
        P14["Paper 14: Global Aggregation"]:::learning
    end

    %% UI and Observer
    subgraph UILayer ["Visualization & Validation Layer (Papers 15-20)"]
        P15["Paper 15: AR Visualization"]:::observer
        P16["Paper 16: Read-Only Observer"]:::observer
    end

    %% Connections Sensing -> Events
    P1 --"Publishes"--> E1
    P3 --"Publishes (Vectors Only)"--> E2
    P6 --"Publishes"--> E3
    
    %% Events -> Orchestrator
    E1 --> EB
    E2 --> EB
    E3 --> EB
    
    %% Orchestrator -> Governance
    EB --"Subscribes to Face/Context"--> P7
    EB --"Subscribes to Anomalies"--> P4
    EB --"Subscribes to Intersections"--> P2
    EB --"Subscribes to ANY Event"--> P8
    
    %% Governance -> Orchestrator (Internal Loops)
    P7 --"Publishes COMPLIANCE_CHECKED"--> EB
    P2 --"Publishes THREAT_FUSED"--> EB
    
    %% Orchestrator -> FL Layer
    EB --"Subscribes to System Drift"--> P12
    EB --"Subscribes to Anonymous Tensors"--> P13
    
    %% Orchestrator -> UI Layer
    EB --"Subscribes to ALERTS"--> P15
    EB --"Subscribes to METRICS"--> P16
    
    %% Hardware Monitoring side-channel
    P5 -. "Monitors Event Load" .-> EB
```

## How This Prevents Conflict

When Paper 7 (Spatiotemporal Constraints) is implemented, it does not query the camera or microphone. It subscribes to the `UnifiedOrchestrator` to receive `FACE_DETECTED` events. 

If Paper 3 (Pose Privacy) ensures that RGB frames are instantly destroyed, Paper 7's implementation is entirely unaffected as it already operates solely on the abstract, delayed, and privacy-filtered events provided by the Orchestrator. No implementation degrades another, and Papers 16-20 act entirely as read-only observers on the event stream, ensuring zero interference with production logic.
