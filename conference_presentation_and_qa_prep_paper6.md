# ICACT 2026 Presentation & Q&A Defense Master Dossier (Paper 6)

**Conference:** 2026 IEEE 3rd International Conference on Advanced Computing Technologies (ICACT 2026)  
**IEEE Conference Record No.:** 70625  
**Technical Co-Sponsorship:** IEEE Nepal Section  
**Paper Title:** *NLOS Acoustic Sensing via Spectral Gating and GCC-PHAT*  
**Paper ID / Track:** Paper 6 • Physical Sensing & Edge Cyber-Physical Systems  
**Authors:** Polisetti Narendra $^{1,*}$, Vijaya Raju Motru $^{1}$, Suresh Kumar Sreedharan $^{1}$, Praveena Mallampalli $^{1}$, T Murali Mohan $^{1}$, T V Satyasheela $^{1}$  
**Affiliation:** Department of Computer Science and Engineering, Swarnandhra College of Engineering \& Technology (Autonomous), Narsapur, Andhra Pradesh, India  
**Presenting Author:** Polisetti Narendra (`narendresh@yahoo.com`)  
**Allocated Time:** 10 Minutes Oral Presentation + 2 Minutes Defense & Discussion  

---

## 1. Slide-by-Slide Schedule (10-Minute Presentation)

| Slide | Title | Time | Cumulative | Spoken Highlights |
|:---|:---|:---:|:---:|:---|
| **1** | **Title Slide** | 0:30 | 0:00 – 0:30 | Introduce authors, SCET affiliation, ICACT 2026 conference title, and core research mission. |
| **2** | **1. Introduction & Motivation** | 1:30 | 0:30 – 2:00 | Optical blindness at corridor junctions, acoustic wave diffraction, latency & privacy failures of deep learning audio transformers (AST/PANNs). |
| **3** | **2. Related Work & Gap** | 1:00 | 2:00 – 3:00 | Semantic classification vs edge reaction speed, failure of amplitude triggers in corridors, multipath degradation in classical TDOA. |
| **4** | **3. Proposed Method** | 2:30 | 3:00 – 5:30 | 4-mic array ($d=4.2\text{cm}$) $\rightarrow$ 100ms Circular RAM buffer $\rightarrow$ Logarithmic Spectral Gating ($\delta > 0.40$) $\rightarrow$ Autocorrelation Periodicity Rejection ($\rho < 0.65$) $\rightarrow$ GCC-PHAT $\rightarrow$ Immediate PCM overwrite. |
| **5** | **4. Experimental Setup** | 1:00 | 5:30 – 6:30 | L-shaped corridor ($30\text{m} \times 2.4\text{m} \times 3.0\text{m}$), $RT_{60} \approx 1.2\text{s}$, $D_c \approx 2.1\text{m}$, 1000-event hybrid corpus (FSD50K, MIVIA, ambient HVAC), ARM Cortex-A72 testbed ($<120\text{ms}$ latency, $<15\%$ CPU). |
| **6** | **5. Results & Findings** | 2:30 | 6:30 – 9:00 | 100% detection at 5m & 15m ($S_{env}$) vs 0% for cameras; 24-fold drop in false alarms (42.6% $\rightarrow$ 1.8%) with 94.5% recall; 96.3% F1 under 60dB traffic noise. |
| **7** | **Discussion & Limitations** | *Optional* | — | Privacy by architectural constraint (zero disk storage), limitations: azimuth-only 1D array, metallic multipath jitter ($\pm 8^\circ$), crowd noise masking at 70dB. |
| **8** | **6. Conclusion & Roadmap** | 1:00 | 9:00 – 10:00 | Core one-sentence takeaway; future 3D volumetric arrays, adaptive noise tracking, and ScholarMaster PTZ camera cueing. |
| **9** | **References & Declarations** | *Shown* | — | Foundation references (Knapp & Carter, Allen & Berkley, Valenzise et al., MBEEE: J. Basic Sci. vol. 26(5), pp. 31--37, 2026), ethics compliance, no external funding declaration. |
| **10** | **Thank You & Q&A** | 2:00 | 10:00 – 12:00 | Presenter contact info and invitation for questions. |

---

## 2. Word-for-Word Presentation Speech Script

### **Slide 1: Title Slide (0:00 – 0:30)**
> *"Good morning Session Chair, distinguished judges, and fellow researchers. I am **Polisetti Narendra**, and on behalf of my co-authors at Swarnandhra College of Engineering and Technology, I am honored to present our research entitled **'NLOS Acoustic Sensing via Spectral Gating and GCC-PHAT'** at ICACT 2026.*
> 
> *Our work develops a deterministic, physics-driven acoustic sensing subsystem designed to eliminate permanent visual blind spots in indoor security environments with bounded latency and zero raw audio persistence."*

---

### **Slide 2: 1. Introduction and Motivation (0:30 – 2:00)**
> *"In indoor public and institutional buildings, surveillance cameras suffer from a fundamental physical limitation: **Line-of-Sight optical blindness**. Structural corners, L-shaped corridor bends, and partitions create permanent blind spots where cameras cannot see safety hazards until it is too late.*
> 
> *Acoustics offers a compelling physical alternative: sound waves naturally diffract around sharp geometric corners and reflect off walls, floors, and ceilings, propagating deep into occluded areas.*
> 
> *However, applying modern deep learning audio models like Audio Spectrogram Transformers (AST) or PANNs introduces severe operational bottlenecks: buffering multiple seconds of audio introduces over 1000 milliseconds of latency, requires massive GPU memory, and raises critical privacy objections due to continuous audio recording.*
> 
> *The central thesis of our paper is that **deterministic, physics-driven signal processing can reliably detect impulsive NLOS anomalies in reverberant corridors within 120 milliseconds while guaranteeing zero raw audio retention.**"*

---

### **Slide 3: 2. Related Work and the Research Gap (2:00 – 3:00)**
> *"When we examine existing solutions: first, modern deep learning Audio Event Detection is built for semantic categorization on cloud benchmarks like FSD50K. In real-time physical safety, classifying fine-grained sound semantics is secondary to detecting chaotic energy bursts with guaranteed sub-150 ms reaction time.*
> 
> *Second, naive amplitude triggers fail catastrophically in corridors because everyday door slams and footfalls exceed preset thresholds. Meanwhile, standard cross-correlation collapses under multipath reverberation, where delayed reflections create spurious correlation peaks.*
> 
> *Our work bridges this gap by introducing a two-stage physical filtering architecture—combining logarithmic spectral gating $\delta$ and autocorrelation periodicity rejection $\rho$—coupled with GCC-PHAT phase whitening inside a formally defined reverberant operating regime $\mathcal{R}_{rev}$."*

---

### **Slide 4: 3. Proposed Method: Deterministic Sensing Pipeline (3:00 – 5:30)**
> *"Here is our proposed end-to-end architecture:*
> 
> *A linear 4-microphone array sampled at 44.1 kHz streams into a lock-free 100-millisecond circular RAM ring buffer. Our two-stage physical discriminator filters the audio in real time:*
> 
> *In **Stage 1 (Spectral Gating)**, we compute the logarithmic ratio $\delta$ between high-frequency energy in the 2-to-4 kHz impulse band and low-frequency energy in the 0-to-500 Hz band. Genuine safety anomalies—such as screams or glass breaks—emit rich high-frequency harmonics exceeding a $\delta$ threshold of 0.40, immediately discarding low-frequency structural thuds.*
> 
> *In **Stage 2 (Periodicity Rejection)**, passing frames are tested via discrete autocorrelation. Repeating mechanical waveforms, such as HVAC compressor cycles and ventilation fans, exhibit strong cyclic peaks above $\rho = 0.65$ and are discarded.*
> 
> *For verified chaotic anomalies, **GCC-PHAT** applies magnitude normalization to whiten the cross-power spectral density. This strips out reverberant echo dominance and isolates the true phase arrival delay to calculate the horizontal azimuth angle $\theta$.*
> 
> *Crucially, the moment this lightweight 3-tuple telemetry is emitted, the raw PCM buffer is immediately overwritten in volatile RAM, ensuring complete privacy by design."*

---

### **Slide 5: 4. Experimental Setup & Testbed (5:30 – 6:30)**
> *"We evaluated our system in a physical academic corridor measuring 30 meters in length with an L-shaped blind intersection. Room impulse response profiling revealed a reverberation time $RT_{60}$ of 1.2 seconds and a critical distance $D_c$ of 2.1 meters. Because our safety envelope is 15 meters, the system operates deep inside the reverberant regime $\mathcal{R}_{rev}$, where multipath echoes dominate over direct sound.*
> 
> *We fixed the microphone spacing at $d = 4.2$ cm, which places the spatial aliasing limit at 4083 Hz—comfortably above our 4 kHz target band.*
> 
> *We evaluated on a 1000-event hybrid corpus combining physical corridor recordings with anechoic screams and glass breaks from FSD50K and MIVIA convolved with measured corridor impulse responses. On a quad-core ARM Cortex-A72, the entire pipeline executes in under 120 milliseconds with less than 15% CPU load."*

---

### **Slide 6: 5. Results and Empirical Findings (6:30 – 9:00)**
> *"Our empirical results demonstrate decisive safety advantages:*
> 
> *First, in our **NLOS Safety Envelope Test** around occluded corridor corners, optical cameras registered exactly 0% detection at all distances. In contrast, our acoustic sensing subsystem achieved **100% detection at 5 meters and 15 meters**, decaying gracefully to 89% at 25 meters.*
> 
> *Second, our **Ablation Study** proves why layered physical filtering is essential: an amplitude-only trigger produces an unusable 42.6% false positive rate. Introducing our spectral gate $\delta$ reduces false alarms to 8.2%, and adding autocorrelation periodicity rejection $\rho$ crushes false alarms down to just **1.8%**—a 24-fold reduction—while maintaining **94.5% recall**.*
> 
> *Third, under ambient noise stress-testing, our pipeline maintains **96.3% F1 score** even under 60 dB ambient traffic noise.*
> 
> *Fourth, GCC-PHAT achieves an azimuth localization accuracy of $\pm 4.2^\circ$ in standard corridors and $\pm 8.0^\circ$ under metallic reflection conditions."*

---

### **Slide 7: Discussion and Limitations (Optional)**
> *"Architecturally, our system provides **Privacy by Design**: because audio exists only in volatile 100 ms RAM buffers and is overwritten immediately, it is physically impossible to record speech or eavesdrop.*
> 
> *We also acknowledge our physical operational boundaries: our linear 4-microphone array provides 1D horizontal azimuth tracking; multi-floor stairwells require volumetric 3D arrays. Additionally, heavy 70 dB crowd chatter causes acoustic masking that lowers recall to 78%."*

---

### **Slide 8: 6. Conclusion and Future Roadmap (9:00 – 10:00)**
> *"To conclude, our paper proves that **deterministic, physics-driven acoustic signal processing extends spatial awareness into visually occluded corridors, achieving over 95% detection within a 15-meter envelope, sub-120 millisecond latency, a 1.8% false positive rate, and zero audio storage.***
> 
> *Our future roadmap includes developing 3D tetrahedral microphone arrays for stairwells and integrating these acoustic directional triggers into the ScholarMaster engine to automatically steer pan-tilt-zoom cameras toward occluded incident hotspots.*
> 
> *Thank you very much, and I welcome any questions."*

---

## 3. Deep Study & Q&A Defense Master Guide (Top 5 Questions)

### **Q1: "Why did you choose deterministic signal processing instead of deep learning models like AST or Audio CNNs?"**
> **Authoritative Defense Answer:**  
> *"In emergency edge safety applications, three non-negotiable constraints dictate the architecture: latency, compute, and privacy.*  
> 1. *Deep learning models like AST or PANNs require multi-second audio context windows (often 2 to 10 seconds), introducing over 1000 milliseconds of structural buffering latency—violating sub-150 ms emergency response budgets.*  
> 2. *Large models with >85 million parameters require dedicated GPUs or NPUs (>200 MB memory), whereas our deterministic FFT and autocorrelation pipeline consumes under 5 MB of RAM and takes less than 15% of a commodity ARM CPU.*  
> 3. *Continuously buffering and storing audio for deep learning raises severe institutional privacy concerns. In our deterministic pipeline, the raw PCM sample is immediately overwritten in volatile RAM upon feature extraction. We achieve >95% anomaly detection without ever recording audio or running heavy neural networks."*

---

### **Q2: "What is the 'Reverberant Operating Regime' ($\mathcal{R}_{rev}$), and why does standard acoustic sensing fail there?"**
> **Authoritative Defense Answer:**  
> *"Critical distance ($D_c$) is the distance from a sound source where direct sound energy equals the reverberant multipath energy reflected from walls, floor, and ceiling.  
> In typical institutional corridors with painted concrete and vinyl tile, the reverberation time ($RT_{60}$) is approximately 1.2 seconds, resulting in a critical distance ($D_c$) of only 2.1 meters.  
> Because our safety envelope ($S_{env}$) is 15 meters, our system operates deep inside $\mathcal{R}_{rev} = \{r : r \gg D_c\}$, where multipath echoes completely dominate the direct signal.  
> Standard inverse-square law distance estimations and classical cross-correlation fail in this regime because multipath reflections create multiple delayed correlation peaks that mask the true source direction. We solve this by applying GCC-PHAT magnitude whitening, which strips reverberant energy dominance and isolates the true phase arrival delay."*

---

### **Q3: "How does your two-stage filter discriminate an emergency scream or glass break from benign door slams and HVAC hum?"**
> **Authoritative Defense Answer:**  
> *"We exploit physical spectral and temporal decay characteristics:  
> 1. **Stage 1 (Spectral Gating $\delta$):** Impulsive anomalies like human screams and shattering glass emit strong high-frequency harmonics in the 2–4 kHz band, whereas heavy door slams and dropped objects concentrate their impact energy below 500 Hz. Our logarithmic ratio $\delta = \log_{10}(E_{2\text{-}4\text{kHz}} / E_{0\text{-}500\text{Hz}})$ exceeds $0.40$ (a $2.5\times$ energy ratio) for true anomalies, instantly rejecting low-frequency structural impacts.  
> 2. **Stage 2 (Periodicity Rejection $\rho$):** Chaotic vocal screams decay rapidly without periodic repetition ($\rho < 0.65$). In contrast, repetitive mechanical noise from HVAC compressors, ventilation fans, and motor hum produce strong periodic peaks in the discrete autocorrelation function $R_{xx}(k)$ above 120 Hz ($k_{min}$). This two-stage filter crushes false alarms from 42.6% down to just 1.8%."*

---

### **Q4: "What are the physical limitations of using a 1D linear 4-microphone array in corridor deployments?"**
> **Authoritative Defense Answer:**  
> *"A 1D linear array estimates the angle of arrival along the horizontal plane (azimuth $\theta$), which is well-suited for linear corridor hallways.  
> However, it has two clear physical limitations:  
> 1. *It cannot estimate vertical elevation angles, making it insufficient for multi-floor vertical stairwells or open atriums without supplementary sensors.*  
> 2. *In metallic corridors with highly specular reflection boundaries, severe multipath interference causes GCC-PHAT peak broadening, introducing an angular jitter of up to $\pm 8^\circ$ (compared to $\pm 4.2^\circ$ in standard corridors).*  
> *In our future work, we are designing 3D tetrahedral volumetric arrays to resolve simultaneous azimuth and elevation in complex architectural junctions."*

---

### **Q5: "How does your system guarantee privacy compliance in institutional and campus environments?"**
> **Authoritative Defense Answer:**  
> *"Privacy is guaranteed through **architectural constraint**, not merely software policy:  
> 1. *Audio samples are ingested strictly into a lock-free 100 ms circular RAM buffer that resides exclusively in volatile memory—never swapped or written to non-volatile disk storage.*  
> 2. *The moment spectral gating and GCC-PHAT extraction finish, the PCM buffer is overwritten.*  
> 3. *The sensing node runs no speech-to-text transcription, voice recognition, or semantic decoding.*  
> 4. *The only output emitted over the network is an encrypted 3-tuple metadata packet: `[Timestamp, Anomaly_Confidence, Azimuth_Angle]`.*  
> *Even in the event of a physical node breach, there is no audio recording stored on the device to recover."*

---

## 4. Quick Reference Metric Numbers (Paper 6 Cheat Sheet)

| Parameter / Metric | Baseline (SPL Trigger) | Spectral Gate Only | **Full Proposed System (Paper 6)** |
|:---|:---:|:---:|:---:|
| **NLOS Safety Detection (15m)** | $0.0\%$ (Camera) | $96.0\%$ | **$100.0\%$ ($S_{env} = 15\text{m}$)** |
| **False Positive Rate** | $42.6\%$ (Unusable) | $8.2\%$ | **$1.8\%$ ($24\times$ Reduction!)** |
| **Recall / Sensitivity** | $99.5\%$ | $96.0\%$ | **$94.5\%$** |
| **F1 Score (60 dB Traffic Floor)** | — | — | **$96.3\%$ ($98.2\%$ Precision)** |
| **End-to-End Latency** | — | — | **$< 120\text{ ms}$ (Single-stream ARM)** |
| **CPU Utilization (ARM Cortex-A72)** | — | — | **$< 15\%$** |
| **RAM Footprint** | $> 200\text{ MB}$ (AST) | — | **$< 5\text{ MB}$ (Circular RAM Buffer)** |
| **Azimuth Accuracy** | — | — | **$\pm 4.2^\circ$ (Standard) / $\pm 8.0^\circ$ (Metallic)** |

---

### Master Assets Summary:
* **LaTeX Beamer Slide Deck:** [presentation_paper6.tex](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/presentation_paper6.tex)
* **Interactive Rehearsal Tool:** [presentation_paper6.html](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/presentation_paper6.html)
* **Full Defense Dossier:** [conference_presentation_and_qa_prep_paper6.md](file:///Users/premkumartatapudi/Desktop/ScholarMasterEngine/conference_presentation_and_qa_prep_paper6.md)
