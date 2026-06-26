#!/usr/bin/env bash

set -euo pipefail

SOURCE_DIR=/tmp/dotfiles-source

echo "=== Installing dependencies ==="
apt-get update -qq
apt-get install -y -qq ansible python3-apt sudo git curl ca-certificates > /dev/null

rm -rf "$SOURCE_DIR"
mkdir -p "$SOURCE_DIR"
cp -a /dotfiles/. "$SOURCE_DIR"

cd "$SOURCE_DIR/scripts/ansible"

echo "=== Installing Galaxy requirements ==="
ansible-galaxy install -r requirements.yml > /dev/null

echo "=== First playbook run ==="
ansible-playbook playbook.yml -i inventory/hosts.yml -c local | tee /tmp/ansible-first-run.log

echo "=== Second playbook run ==="
ansible-playbook playbook.yml -i inventory/hosts.yml -c local | tee /tmp/ansible-second-run.log

recap_line="$(grep '^localhost' /tmp/ansible-second-run.log | tail -n 1 || true)"

if [ -z "$recap_line" ]; then
  echo "Missing play recap from second run" >&2
  exit 1
fi

changed_count="$(printf '%s\n' "$recap_line" | sed -n 's/.*changed=\([0-9][0-9]*\).*/\1/p')"
failed_count="$(printf '%s\n' "$recap_line" | sed -n 's/.*failed=\([0-9][0-9]*\).*/\1/p')"
unreachable_count="$(printf '%s\n' "$recap_line" | sed -n 's/.*unreachable=\([0-9][0-9]*\).*/\1/p')"

if [ -z "$changed_count" ] || [ -z "$failed_count" ] || [ -z "$unreachable_count" ]; then
  echo "Could not parse play recap: $recap_line" >&2
  exit 1
fi

if [ "$failed_count" -ne 0 ] || [ "$unreachable_count" -ne 0 ]; then
  echo "Second playbook run failed: $recap_line" >&2
  exit 1
fi

if [ "$changed_count" -ne 0 ]; then
  echo "Second playbook run was not idempotent: $recap_line" >&2
  exit 1
fi

echo "Second run was idempotent: $recap_line"
