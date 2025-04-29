#!/bin/bash
set -x
# Get Root partition UUID

# Uses what is in /dev, ensure the label ROOT is not used by another mounted volume

echo "See fstab original"
cat /etc/fstab
ROOT_UUID="/dev/mapper/root"

ROOT_DEV=$(blkid --list-one --output device --match-token LABEL="ROOT") 

HASH_DEV="/tmp/root-verity.img"

VERITY_FILE="./verity-info.txt"

sed -i "1s|UUID=[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}|${ROOT_DEV}|" /etc/fstab

echo "See fstab changes"
cat /etc/fstab

# Generate verity hash
veritysetup format "${ROOT_DEV}" "${HASH_DEV}" \
  --hash-offset=0 --data-block-size=4096 --hash-block-size=4096 \
  | tee $VERITY_FILE

# set ROOT_HASH
ROOT_HASH=$(grep "Root hash:" "${VERITY_FILE}" | awk '{print $3}')
echo $ROOT_HASH

dracut \
  --uefi \
  --kver $(uname -r) \
  --force /boot/efi/EFI/BOOT/BOOTX64.EFI \
  --kernel-cmdline "root=/dev/mapper/root rootwait roothash=${ROOT_HASH} nvme_core.io_timeout=500 console=ttyS0,115200n8 systemd.log_level=debug systemd.log_target=console rd.shell=1 systemd.verity_root_data=/dev/disk/by-partlabel/ROOT systemd.verity_root_hash=/dev/disk/by-partlabel/VERITY systemd.verity_root_options=ignore-zero-blocks,ignore-corruption" 

