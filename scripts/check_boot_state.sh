#!/usr/bin/env sh
# Read-only Android boot property observer. It does not change device state.
set -u

EXPECTED_SERIAL="CHR7N18A24001030"
PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
LOG_DIR="$PROJECT_DIR/logs"
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
LOG_FILE="$LOG_DIR/boot_state_${TIMESTAMP}.log"
TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/check_boot_state.XXXXXX")
STDOUT_FILE="$TEMP_DIR/stdout"
STDERR_FILE="$TEMP_DIR/stderr"
LAST_OUTPUT=""

cleanup() {
  rm -rf "$TEMP_DIR"
}

trap cleanup EXIT HUP INT TERM

mkdir -p "$LOG_DIR"

log() {
  printf '%s\n' "$*" | tee -a "$LOG_FILE"
}

record_file() {
  if [ -s "$1" ]; then
    sed 's/^/  /' "$1" | tee -a "$LOG_FILE"
  else
    printf '  <empty>\n' | tee -a "$LOG_FILE"
  fi
}

run_check() {
  CHECK_NAME=$1
  shift

  : >"$STDOUT_FILE"
  : >"$STDERR_FILE"
  "$@" >"$STDOUT_FILE" 2>"$STDERR_FILE"
  CHECK_EXIT=$?
  LAST_OUTPUT=$(cat "$STDOUT_FILE")

  log "[CHECK]"
  log "command: $CHECK_NAME"
  log "stdout:"
  record_file "$STDOUT_FILE"
  log "stderr:"
  record_file "$STDERR_FILE"
  log "exit code: $CHECK_EXIT"

  return "$CHECK_EXIT"
}

fail() {
  log "[ERROR] $*"
  log "log: $LOG_FILE"
  exit 1
}

if ! run_check "adb devices" adb devices; then
  fail "adb devices failed"
fi

DEVICE_COUNT=$(printf '%s\n' "$LAST_OUTPUT" | awk 'NR > 1 && NF { count++ } END { print count + 0 }')
if [ "$DEVICE_COUNT" -eq 0 ]; then
  fail "target serial $EXPECTED_SERIAL is not present"
fi
if [ "$DEVICE_COUNT" -gt 1 ]; then
  fail "multiple ADB devices are connected"
fi

FOUND_SERIAL=$(printf '%s\n' "$LAST_OUTPUT" | awk 'NR > 1 && NF { print $1; exit }')
FOUND_STATE=$(printf '%s\n' "$LAST_OUTPUT" | awk 'NR > 1 && NF { print $2; exit }')

if [ "$FOUND_SERIAL" != "$EXPECTED_SERIAL" ]; then
  fail "serial mismatch: expected $EXPECTED_SERIAL, found $FOUND_SERIAL"
fi
case "$FOUND_STATE" in
  device)
    ;;
  unauthorized)
    fail "target serial $EXPECTED_SERIAL is unauthorized"
    ;;
  offline)
    fail "target serial $EXPECTED_SERIAL is offline"
    ;;
  *)
    fail "target serial $EXPECTED_SERIAL is not in device state: $FOUND_STATE"
    ;;
esac

get_property() {
  PROPERTY=$1
  if ! run_check "adb -s $EXPECTED_SERIAL shell getprop $PROPERTY" \
    adb -s "$EXPECTED_SERIAL" shell getprop "$PROPERTY"; then
    fail "failed to read $PROPERTY"
  fi
  LAST_VALUE=$LAST_OUTPUT
  if [ -z "$LAST_VALUE" ]; then
    LAST_VALUE="<empty>"
  fi
}

get_property ro.product.model
PRODUCT_MODEL=$LAST_VALUE
get_property ro.build.version.release
ANDROID_RELEASE=$LAST_VALUE
get_property ro.build.version.emui
EMUI_VERSION=$LAST_VALUE
get_property ro.build.version.security_patch
SECURITY_PATCH=$LAST_VALUE

get_property ro.boot.flash.locked
BOOT_FLASH_LOCKED=$LAST_VALUE
get_property ro.boot.verifiedbootstate
BOOT_VERIFIED_BOOT_STATE=$LAST_VALUE
get_property ro.boot.vbmeta.device_state
BOOT_VBMETA_DEVICE_STATE=$LAST_VALUE
get_property ro.boot.veritymode
BOOT_VERITY_MODE=$LAST_VALUE

log "[BOOT PROPERTIES]"
log "ro.boot.flash.locked=$BOOT_FLASH_LOCKED"
log "ro.boot.verifiedbootstate=$BOOT_VERIFIED_BOOT_STATE"
log "ro.boot.vbmeta.device_state=$BOOT_VBMETA_DEVICE_STATE"
log "ro.boot.veritymode=$BOOT_VERITY_MODE"
log "log: $LOG_FILE"
