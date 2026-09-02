# Root feasibility record and safe plan

Checked: 2026-09-02

This record does not authorize unlocking, flashing, modifying a partition, or changing device state.

## Current device gate — CONFIRMED

- The sole connected ADB device matched `CHR7N18A24001030`.
- Read-only properties: ANE-LX2J; Android 9; EmotionUI_9.1.0; patch 2020-04-01;
  `flash.locked=1`, verified-boot `green`, vbmeta state `locked`, verity `enforcing`.
- Treat the bootloader as locked. No root image may be flashed.

## Public evidence

### CONFIRMED

- An [XDA thread](https://xdaforums.com/t/cpu-cores-offline.4434543/) reports custom-GSI
  use on P20 lite LX2J / EMUI 9.1.0.324, with a stock-recovery workaround for a CPU issue.
  It does not identify C111E37R1P6 or give a validated installation route.
- [Huawei](https://consumer.huawei.com/en/emui/faq/) does not publish complete microSD
  packages from EMUI 4 onward and directs updates/recovery to online update or supported HiSuite.
  Support for recovery depends on the device and corresponding ROM.

### LIKELY — third-party claim only

- A [P20 lite EMUI 9.1 guide](https://ministryofsolutions.com/huawei-p20-lite-emui9-1-root-ane-lx1-lx2-lx3-al00/)
  claims an already-unlocked workflow using TWRP in `recovery_ramdisk`, `erecovery_ramdisk`,
  and Magisk v23. It neither proves compatibility with ANE-LX2J C111E37R1P6 nor makes a
  different-build image safe.

### UNVERIFIED

- A permitted bootloader-unlock method for exact ANE-LX2J 9.1.0.324(C111E37R1P6).
- Magisk/root or TWRP success for that exact build.
- Exact-firmware availability/integrity and the presence of RECOVERY_RAMDISK, RAMDISK,
  KERNEL, RECOVERY_VENDOR, and VBMETA images in its package.

## Safe next action

The installed macOS HiSuite client does not expose an **Update** screen, so it
cannot be used to inspect an offered firmware build. Do not attempt to work
around this with Update, Rollback, System Recovery, download, or restore on a
different client. If a supported read-only firmware-information source becomes
available, it must show the exact model/CUST/build before it is recorded.

## Prohibited while locked

No `flash`, `erase`, `format`, OEMINFO/NV change, firmware installation, recovery/TWRP/Magisk
write, or non-matching firmware. Index 1 remains unresolved and must never be resent or reclassified.
