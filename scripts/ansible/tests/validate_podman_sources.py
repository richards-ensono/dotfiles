#!/usr/bin/env python3
"""Reject mutable managed Podman source refs, retaining existing role names."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def validate(root):
    role = root / "scripts/ansible/roles/podman"
    text = "\n".join(p.read_text(encoding="utf-8") for p in role.rglob("*.yml"))
    errors = []
    for variable in ["podman_containers_image_ref", "podman_source_commit"]:
        if not re.search(rf'{variable}:\s*"[0-9a-f]{{40}}"', text):
            errors.append(f"{variable} must use a reviewed full commit")
    for ref in re.findall(r"https://raw\.githubusercontent\.com/containers/image/([^/\s\"]+)", text):
        if ref != "{{" and not re.fullmatch(r"[0-9a-f]{40}", ref):
            errors.append("Mutable managed Podman configuration URL")
    if "{{ podman_containers_image_ref }}" not in text:
        errors.append("Podman configuration must reference its immutable source variable")
    if "== podman_source_commit" not in text:
        errors.append("Podman checkout must be checked against its immutable source commit")
    return errors


if __name__ == "__main__":
    errors = validate(ROOT)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print("PASS: Podman managed sources use reviewed immutable refs")
