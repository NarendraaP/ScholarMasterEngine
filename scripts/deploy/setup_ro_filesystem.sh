#!/bin/bash
# Paper 11: Read-Only Filesystem Setup
# =====================================
# Configures overlayfs for corruption-resistant operation during power failures.
# Compatible with Raspberry Pi OS / Debian-based systems.

set -e

echo "🔒 Configuring Read-Only Filesystem with OverlayFS"
echo "=================================================="

# Check root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root (sudo)"
  exit 1
fi

# Backup fstab
cp /etc/fstab /etc/fstab.backup
echo "✅ Backed up /etc/fstab"

# Create mount points for overlayfs
mkdir -p /overlay/{upper,work}
echo "✅ Created overlay directories"

# Add tmpfs for volatile writes (RAM-based)
if ! grep -q "tmpfs /overlay/upper" /etc/fstab; then
    echo "tmpfs /overlay/upper tmpfs defaults,noatime 0 0" >> /etc/fstab
    echo "tmpfs /overlay/work tmpfs defaults,noatime 0 0" >> /etc/fstab
    echo "✅ Added tmpfs entries to /etc/fstab"
fi

# Remount root as read-only with overlayfs
# This requires initramfs overlay support (available in modern RPi OS)
if ! grep -q "overlayroot" /boot/cmdline.txt 2>/dev/null; then
    echo ""
    echo "⚠️  WARNING: Enabling read-only root filesystem"
    echo "   - Root (/) will be mounted RO"
    echo "   - Writes go to RAM (lost on reboot)"
    echo "   - /data partition remains RW for persistence"
    echo ""
    echo "To enable, add to /boot/cmdline.txt (or /boot/firmware/cmdline.txt):"
    echo "   overlayroot=tmpfs"
    echo ""
    echo "Or use raspi-config (Performance Options -> Overlay File System)"
fi

# Create persistent data partition
DATA_PARTITION="/dev/mmcblk0p3"  # Adjust for your SD card layout
DATA_MOUNT="/data"

if [ -b "$DATA_PARTITION" ]; then
    mkdir -p $DATA_MOUNT
    
    # Format if not already done
    if ! blkid $DATA_PARTITION | grep -q "TYPE"; then
        echo "📂 Formatting data partition..."
        mkfs.ext4 -F $DATA_PARTITION
    fi
    
    # Add to fstab
    if ! grep -q "$DATA_PARTITION" /etc/fstab; then
        echo "$DATA_PARTITION $DATA_MOUNT ext4 defaults,noatime 0 2" >> /etc/fstab
        echo "✅ Added data partition to /etc/fstab"
    fi
    
    mount $DATA_MOUNT 2>/dev/null || echo "⚠️  Data partition already mounted"
else
    echo "⚠️  Data partition $DATA_PARTITION not found. Using /data on root."
    mkdir -p /data
fi

# Create symbolic links from volatile to persistent storage
mkdir -p /data/logs /data/checkpoints /data/telemetry
ln -sf /data/logs /opt/scholarmaster/logs 2>/dev/null || true
ln -sf /data/checkpoints /opt/scholarmaster/checkpoints 2>/dev/null || true

echo ""
echo "✅ Read-Only Filesystem Configuration Complete"
echo ""
echo "📋 Next Steps:"
echo "   1. Review /etc/fstab changes"
echo "   2. Reboot to activate overlayfs"
echo "   3. Verify with: mount | grep overlay"
echo ""
echo "🔄 To temporarily remount root as RW (for updates):"
echo "   sudo mount -o remount,rw /"
echo "   # Make changes..."
echo "   sudo mount -o remount,ro /"
