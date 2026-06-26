#!/usr/bin/env bash
# Helper script for testing dotfiles in Docker
# This script runs inside the container

set -euo pipefail

run_chezmoi_diff() {
	local exit_code

	set +e
	chezmoi diff --source="$SOURCE_DIR"
	exit_code=$?
	set -e

	if [ "$exit_code" -gt 1 ]; then
		echo "chezmoi diff failed with exit code $exit_code" >&2
		exit "$exit_code"
	fi
}

echo "=== Installing dependencies ==="
apt-get update -qq
apt-get install -y -qq curl git ca-certificates > /dev/null

echo "=== Installing chezmoi ==="
cd /tmp
curl -fsSL https://get.chezmoi.io -o install-chezmoi.sh
chmod +x install-chezmoi.sh
./install-chezmoi.sh -b /usr/local/bin

SOURCE_DIR=/tmp/dotfiles-source
rm -rf "$SOURCE_DIR"
mkdir -p "$SOURCE_DIR"
cp -a /dotfiles/. "$SOURCE_DIR"

echo "=== Chezmoi Diff (what would be applied) ==="
run_chezmoi_diff

echo ""
echo "=== Chezmoi Doctor ==="
chezmoi doctor --source="$SOURCE_DIR"

echo ""
echo "=== Chezmoi Managed Files ==="
chezmoi managed --source="$SOURCE_DIR"
