#!/bin/sh
# Validate that the configured Podman Compose provider can create its network.
set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
compose_file="$script_dir/podman-compose-network.yml"
project_name="podman-network-helper-validation"

cleanup() {
  podman compose --project-name "$project_name" --file "$compose_file" down \
    --volumes --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

podman compose --project-name "$project_name" --file "$compose_file" up \
  --abort-on-container-exit --exit-code-from probe
