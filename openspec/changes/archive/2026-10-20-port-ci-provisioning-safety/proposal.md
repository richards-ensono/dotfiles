# Port CI and provisioning safety

## Why

The personal dotfiles repository has useful validation and recovery safeguards that are missing from the work repository. Port only CI, staged .NET/Neovim/Podman installation, focused regression tests, and preservation-aware Pi settings management.

## What changes

- Add least-privilege GitHub CI with immutable action references, lint, syntax, isolated rendering, regression tests, and scheduled/manual idempotence checks.
- Stage and verify installer output before activation; preserve existing installations/configuration and restore on failure.
- Add offline failure-path fixtures, immutable-source/plugin-lock validators, and isolated Podman network checks.
- Merge a repository-owned Pi settings fragment into existing settings atomically, preserving unowned preferences.

## Non-goals

No new developer tools, runtime managers, themes, personal identities, role renames, package removals, or unrelated dependency/version upgrades. Preserve the work repository's existing role APIs, security tooling, rootless configuration, and YubiKey signing.

## Reference

Adapted from RichardSlater/dotfiles at 38b2df53dba253eeeb4cce38ddb039ef7febc051; changes are newly authored for richards-ensono, not cherry-picked personal-account commits.
