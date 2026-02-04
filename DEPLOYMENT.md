# Paper 11 Deployment Infrastructure - README
# ============================================

This directory contains production-grade deployment infrastructure for the ScholarMaster Engine.

## 📦 Components Implemented

### 1. **Containerization** (`Dockerfile`)
- Multi-stage optimized Python 3.9 container
- Non-root user execution (security hardening)
- Health check endpoints
- Minimal image size via layer caching

**Build & Test:**
```bash
docker build -t scholarmaster:v2.1 .
docker run --rm --device /dev/video0 scholarmaster:v2.1
```

### 2. **Blue/Green OTA** (`docker-compose.yml`, `blue_green_update.sh`)
- Zero-downtime model updates
- Automated health checks before traffic switch
- Rollback on failure
- Redis + MQTT broker orchestration

**Deploy New Version:**
```bash
./scripts/deploy/blue_green_update.sh v2.2
```

### 3. **Hardware Watchdog** (`utils/watchdog.py`)
- /dev/watchdog heartbeat protocol
- Autonomous recovery from kernel panics
- Compatible with BCM2711 (Raspberry Pi 4)

**Usage:**
```python
from utils.watchdog import get_watchdog
wd = get_watchdog()
wd.start()  # Begins 10-second heartbeat
```

**Enable on Raspberry Pi:**
```bash
echo "dtparam=watchdog=on" | sudo tee -a /boot/config.txt
sudo reboot
```

### 4. **MQTT Store-and-Forward** (`utils/mqtt_buffer.py`)
- Partition-tolerant telemetry
- SQLite persistence during outages
- Automatic replay on reconnection
- QoS 1 (At Least Once)

**Usage:**
```python
from utils.mqtt_buffer import MQTTBuffer
buffer = MQTTBuffer(broker_host="localhost")
buffer.publish("scholar/attendance", {"count": 42})
```

### 5. **Read-Only Filesystem** (`setup_ro_filesystem.sh`)
- OverlayFS configuration
- Corruption-resistant during power failures
- Persistent /data partition
- tmpfs for volatile writes

**Setup:**
```bash
sudo ./scripts/deploy/setup_ro_filesystem.sh
sudo reboot
```

### 6. **LUKS Encryption** (`setup_luks_encryption.sh`)
- Data-at-rest encryption
- TPM 2.0 key unsealing (optional)
- Prevents recovery if device stolen

**Setup:**
```bash
sudo ./scripts/deploy/setup_luks_encryption.sh
# Follow prompts
```

---

## 🔧 Quick Start

### Raspberry Pi / Jetson Deployment

```bash
# 1. Install system dependencies
sudo apt-get update
sudo apt-get install -y docker.io docker-compose redis-server mosquitto

# 2. Build Docker image
docker build -t scholarmaster:v2.1 .

# 3. Start services
docker-compose up -d

# 4. Verify health
docker ps
docker logs scholar-blue

# 5. Enable systemd service (optional)
sudo ./scripts/deploy/install_service.sh
sudo systemctl status scholarmaster
```

---

## 📊 Validation Commands

**Check Watchdog:**
```bash
python3 utils/watchdog.py
```

**Check MQTT Buffer:**
```bash
python3 utils/mqtt_buffer.py
# Monitor: tail -f data/mqtt_buffer.db
```

**Check OverlayFS:**
```bash
mount | grep overlay
```

**Check LUKS:**
```bash
sudo cryptsetup status scholardata
```

---

## 🛡️ Security Hardening Checklist
- [x] Systemd supervision (`Restart=always`)
- [x] Hardware watchdog timer
- [x] Read-only root filesystem
- [x] Docker containerization
- [x] Non-root user execution
- [x] LUKS data encryption
- [x] Partition-tolerant messaging

---

## 📖 Paper 11 Citation
These components validate the reliability architecture described in:
> P. Tatapudi, "From Lab to Lecture Hall: Longitudinal Deployment, Data Governance, and Empirical Validation of the ScholarMaster Engine," *ScholarMaster Research Series*, Paper 11, 2026.

---

## 🔗 References
- Docker Best Practices: https://docs.docker.com/develop/dev-best-practices/
- Raspberry Pi Watchdog: https://www.raspberrypi.com/documentation/computers/linux_kernel.html#watchdog-timers
- LUKS Encryption: https://gitlab.com/cryptsetup/cryptsetup
- MQTT QoS: https://www.hivemq.com/blog/mqtt-essentials-part-6-mqtt-quality-of-service-levels/
