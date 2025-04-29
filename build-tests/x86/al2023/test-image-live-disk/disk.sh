#!/bin/bash
set -x
# Get Root partition UUID

ROOT_UUID=$(blkid --list-one --output value --match-token LABEL="/" -s UUID)

dracut \
  --uefi \
  --kver $(uname -r) \
  --kernel-cmdline "root=UUID=${ROOT_UUID} rootwait ro security=selinux nvme_core.io_timeout=4294967295 rd.shell=0 selinux=0 security=selinux console=ttyS0,115200n8 earlyprintk=ttyS0,115200 systemd.log_level=debug systemd.log_target=console rd.shell=1" \
--force /boot/efi/EFI/BOOT/BOOTX64.EFI
