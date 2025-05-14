#!/bin/bash
set -x
# Get Root partition UUID

# Uses what is in /dev, ensure the label ROOT is not used by another mounted volume
echo "list blk"
blkid


# Install grub here when the partitions are set but before sync 
# to readonly filesystem
dnf install grub2-tools grub2-efi-x64-ec2 -y 
/usr/bin/grub2-amazon-setup -y

echo "See fstab original"
cat /etc/fstab
ROOT_DEV=$(blkid --list-one --output device --match-token LABEL="ROOT") 
ROOT_UUID=$(blkid --list-one --output value -s UUID --match-token LABEL="ROOT") 
ROOT_TYPE=$(blkid --list-one --output value -s TYPE --match-token LABEL="ROOT") 
echo "${ROOT_UUID} / ${ROOT_TYPE} 0 1" >> /etc/fstab
echo "See fstab changed"
cat /etc/fstab
# # Get the specific loop device 
# LOOP_DEV=$(echo "${ROOT_DEV}" | sed 's/p[0-9]\+$//')

# # TODO: Remove after testing 
# HASH_DEV="/boot/efi/root-verity.img"

# VERITY_FILE="/boot/efi/verity-info.txt"

# # Remap verity with the symlink for verity device
# # sed -i "1s|UUID=[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}|${ROOT_VERITY}|" /etc/fstab


# echo "list blk"
# blkid


# echo "See fstab changes"
# cat /etc/fstab
#VERITY_DEV=$(blkid --list-one --output device --match-token LABEL="VERITY") 

## Unmount the verity parition
#umount /verity

## Create a verity partition in the loop device 
##NOTE: not using the Kiwi parition b/c of mountpoint 
## sgdisk -n 2:0:+1G -t 2:8300 -c 2:"VERITY" $LOOP_DEV
## Generate verity hash

#tee /etc/udev/rules.d/99.partlabel.rules > /dev/null << 'EOF'
#ENV{ID_PART_ENTRY_NAME}==\"ROOT\", SYMLINK+=\"disk/by-partlabel/ROOT\"
#ENV{ID_PART_ENTRY_NAME}==\"VERITY\", SYMLINK+=\"disk/by-partlabel/VERITY\"
#EOF

#veritysetup format "${ROOT_DEV}" "${HASH_DEV}" \
#  --hash-offset=0 --data-block-size=4096 --hash-block-size=4096 \
#  | tee $VERITY_FILE

## Create verity data in partition
#dd if="${VERITY_FILE}" of="${VERITY_DEV}" bs=4096 conv=fsync

## set ROOT_HASH
#ROOT_HASH=$(grep "Root hash:" "${VERITY_FILE}" | awk '{print $3}')
#echo $ROOT_HASH

## Verify verity setup and create /dev/mapper/verity_root
#veritysetup open "${ROOT_DEV}" verity_root "${VERITY_DEV}" "${ROOT_HASH}" \
#  --hash-offset=0
#if [ $? -ne 0 ]; then
#    echo "Error: Verity setup failed"
#    exit 1
#fi

#  # --kernel-cmdline "root=/dev/mapper/root rootwait roothash=${ROOT_HASH} nvme_core.io_timeout=500 console=ttyS0,115200n8 systemd.log_level=debug systemd.log_target=console rd.shell=1 systemd.verity_root_data=/dev/disk/by-label/ROOT systemd.verity_root_hash=/dev/disk/by-partlabel/VERITY systemd.verity_root_options=ignore-zero-blocks,ignore-corruption" 
#dracut \
#  --uefi \
#  --kver $(uname -r) \
#  --force /boot/efi/EFI/BOOT/BOOTX64.EFI \
#  --add-drivers "dm-verity erofs overlay vfat nls_cp437 nls_iso8859-1" \
#  --force-drivers "dm-verity erofs overlay vfat nls_cp437 nls_iso8859-1" \
#  --add "dm crypt systemd systemd-veritysetup systemd-initrd" \
#  --kernel-cmdline "root=UUID=${ROOT_UUID} rootwait roothash=${ROOT_HASH} nvme_core.io_timeout=500 console=ttyS0,115200n8 systemd.log_level=debug systemd.log_target=console rd.shell=1 systemd.verity_root_options=ignore-zero-blocks,ignore-corruption" 

