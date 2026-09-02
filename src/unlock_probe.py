#!/usr/bin/env python3
"""Conservative Fastboot response probe for one owner-authorized device."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from datetime import datetime, timezone
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "state" / "probe-state.json"
LOG_DIR = ROOT / "logs"
EXPECTED_SERIAL = "CHR7N18A24001030"
MAX_PER_RUN = 4
FASTBOOT_TIMEOUT_SECONDS = 30


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log(stage: str, message: str) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    line = f"{utc_now()} [{stage}] {message}"
    print(line, flush=True)
    with (LOG_DIR / "probe.log").open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def atomic_write_state(state: dict[str, Any]) -> None:
    """Persist state with tmp file, fsync, and atomic replacement."""
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp_path = STATE_PATH.with_name(f".{STATE_PATH.name}.{os.getpid()}.tmp")
    try:
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, STATE_PATH)
        directory_fd = os.open(STATE_PATH.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def load_state(expected_serial: str, candidates_digest: str) -> dict[str, Any]:
    if not STATE_PATH.exists():
        state: dict[str, Any] = {
            "schema_version": 2,
            "expected_serial": expected_serial,
            "candidates_sha256": candidates_digest,
            "last_sent_index": None,
            "last_confirmed_failed_index": None,
            "pending_index": None,
            "historical_pending_indexes": [],
            "next_index": 0,
            "halt_reason": None,
            "updated_at": utc_now(),
        }
        atomic_write_state(state)
        return state
    with STATE_PATH.open(encoding="utf-8") as handle:
        state = json.load(handle)
    required = {"expected_serial", "candidates_sha256", "last_sent_index", "last_confirmed_failed_index", "pending_index", "next_index"}
    if not required.issubset(state):
        raise ValueError("state schema is incomplete; refusing to continue")
    if state["expected_serial"] != expected_serial:
        raise ValueError("expected_serial differs from the serial fixed in state")
    if state["candidates_sha256"] != candidates_digest:
        raise ValueError("candidate file differs from the file fixed in state")
    # The previous run left index 1 unresolved after a timeout.  Preserve that
    # fact as history, but do not treat it as an in-flight command: it must
    # never be retransmitted or reclassified by this tool.
    changed = False
    historical = state.setdefault("historical_pending_indexes", [])
    if not isinstance(historical, list) or any(not isinstance(item, int) for item in historical):
        raise ValueError("historical_pending_indexes is invalid")
    if state["pending_index"] == 1:
        if 1 not in historical:
            historical.append(1)
        state["pending_index"] = None
        state["next_index"] = max(state["next_index"], 2)
        state["halt_reason"] = "index=1 retained as historical unresolved timeout"
        changed = True
    elif state["pending_index"] is not None:
        raise ValueError("an unresolved current pending_index exists; refusing to send")
    if state.get("schema_version") != 2:
        state["schema_version"] = 2
        changed = True
    if changed:
        state["updated_at"] = utc_now()
        atomic_write_state(state)
    return state


def read_candidates(path: Path) -> list[str]:
    if not path.is_file():
        raise ValueError(f"codes file is not a regular file: {path}")
    candidates = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()
                  if line.strip() and not line.lstrip().startswith("#")]
    if not candidates:
        raise ValueError("codes file contains no candidates")
    if any(any(ch.isspace() for ch in code) for code in candidates):
        raise ValueError("a candidate contains whitespace")
    if any(re.fullmatch(r"[0-9]{16}", code) is None for code in candidates):
        raise ValueError("every candidate must contain exactly 16 ASCII digits")
    if len(candidates) != len(set(candidates)):
        raise ValueError("duplicate candidates are not allowed")
    return candidates


def candidate_tag(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()[:12]


def redact_imei(text: str) -> str:
    """Never persist a full 15-digit IMEI if a device response contains one."""
    return re.sub(r"(?<!\d)(\d{11})(\d{4})(?!\d)", r"***********\2", text)


def safe_output(value: str) -> str:
    """Keep diagnostic output readable without persisting a full IMEI."""
    return redact_imei(value).strip() or "<empty>"


def run_fastboot_check(command: list[str], display_command: str) -> subprocess.CompletedProcess[str]:
    """Run and completely log a read-only Fastboot connectivity check."""
    log("CHECK", f"command={display_command}")
    try:
        result = subprocess.run(command, text=True, capture_output=True,
                                timeout=FASTBOOT_TIMEOUT_SECONDS, check=False)
    except subprocess.TimeoutExpired as exc:
        log("CHECK", f"timeout={FASTBOOT_TIMEOUT_SECONDS}s stdout={safe_output(exc.stdout or '')!r} "
                     f"stderr={safe_output(exc.stderr or '')!r}")
        raise
    log("CHECK", f"exit={result.returncode} stdout={safe_output(result.stdout)!r} "
                 f"stderr={safe_output(result.stderr)!r}")
    return result


def connected_devices() -> list[tuple[str, str]]:
    result = run_fastboot_check(["fastboot", "devices"], "fastboot devices")
    if result.returncode != 0:
        raise RuntimeError("fastboot devices returned a non-zero exit code")
    return [(fields[0], fields[1] if len(fields) > 1 else "")
            for line in result.stdout.splitlines() if (fields := line.split())]


def assert_one_expected_device(expected_serial: str) -> None:
    devices = connected_devices()
    if len(devices) != 1:
        raise RuntimeError(f"expected exactly one fastboot device; found {len(devices)}")
    serial, mode = devices[0]
    if serial != expected_serial:
        raise RuntimeError("connected fastboot serial does not match expected_serial")
    if mode != "fastboot":
        raise RuntimeError(f"expected fastboot mode; found {mode or '<empty>'}")
    log("CHECK", "one expected fastboot device confirmed")


def classify_response(output: str) -> str:
    text = output.casefold()
    if "check password failed!" in output:
        return "wrong_code"
    if "command not allowed" in text:
        return "command_not_allowed"
    if any(token in text for token in ("okay", "success", "unlocked")):
        return "possible_success"
    return "unknown"


def stop_pending(state: dict[str, Any], reason: str) -> int:
    state["halt_reason"] = reason
    state["updated_at"] = utc_now()
    atomic_write_state(state)
    log("CHECK", f"stopping with pending_index={state['pending_index']}: {reason}")
    return 2


def main() -> int:
    parser = argparse.ArgumentParser(description="Conservative Huawei Fastboot response probe")
    parser.add_argument("--expected-serial", default=EXPECTED_SERIAL)
    parser.add_argument("--codes-file", required=True, type=Path)
    args = parser.parse_args()
    if args.expected_serial != EXPECTED_SERIAL:
        raise ValueError("expected_serial is fixed and does not match this device")

    candidates = read_candidates(args.codes_file)
    digest = hashlib.sha256("\n".join(candidates).encode("utf-8")).hexdigest()
    state = load_state(args.expected_serial, digest)
    if state["next_index"] >= len(candidates):
        log("CHECK", "all supplied candidates are already resolved; no command will be sent")
        return 0

    print("This may erase the device. Confirm backup, ownership, and the exact serial above.")
    answer = input("Type yes to send at most 4 owner-authorized candidates: ").strip().lower()
    if answer != "yes":
        log("CHECK", "operator declined confirmation; no command sent")
        return 0

    ending = min(state["next_index"] + MAX_PER_RUN, len(candidates))
    for index in range(state["next_index"], ending):
        try:
            assert_one_expected_device(args.expected_serial)
        except (RuntimeError, subprocess.TimeoutExpired) as exc:
            log("CHECK", f"device preflight failed; stopping: {exc}")
            return 2

        code = candidates[index]
        state["pending_index"] = index
        state["last_sent_index"] = index
        state["halt_reason"] = None
        state["updated_at"] = utc_now()
        atomic_write_state(state)
        log("SEND", f"index={index} code_sha256_12={candidate_tag(code)}")
        log("ACTION", f"index={index} command=fastboot -s {EXPECTED_SERIAL} oem unlock <redacted>")
        try:
            result = subprocess.run(["fastboot", "-s", args.expected_serial, "oem", "unlock", code],
                                    text=True, capture_output=True, timeout=FASTBOOT_TIMEOUT_SECONDS, check=False)
        except subprocess.TimeoutExpired as exc:
            log("RECV", f"index={index} timeout={FASTBOOT_TIMEOUT_SECONDS}s "
                        f"stdout={safe_output(exc.stdout or '')!r} stderr={safe_output(exc.stderr or '')!r}")
            return stop_pending(state, "fastboot command timed out")
        output = result.stdout + result.stderr
        log("RECV", f"index={index} exit={result.returncode} stdout={safe_output(result.stdout)!r} "
                    f"stderr={safe_output(result.stderr)!r}")
        kind = classify_response(output)
        if kind == "wrong_code":
            state["last_confirmed_failed_index"] = index
            state["pending_index"] = None
            state["next_index"] = index + 1
            state["halt_reason"] = None
            state["updated_at"] = utc_now()
            atomic_write_state(state)
            log("CHECK", f"index={index} explicitly rejected; failure confirmed")
            continue
        if kind == "command_not_allowed":
            return stop_pending(state, "device returned command not allowed")
        if kind == "possible_success":
            return stop_pending(state, "possible successful unlock response")
        return stop_pending(state, "unknown fastboot response or device disappearance")

    log("CHECK", f"run limit reached: processed at most {MAX_PER_RUN} candidates; exiting")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError, RuntimeError, subprocess.TimeoutExpired) as exc:
        log("CHECK", f"fatal error; no further action: {exc}")
        raise SystemExit(2)
