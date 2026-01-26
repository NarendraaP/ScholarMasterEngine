#!/bin/bash
# ==========================================
# M2 Power Profiler Script
# Paper 5: Hardware Benchmarking
# ==========================================
#
# Purpose: Capture high-frequency power metrics on Apple Silicon platforms
#          Samples CPU, GPU, and ANE (Apple Neural Engine) power rails
#
# Usage: sudo ./power_profiler.sh [duration_seconds] [output_file]
#
# Requirements:
#   - macOS 11+ (Big Sur or later)
#   - sudo privileges (powermetrics requires root)
#   - Apple Silicon (M1/M2/M3 series)
#
# ==========================================

# Default configuration
DURATION=${1:-3600}  # Default: 60 minutes (3600 seconds)
LOG_FILE=${2:-"power_metrics_$(date +%Y%m%d_%H%M%S).plist"}
SAMPLE_RATE=100  # Sample every 100ms

echo "=========================================="
echo "M2 Power Profiler - Paper 5 Benchmarking"
echo "=========================================="
echo ""
echo "Configuration:"
echo "  Duration:     ${DURATION}s ($(($DURATION / 60)) minutes)"
echo "  Output File:  ${LOG_FILE}"
echo "  Sample Rate:  ${SAMPLE_RATE}ms"
echo ""
echo "Starting power profiling..."
echo "Press Ctrl+C to stop early"
echo ""

# Start powermetrics in background
sudo powermetrics \
  --samplers cpu_power,gpu_power,ane_power,thermal \
  --show-process-coalition \
  --show-process-gpu \
  --show-process-energy \
  --sample-rate ${SAMPLE_RATE} \
  --output-file "${LOG_FILE}" &

POWERMETRICS_PID=$!

# Wait for specified duration
sleep ${DURATION}

# Gracefully stop powermetrics
echo ""
echo "Duration elapsed. Stopping profiler..."
sudo kill -INT ${POWERMETRICS_PID}
wait ${POWERMETRICS_PID} 2>/dev/null

echo ""
echo "=========================================="
echo "Profiling Complete!"
echo "=========================================="
echo "Data saved to: ${LOG_FILE}"
echo ""
echo "To parse the plist file, use:"
echo "  plutil -convert json ${LOG_FILE} -o power_metrics.json"
echo ""
echo "To extract average power:"
echo "  grep -A 5 'CPU Power' ${LOG_FILE} | head -20"
echo ""
