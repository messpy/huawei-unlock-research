# PotatoNV execution-readiness gate

Checked: 2026-09-02. This document prepares a future decision only; it does
not authorize testpoint, NVME, FBLOCK, unlock, reboot, flash, erase, format,
or firmware activity.

## Decision: NOT READY

The following blocking conditions are unresolved:

1. No trusted, board-revision-matched ANE-LX2J testpoint map has been verified.
   Search results include third-party FRP-service diagrams, but they do not
   establish that the pad/location is correct or safe for this specific board.
2. No exact ANE-LX2J C111E37R1P6 stock recovery source or tested restoration
   procedure exists. A failed NV write could therefore leave no validated path
   back to stock.
3. No Windows host, Huawei USB COM/testpoint driver installation, or physical
   VCOM enumeration has been prepared. The current host is macOS 12.7.6.
4. PotatoNV documentation does not establish a `USRKEY`-only UI action. Its
   ANE-LX2 discussion log performs `Writing FBLOCK state` before the user-key
   step and then fails. Selecting a normal unlock workflow cannot presently be
   treated as a minimal USRKEY-only mutation.
5. Exact ANE-LX2J success evidence for the selected release and a validated
   NVME rollback procedure are absent.

## Software and host preparation

### Confirmed release identity

- Official repository: `kitsuned/PotatoNV`.
- Release tag: `2022.03`.
- Asset: `PotatoNV-next-v2.2.1_2022.03-x86.zip` (6,506,263 bytes), published
  from the official release page.
- GitHub's release API did not provide an asset SHA-256 digest. Do not infer
  authenticity from a locally calculated hash alone; a future Windows download
  must be from the official URL and its locally calculated SHA-256 must be
  recorded before extraction. It was prepared read-only on 2026-09-02 in
  `/private/tmp/potatonv-2022.03` (not executed or added to Git). Local SHA-256:
  `98344a77eeddee99f4ca145c586a6656b7f98da0cc04be1007dc102ec62ae416`.
  The archive contains `hisi65x_a` and `hisi65x_b`; the README maps ANE to
  `hisi65x_a`, but this is not execution approval.

### Required, not yet prepared

- A dedicated Windows physical host with a direct USB port; a VM/USB passthrough
  configuration is unvalidated and must not be used as the first attempt.
- Huawei USB COM/testpoint driver. PotatoNV documentation expects the device to
  enumerate as `HUAWEI USB COM 1.0`/`USB SER`; driver installation and its
  publisher/signature must be checked in Windows before any phone is opened.
- A known-good data cable, ESD-safe workspace, plastic opening tools, controlled
  heat source, suitable precision drivers, multimeter, and a separate record of
  the device's visible serial/build. These are preparation requirements, not a
  disassembly instruction.

## Backups

### What can be backed up now

- Ordinary user data: contacts, messages, photos, videos, local documents,
  application data where the app supports export, authenticator recovery codes,
  and a separate list of installed apps/accounts. HiSuite's documented backup
  capability is a candidate for ordinary user data.
- Device identity/state evidence already recorded locally: model, build, patch,
  boot properties, and user-visible configuration. Do not include IMEI in the
  repository.

### What cannot be claimed as backed up

- No documented owner-accessible, read-only backup of NVME `USRKEY`, FBLOCK, or
  the FRP partition is available under the current locked state. Do not use a
  service tool to obtain one; that would exceed the safety policy.
- A completed backup is insufficient until a restore/readback check has shown
  the archive is usable. This check is not yet done.
- Export app-specific data and 2FA recovery material, copy photos/documents to
  two independent destinations, and perform a sample restore or archive
  verification. Android 9 `adb backup` is not guaranteed application coverage.

## Selection and option constraints

- The PotatoNV table associates `ANE` with **Kirin 65x(A)**. That is the only
  family-level mapping found, but it is **not confirmed for ANE-LX2J** because
  an ANE-LX2 write failure is documented. Do not substitute another bootloader
  selection experimentally.
- Never select `Disable FBLOCK`; the project says it changes the security check
  and enables flash/erase/otherwise unavailable OEM commands.
- Never use FRP erase/reset, OEMINFO/NV repair, firmware/customization, or any
  tool operation beyond a future explicitly authorized scope.
- Because a USRKEY-only path is unproven, **do not start PotatoNV** merely to
  attempt a supposedly minimal write.

## Testpoint and physical preparation

The exact ANE-LX2J pad for this board revision remains **UNVERIFIED**. Do not
use ANE-LX1/other-revision or unverified service diagrams. Confirmed only is
the high-level flow: powered-off opened phone, temporary testpoint contact while
USB is connected, then `HUAWEI USB COM 1.0`/`USB SER` enumeration. Required
tools: direct Windows USB port/cable, ESD protection, plastic picks, controlled
heat, precision drivers, magnification and multimeter. No pad contact is
authorized until board identity and a trusted map match.

## USRKEY-only and stop policy

The release does not document a user-key-only transaction. The published
ANE-LX2 log performs `Writing FBLOCK state` before the key step and then
`Failed to set prop:`. Thus the smallest defensible procedure is currently
“do not run”; a future YES requires maintainer confirmation and an exact-board
recovery path. Stop without further commands on invalid ACK, timeout, write
error, unexpected FBLOCK/NV selection, lost USB, black screen, boot loop, or
failure to reconnect.

## Future run decision gates and stop conditions

Only after every blocker above is cleared and explicit authorization is given:

1. Verify full, restorable ordinary-data backup and exact recovery path.
2. Verify the exact board/revision against a trusted testpoint source before
   opening the device. A mismatch is a stop.
3. In Windows, verify the expected VCOM device and driver identity before
   launching PotatoNV. No VCOM, unexpected serial/model/build, or a second USB
   device is a stop.
4. A release verification failure, image verification failure, invalid ACK,
   resource-in-use message, timeout, write error, unexpected option, or failure
   to reconnect is an immediate stop. Do not retry with a different loader.
5. If a future authorized operation reaches normal Fastboot, `fastboot devices`
   is the only initial read-only channel check. This device's prior
   `oem get-bootinfo` timeout/command behavior makes it unsuitable as a primary
   success test. Do not issue `fastboot oem unlock` until separately authorized.

## After a future successful unlock (not this task)

Assume a data wipe. Only after Android has completed its own first boot may the
existing read-only boot-state checker be used to record boot properties. A
root image, TWRP, `recovery_ramdisk`, or re-lock action remains prohibited until
an exact-build recovery plan is independently validated.

## Sources

- [PotatoNV README](https://github.com/kitsuned/PotatoNV)
- [PotatoNV release 2022.03](https://github.com/kitsuned/PotatoNV/releases/tag/2022.03)
- [PotatoNV discussion #24](https://github.com/kitsuned/PotatoNV/discussions/24)
- [PotatoNV discussion #138](https://github.com/kitsuned/PotatoNV/discussions/138)
- [Huawei HiSuite capabilities](https://consumer.huawei.com/ph/support/content/en-us00731203/)
