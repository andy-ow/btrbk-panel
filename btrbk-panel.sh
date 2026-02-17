#!/usr/bin/env bash
set -euo pipefail

LOG="/var/log/btrbk.log"

HELPER="/usr/lib/btrbk-panel/btrbk-helper"

M_T7="/mnt/T7_backup"
M_SAN="/mnt/san128_backup"
M_DF="/mnt/DFilmy_backup"

is_mounted() { findmnt -rn --target "$1" >/dev/null 2>&1; }

fmt() { is_mounted "$1" && echo "TAK" || echo "NIE"; }

run_job() {
  local mode="$1"   # run|dry
  local group="$2"  # T7|san128|DFilmy
  local label="$3"

  # okno z live-logiem (tail)
  yad --title="btrbk log (${label})" --width=900 --height=500 \
      --text-info --tail --filename="$LOG" --wrap \
      --button="Zamknij:0" &
  log_pid=$!

  # progress pulsujący
  (
    echo "# Uruchamiam: ${mode} ${group}"
    echo "0"
    # pkexec pokaże okno autoryzacji
    if pkexec "$HELPER" "$mode" "$group"; then
      echo "100"
      echo "# Zakończone OK"
      exit 0
    else
      echo "100"
      echo "# Błąd (sprawdź log)"
      exit 1
    fi
  ) | yad --progress --pulsate --auto-close --auto-kill \
          --title="btrbk (${label})" --width=420 \
          --text="Wykonywanie btrbk... (log w osobnym oknie)"

  rc=${PIPESTATUS[0]}

  # posprzątaj okno logu
  kill "$log_pid" 2>/dev/null || true

  if [[ $rc -eq 0 ]]; then
    yad --info --title="btrbk" --text="Zakończone: ${label}"
  else
    yad --error --title="btrbk" --text="Błąd podczas: ${label}\nZobacz: ${LOG}"
  fi
}

S_T7="$(fmt "$M_T7")"
S_SAN="$(fmt "$M_SAN")"
S_DF="$(fmt "$M_DF")"

yad --title="Btrbk panel" --width=560 \
  --text="<b>Mount status</b>\n\nT7_backup: <tt>${S_T7}</tt> (${M_T7})\nsan128_backup: <tt>${S_SAN}</tt> (${M_SAN})\nDFilmy_backup: <tt>${S_DF}</tt> (${M_DF})\n\nWybierz akcję:" \
  --button="Run T7:10"      --button="Dry T7:11" \
  --button="Run san128:20"  --button="Dry san128:21" \
  --button="Run DFilmy:30"  --button="Dry DFilmy:31" \
  --button="Zamknij:0"

rc=$?
case "$rc" in
  10) run_job run T7     "Run T7" ;;
  11) run_job dry T7     "Dry T7" ;;
  20) run_job run san128 "Run san128" ;;
  21) run_job dry san128 "Dry san128" ;;
  30) run_job run DFilmy "Run DFilmy" ;;
  31) run_job dry DFilmy "Dry DFilmy" ;;
  *) exit 0 ;;
esac
