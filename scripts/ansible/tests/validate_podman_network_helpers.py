#!/usr/bin/env python3
"""Ensure existing distro-owned network helpers remain provisioned."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def validate(root):
    role = root / "scripts/ansible/roles/podman"
    text = (role / "tasks/main.yml").read_text(encoding="utf-8")
    variables = (role / "vars/main.yml").read_text(encoding="utf-8")
    errors = []
    for helper in ["netavark", "aardvark-dns"]:
        if f"      - {helper}\n" not in text:
            errors.append(f"Existing distro helper {helper} must remain provisioned")
    if "podman_package_map[podman_network_handler]" not in text:
        errors.append("Selected rootless network handler must remain provisioned")
    if 'pasta: "passt"' not in variables or 'slirp4netns: "slirp4netns"' not in variables:
        errors.append("Rootless network handler package map is incomplete")
    return errors


if __name__ == "__main__":
    errors = validate(ROOT)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print("PASS: existing Podman network-helper ownership is retained")
