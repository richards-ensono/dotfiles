#!/usr/bin/env python3
"""Check declared immutable plugin pins against the work repo's lockfile."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def validate(root):
    text = (root / ".chezmoitemplates/nvim/init.lua").read_text(encoding="utf-8")
    lock = json.loads((root / ".chezmoitemplates/nvim/lazy-lock.json").read_text(encoding="utf-8"))
    if not isinstance(lock, dict):
        return ["Neovim lockfile must be an object"]
    pins = re.findall(r'\{\s*"([^"\s]+/[^"\s]+)"[^{}]*?commit\s*=\s*"([0-9a-f]+)"', text)
    errors = []
    if not pins:
        errors.append("No explicit plugin pins found")
    for repository, commit in pins:
        plugin = repository.rsplit("/", 1)[1]
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            errors.append(f"{plugin}: declaration must use a full commit")
        entry = lock.get(plugin, {})
        if not isinstance(entry, dict) or entry.get("commit") != commit:
            errors.append(f"{plugin}: lockfile does not match its declared commit")
    bootstrap = re.search(r'local lazycommit = "([0-9a-f]{40})"', text)
    if bootstrap is None:
        errors.append("lazy.nvim bootstrap must use a full immutable commit")
    elif lock.get("lazy.nvim", {}).get("commit") != bootstrap.group(1):
        errors.append("lazy.nvim: lockfile does not match bootstrap commit")
    return errors


if __name__ == "__main__":
    try:
        errors = validate(ROOT)
    except (OSError, ValueError, AttributeError) as error:
        print(f"FAIL: Neovim lock input could not be validated ({type(error).__name__})")
        sys.exit(1)
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print("PASS: Neovim explicit plugin and bootstrap pins match the lockfile")
