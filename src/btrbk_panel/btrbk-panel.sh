#!/usr/bin/env bash
set -uo pipefail
set +e
LOG="/var/log/btrbk.log"
HELPER="/usr/lib/btrbk-panel/btrbk-helper"

# panel logów (prawy)
log_fifo="$(mktemp -u)"
mkfifo "$log_fifo"
cleanup(){ rm -f "$log_fifo"; }
trap cleanup EXIT

# uruchom "tail" logu do fifo (żeby mieć live)
( tail -n 200 -f "$LOG" > "$log_fifo" ) &

# lewy panel: lista akcji; prawy panel: text-info z tail
# --paned pozwala mieć dwa widgety w jednym oknie
yad --title="Btrbk panel" --width=1100 --height=600 --paned \
  --key="$$" \
  --splitter=350 \
  \
  --list --no-headers --listen --print-column=1 \
  --column="action" \
  "run:T7" "dry:T7" \
  "run:san128" "dry:san128" \
  "run:DFilmy" "dry:DFilmy" \
  \
  : \
  --text-info --tail --filename="$log_fifo" --wrap \
| while IFS= read -r action; do
    # action np. "run:T7"
    mode="${action%%:*}"
    group="${action#*:}"

    # (opcjonalnie) dopisz do logu informację
    echo "=== UI: requested ${mode} ${group} @ $(date) ===" | pkexec /usr/bin/tee -a "$LOG" >/dev/null

    # odpal btrbk przez pkexec (blokująco; jeśli chcesz równolegle -> dodaj &)
    pkexec "$HELPER" "$mode" "$group" || true
done
