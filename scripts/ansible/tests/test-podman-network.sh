#!/usr/bin/env bash
# Run only on a disposable provisioned host/container; creates one temporary
# network and never prunes existing images, volumes, containers or networks.
set -euo pipefail
if [ "${DOTFILES_ISOLATED_TEST:-}" != 1 ]; then
  echo "Set DOTFILES_ISOLATED_TEST=1 only in a disposable provisioned environment." >&2
  exit 1
fi
stage="$(mktemp -d)"
network="dotfiles-network-${stage##*/}"
created=false
cleanup() {
  if [ "$created" = true ]; then
    podman network rm "$network" >/dev/null
  fi
  rm -rf "$stage"
}
trap cleanup EXIT
podman info --format '{{.Host.NetworkBackendInfo.Path}} {{.Host.NetworkBackendInfo.Version}}'
podman network create "$network" > "$stage/network-id"
created=true
podman network inspect "$network" > "$stage/network.json"
python3 - "$stage/network.json" "$network" <<'PY'
import json
import sys
from pathlib import Path
networks = json.loads(Path(sys.argv[1]).read_text())
assert len(networks) == 1 and networks[0]["name"] == sys.argv[2]
PY
printf 'PASS: isolated Podman network creation and inspection\n'
