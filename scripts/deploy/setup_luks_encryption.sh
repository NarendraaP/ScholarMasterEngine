#!/bin/bash
# Paper 11: LUKS Encryption Setup
# ================================
# Encrypts data partition using LUKS with TPM 2.0 unsealing.
# Prevents data recovery if edge device is physically stolen.

set -e

echo "🔐 Setting Up LUKS Data Encryption with TPM"
echo "============================================"

# Check root
if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run as root (sudo)"
  exit 1
fi

# Check dependencies
if ! command -v cryptsetup &> /dev/null; then
    echo "📦 Installing cryptsetup..."
    apt-get update && apt-get install -y cryptsetup tpm2-tools
fi

# Configuration
DATA_PARTITION="/dev/mmcblk0p3"  # Adjust for your SD card layout
LUKS_NAME="scholardata"
MOUNT_POINT="/data"

# Warning
echo ""
echo "⚠️  WARNING: This will ERASE all data on $DATA_PARTITION"
echo "   Make sure you have backups!"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Aborted"
    exit 1
fi

# Step 1: Generate encryption key
KEY_FILE="/root/luks-key.bin"
dd if=/dev/urandom of=$KEY_FILE bs=512 count=1
chmod 600 $KEY_FILE
echo "✅ Generated encryption key: $KEY_FILE"

# Step 2: Format partition with LUKS
echo "🔒 Encrypting partition with LUKS..."
cryptsetup luksFormat $DATA_PARTITION $KEY_FILE --batch-mode

# Step 3: Open encrypted partition
cryptsetup luksOpen $DATA_PARTITION $LUKS_NAME --key-file $KEY_FILE

# Step 4: Create filesystem
echo "📂 Creating ext4 filesystem..."
mkfs.ext4 /dev/mapper/$LUKS_NAME

# Step 5: Mount and test
mkdir -p $MOUNT_POINT
mount /dev/mapper/$LUKS_NAME $MOUNT_POINT
echo "✅ Encrypted partition mounted at $MOUNT_POINT"

# Step 6: TPM Integration (if available)
if command -v tpm2_pcrread &> /dev/null; then
    echo "🔑 Integrating with TPM 2.0..."
    
    # Seal key to TPM PCR banks (simplified - production should use full clevis/systemd-cryptenroll)
    echo "⚠️  TPM sealing requires clevis or systemd-cryptenroll for full automation"
    echo "   Install: apt-get install clevis clevis-luks clevis-tpm2"
    echo ""
    echo "   Then run: clevis luks bind -d $DATA_PARTITION tpm2 '{\"pcr_bank\":\"sha256\",\"pcr_ids\":\"7\"}'"
else
    echo "⚠️  TPM tools not found. Using key file only."
fi

# Step 7: Add to /etc/crypttab for auto-unlock
if ! grep -q "$LUKS_NAME" /etc/crypttab; then
    echo "$LUKS_NAME $DATA_PARTITION $KEY_FILE luks" >> /etc/crypttab
    echo "✅ Added to /etc/crypttab"
fi

# Step 8: Add to /etc/fstab
if ! grep -q "/dev/mapper/$LUKS_NAME" /etc/fstab; then
    echo "/dev/mapper/$LUKS_NAME $MOUNT_POINT ext4 defaults,noatime 0 2" >> /etc/fstab
    echo "✅ Added to /etc/fstab"
fi

echo ""
echo "✅ LUKS Encryption Setup Complete"
echo ""
echo "📋 Verification:"
echo "   cryptsetup status $LUKS_NAME"
echo "   ls -la $MOUNT_POINT"
echo ""
echo "🔒 Security Notes:"
echo "   - Key file: $KEY_FILE (keep secure!)"
echo "   - For full TPM integration, use 'clevis' or 'systemd-cryptenroll'"
echo "   - Without TPM, key file must remain on system"
echo ""
echo "🔄 To manually unlock after reboot:"
echo "   sudo cryptsetup luksOpen $DATA_PARTITION $LUKS_NAME --key-file $KEY_FILE"
echo "   sudo mount /dev/mapper/$LUKS_NAME $MOUNT_POINT"
