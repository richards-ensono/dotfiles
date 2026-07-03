#!/usr/bin/env bash
set -uo pipefail

config="dot_config/oh-my-posh/ensono.omp.json"
config_dir="$(dirname "$config")"
config_file="$(basename "$config")"
cmd="oh-my-posh print primary --config ${config}"

run_prompt() {
  clear
  script -qfec "$cmd" /dev/null || true
}

command -v inotifywait >/dev/null 2>&1 || {
  echo "Error: inotifywait not found. Install it with: sudo apt install inotify-tools" >&2
  exit 1
}

trap 'echo; exit 130' INT

run_prompt

inotifywait -m -q -e close_write,modify,move,create,delete "$config_dir" |
while read -r _dir _events file; do
  if [[ "$file" == "$config_file" ]]; then
    run_prompt
  fi
done
