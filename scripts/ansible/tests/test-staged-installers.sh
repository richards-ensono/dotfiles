#!/usr/bin/env bash
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
command -v ansible-playbook >/dev/null
python3 "$script_dir/test_staged_installers.py" -v
