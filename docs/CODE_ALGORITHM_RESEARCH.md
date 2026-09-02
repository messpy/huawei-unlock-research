# Huawei unlock-code algorithm research

Date: 2026-09-02
Scope: Huawei ANE-LX2J / P20 lite family, Android 9 / EMUI 9.1, Kirin 659.

This is external-source research, not a device observation.  It deliberately
does not reproduce an unlock candidate or use the target device's IMEI.

## Confirmed from source code and project documentation

### `haexhub/huaweiBootloaderHack`

- [`unlock.py`](https://github.com/haexhub/huaweiBootloaderHack/blob/master/unlock.py)
  is a Python Fastboot **smartphone bootloader** attempt loop: it invokes
  `adb reboot bootloader`, then `fastboot oem unlock`.
- Its claimed candidate sequence starts at `1000000000000000` (a 16-digit
  number).  The next value is the previous value plus
  `luhn_checksum(imei) + sqrt(imei) * 1024`, converted to an integer.  Thus,
  the often repeated “Luhn-like + sqrt” formula originates in this project’s
  source, not in Huawei documentation or an identified Huawei bootloader
  implementation.
- The source offers an optional attempt-limit mode with `limitAttempt = 5`.
  When enabled, its condition reboots the bootloader every `limitAttempt - 1`
  failures (therefore every 4 failures), not after five.  Its default disables
  the limit and instead can run an effectively unbounded sequence.  It does
  not handle a Fastboot timeout, serial mismatch, or an ambiguous response
  safely; it suppresses command output and treats return code zero as success.
- It contains no ANE, P20 lite, Kirin 659, EMUI 9.1, or documented Huawei
  protocol evidence for that formula.  Its README/source claims are therefore
  insufficient evidence that its generated values are `USERLOCK` codes for
  this target.

### `forth32/huaweicalc` and `kenshaw/huaweihash`

- [`forth32/huaweicalc`](https://github.com/forth32/huaweicalc) explicitly
  describes itself as a *Huawei modem unlock code calculator*.  Its
  [`calc.cpp`](https://github.com/forth32/huaweicalc/blob/master/calc.cpp)
  selects v2/v201 handlers from an IMEI-derived index; its
  [`encrypt_v1.cpp`](https://github.com/forth32/huaweicalc/blob/master/encrypt_v1.cpp)
  is MD5-based and formats a numeric result.  This is source code for modem
  NCK/flash-style calculations, not evidence for a phone `fastboot oem unlock`
  `USERLOCK` value.
- [`kenshaw/huaweihash`](https://github.com/kenshaw/huaweihash) documents that
  it imports the C calculations from `forth32` and exposes **flash, v1, v2,
  v201** codes.  Its example values are 8 digits.  It is therefore corroborating
  modem/firmware-code code, not a 16-digit smartphone bootloader-code source.

### `keowu/huawei_code_calculator`

- [`main.py`](https://github.com/keowu/huawei_code_calculator/blob/main/main.py)
  computes MD5-derived values from an IMEI plus two fixed salts and labels them
  “Unlock CODE” and “Flash CODE”.  The repository describes itself broadly as
  a calculator for Huawei products, but its source does not identify ANE,
  Kirin 659, `USERLOCK`, Fastboot, or a 16-digit smartphone bootloader format.
- Its source is therefore not a validated input generator for this phone.

### PotatoNV and the ANE / Kirin 659 relationship

- [`PotatoNV`](https://github.com/kitsuned/PotatoNV) lists Kirin 659 among
  supported CPU families and lists **Huawei P20 Lite / Nova 3e (`ANE`)** with
  “Kirin 65x (A)” in its tested-device table.  This is relevant family-level
  evidence, but it is not model-variant-specific proof for ANE-LX2J.
- The project states that its process requires physical disassembly and a
  testpoint to enter `DOWNLOAD_VCOM`, uploads a USB bootloader, and writes a
  SHA-256 hash to the NVME `USRKEY` property.  It can then provide a newly
  written unlock code for `fastboot oem unlock`.  It is **not** an IMEI/Luhn
  code calculator; it changes bootloader/NV data.  Its optional “Disable
  FBLOCK” further enables otherwise unavailable flash/erase/OEM operations.
  Those state-changing procedures are out of scope for this repository and
  were not executed.

## Conclusions for this probe

1. There is no confirmed source tying the Luhn + sqrt sequence to Huawei
   smartphone `USERLOCK`, ANE-LX2J, P20 lite, or Kirin 659.  It is an unverified
   third-party heuristic.
2. The 16-digit premise is supported only by the starting value chosen in the
   `haexhub` loop and by the local, owner-supplied candidate-file validation;
   it is not established by the modem calculators.
3. The modem/router-style calculator families must not be conflated with the
   smartphone Fastboot `USERLOCK` path: their documented inputs/outputs and
   purposes differ, and their examples are 8-digit values.
4. Because the prior index 1 attempt timed out, it remains an historical,
   unresolved observation.  It is neither a confirmed failure nor success and
   is never resent by the revised probe.
5. The revised probe does not adopt the external loop's reboot/delay strategy.
   It sends at most four pre-supplied owner-authorized candidates (indexes
   2–5), uses a 30-second timeout per candidate, and stops on any ambiguity.

## Source limits

The cited repositories are third-party, archived or community-maintained
projects.  No Huawei primary documentation was found that validates these
candidate algorithms for this model.  Assertions about the target's current
state belong in `docs/CODEX_FINDINGS.md`, not in this research record.
