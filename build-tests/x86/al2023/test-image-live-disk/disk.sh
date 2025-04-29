#!/bin/bash
set -x
# Get Root partition UUID

ROOT_UUID=$(blkid --list-one --output value --match-token LABEL="/" -s UUID)

dracut \
  --uefi \
  --kver $(uname -r) \
  --force /boot/efi/EFI/BOOT/BOOTX64.EFI \
  --kernel-cmdline "root=UUID=${ROOT_UUID} nvme_core.io_timeout=4294967295  console=ttyS0,115200n8  systemd.log_level=debug systemd.log_target=console rd.shell=1" 
