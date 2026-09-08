## Why

The provisioning role currently installs pnpm 11.21.0. pnpm 12 is the current stable release line and provides the supported Rust-native executable while preserving the established standalone, exact-version installation model.

## What Changes

- Update the pnpm role's explicit version pin from pnpm 11 to the selected current stable pnpm 12 release.
- Retain the official standalone installer, user-scoped installation path, installed-version verification, and global-package reinstall behavior.
- Update the pnpm role documentation and component version/integrity inventory with the new selected version and the existing documented installer verification exception.
- Validate provisioning syntax and version/idempotency behavior without changing unrelated component pins.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `reproducible-component-provisioning`: clarify that an upgrade of an installer-managed package manager remains an explicit stable-version provisioning operation.

## Impact

- Affected configuration: `scripts/ansible/roles/pnpm/defaults/main.yml`.
- Affected documentation: `scripts/ansible/roles/pnpm/README.md` and `docs/COMPONENT_VERSION_INVENTORY.md`.
- Provisioned developer hosts will replace pnpm 11 with pnpm 12 during the next Ansible run.
- No application dependency manifests, lockfiles, public APIs, or unrelated provisioning roles are changed.
