# PotatoNV safety and recovery assessment

Checked: 2026-09-02. This is research only. No testpoint, NV write, unlock,
reboot, flash, erase, format, or firmware operation was performed.

## What the project says it changes — CONFIRMED from PotatoNV documentation

- [PotatoNV's README](https://github.com/kitsuned/PotatoNV) lists P20 Lite / Nova
  3e `ANE` as Kirin 65x(A), and Kirin 659 among supported CPUs.
- The documented path is physical disassembly, a motherboard testpoint to enter
  `DOWNLOAD_VCOM`, upload of a temporary USB bootloader to RAM, then a USB-bulk
  command that writes a SHA-256 hash to NVME property `USRKEY`.
- `USRKEY` is the stored verifier for the chosen unlock key: after it is changed,
  the documentation directs the user to use that chosen key with
  `fastboot oem unlock`. This is a persistent security-relevant NVME write, not
  an IMEI calculation or a read-only code lookup.
- The optional `Disable FBLOCK` action additionally changes a security check;
  PotatoNV says it permits flash/erase and otherwise unavailable OEM commands.
  It must not be selected under this repository's safety policy.

## ANE-family evidence

- **CONFIRMED family support claim:** the project maps `ANE` to Kirin 65x(A).
- **CONFIRMED failure report:** a PotatoNV discussion contains an ANE-LX2 on
  EMUI 9.1.0.353 whose log reached `Writing FBLOCK state` then failed; a project
  maintainer replied that the program did not work with that model.  This is not
  the exact ANE-LX2J build, so it cannot prove failure here, but it prevents
  treating the broad `ANE` table entry as sufficient success evidence.
- **UNVERIFIED:** a successful PotatoNV run, rollback, or exact recovery path
  for ANE-LX2J 9.1.0.324(C111E37R1P6).

## Device observations — CONFIRMED, but limited

On the sole expected ADB device, read-only queries returned an empty
`ro.oem_unlock_supported`, `settings global oem_unlock_allowed=1`, and
`ro.frp.pst=/dev/block/bootdevice/by-name/frp`.

These observations do **not** establish that Fastboot will accept an unlock,
that FRP is unlocked, or that a testpoint/NV operation is safe.  They must not
be used as an execution gate on their own.

## Consequences after a successful key write — source-backed limits

- PotatoNV documentation directs the user to perform a subsequent Fastboot
  unlock with the selected key. The project distinguishes normal `USERLOCK`
  from optional FBLOCK disabling; do not conflate the two.
- A P20 Lite PotatoNV discussion states that bootloader unlock erases data and
  recommends backup. Another community guide asserts otherwise. The conflict
  means data wipe must be assumed possible; no no-wipe guarantee is accepted.
- A post-unlock root workflow reported for other P20 Lite variants uses
  `recovery_ramdisk`; it remains **UNVERIFIED** for this exact device/build and
  is not a recovery method.

## Failure modes and recovery evidence

| Situation | Evidence | Safe conclusion |
| --- | --- | --- |
| Testpoint / USB-VCOM is not detected | PotatoNV documents a `USB SER` / `HUAWEI USB COM 1.0` requirement; community reports show driver and timing failures. | Stop before starting the tool; do not try random bootloader selections or repeated shorts. |
| NVME write fails | ANE-LX2 report failed while writing FBLOCK. | Stop. No exact ANE-LX2J rollback record exists. |
| Device boots only to Fastboot/eRecovery/recovery | A P20 Lite PotatoNV brick report retained those modes but had no published resolution. | These modes are not proof of recoverability. Preserve evidence and seek an exact official recovery path. |
| Need stock restoration | Huawei documents supported HiSuite/eRecovery recovery, which may erase data and depends on a corresponding ROM. | Potential channel only; exact C111E37R1P6 availability is still unverified. |
| Re-locking | A community author says re-locking with the chosen key might be possible but was not tested. | **UNVERIFIED and prohibited**; do not relock a modified/non-stock device. |

## Required preconditions before any future authorization

1. A verified ordinary user-data backup, restored/tested independently. This is
   not an NVME/USRKEY backup.
2. An exact ANE-LX2J C111E37R1P6 stock recovery source and an independently
   verified recovery procedure. Neither exists in this repository today.
3. Exact ANE-LX2J success evidence for the selected PotatoNV release and
   Kirin-65x variant, plus a documented rollback path for its NV changes.
4. A Windows environment with the documented Huawei USB COM/testpoint driver
   and a positively identified VCOM device. PotatoNV releases target Windows;
   its README points Linux/macOS users to a cross-platform variant, but that
   variant is not validated here.
5. Explicit user authorization to change NVME and accept possible data loss.
   The present safety policy explicitly withholds that authority.

## Assessment

**Do not execute.** PotatoNV has credible family-level relevance but is not
safe to run on this exact phone under the existing rules: it persistently
changes NVME, exact-model success is absent, an ANE-LX2 failure report exists,
and no exact stock recovery / rollback route is established.

## Sources

- [PotatoNV README](https://github.com/kitsuned/PotatoNV)
- [PotatoNV discussion #24: procedure and ANE-LX2 failure](https://github.com/kitsuned/PotatoNV/discussions/24)
- [PotatoNV discussion #138: P20 Lite data-wipe/`recovery_ramdisk` claim](https://github.com/kitsuned/PotatoNV/discussions/138)
- [PotatoNV discussion #152: P20 Lite brick report](https://github.com/kitsuned/PotatoNV/discussions/152)
- [Huawei system-recovery guidance](https://consumer.huawei.com/en/support/content/en-us00406898/)
- [HCU supported-model list](https://hcu-client.com/supported-models.php)
- [DC-unlocker feature table](https://www.dc-unlocker.com/android-feature-table?filter=bootloader)
