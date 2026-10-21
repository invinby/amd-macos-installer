#!/usr/bin/env bash
# Read-only Linux inventory for the AMD Radeon 680M investigation.
# The only intended write is one text report at the requested output path.
# It does not install/configure software or write to GPU devices, firmware,
# boot entries, or internal disks.

set -u

output_path="${1:-gpu-inventory-linux-$(date -u +%Y%m%dT%H%M%SZ).txt}"

if [[ -e "$output_path" ]]; then
  printf 'Won’t overwrite an existing file: %s\n' "$output_path" >&2
  exit 2
fi

if [[ ! -d "$(dirname -- "$output_path")" ]]; then
  printf 'Output folder does not exist: %s\n' "$(dirname -- "$output_path")" >&2
  exit 2
fi

exec 3>"$output_path" || {
  printf 'Cannot create report: %s\n' "$output_path" >&2
  exit 2
}

section() {
  printf '\n\n===== %s =====\n' "$1" >&3
}

run_readonly() {
  local label="$1"
  shift
  section "$label"
  if command -v "$1" >/dev/null 2>&1; then
    "$@" >&3 2>&1 || printf '[command exit: %s]\n' "$?" >&3
  else
    printf '[not installed: %s]\n' "$1" >&3
  fi
}

section 'Collection limits'
printf '%s\n' \
  'This report contains read-only OS/device metadata.' \
  'The only intended write is this report file. No GPU registers are read or written; firmware is not flashed; internal disks are not mounted; boot settings are not changed.' \
  'Review before sharing; the report may include the computer hostname and device paths.' >&3

run_readonly 'Kernel and distribution' uname -a
run_readonly 'Distribution release' bash -c 'cat /etc/os-release'
run_readonly 'AMD PCI devices and bound drivers' lspci -nnk -d 1002:
run_readonly 'Exact Radeon 680M PCI ID (if present)' lspci -nnk -d 1002:1681
run_readonly 'Loaded AMD GPU module' bash -c 'if test -r /sys/module/amdgpu/version; then cat /sys/module/amdgpu/version; else echo "amdgpu module version not exposed in sysfs"; fi'
run_readonly 'Firmware filenames mentioned by amdgpu module metadata' bash -c 'if command -v modinfo >/dev/null 2>&1; then modinfo -F firmware amdgpu; else echo "modinfo is not installed"; fi'
run_readonly 'Relevant kernel messages' bash -c 'if command -v journalctl >/dev/null 2>&1; then journalctl -k -b --no-pager 2>/dev/null | grep -Ei "amdgpu|drm|firmware|dcn|display core|smu|gfx10|vga"; else dmesg 2>/dev/null | grep -Ei "amdgpu|drm|firmware|dcn|display core|smu|gfx10|vga"; fi'
run_readonly 'DRM cards and connectors' bash -c 'for card in /sys/class/drm/card[0-9]*; do test -e "$card" || continue; printf "\n%s\n" "$card"; readlink -f "$card/device" 2>/dev/null || true; for connector in "$card"-*/status; do test -r "$connector" || continue; printf "%s: " "$connector"; cat "$connector"; done; done'
run_readonly 'AMD firmware files installed on this live system' bash -c 'if test -d /lib/firmware/amdgpu; then find /lib/firmware/amdgpu -maxdepth 1 -type f -printf "%f\n" | sort; else echo "/lib/firmware/amdgpu is absent"; fi'

exec 3>&-
printf 'Read-only report written to: %s\n' "$output_path"
