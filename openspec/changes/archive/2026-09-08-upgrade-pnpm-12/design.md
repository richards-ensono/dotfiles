## Context

The pnpm Ansible role provisions an exact pnpm version through the official standalone installer into a user-scoped `PNPM_HOME`, verifies the installed version, and then installs configured global packages. The current pin is pnpm 11.21.0. pnpm 12 is a stable Rust-native executable and is compatible with the repository's Node 24 LTS environment, while the standalone installation remains independent of Node at runtime.

The existing `component-version-maintenance` and `reproducible-component-provisioning` specifications govern this work. This change adds a focused scenario to the latter so that installer-managed package-manager upgrades explicitly retain the existing exact-current-stable version policy.

## Goals / Non-Goals

**Goals:**
- Pin the pnpm role to the selected current stable pnpm 12 release.
- Preserve exact-version, user-scoped, idempotent provisioning.
- Keep the role documentation and version/integrity inventory synchronized with configuration.
- Validate the configured version, Ansible syntax, and rerun behavior.

**Non-Goals:**
- Replace the standalone installer with Corepack, npm, or a distribution package.
- Change Node/NVM provisioning or its ordering in the playbook.
- Change pnpm global-package policy, package-store configuration, or downstream project lockfiles.
- Update other external component pins.

## Decisions

### Retain the official standalone installer

Keep `https://get.pnpm.io/install.sh` and pass an explicit `PNPM_VERSION` value.

- The current role already relies on this installer and verifies the resulting executable version.
- pnpm 12 is a native executable, so the standalone delivery model removes its runtime dependency on Node without requiring an architectural change.
- The installer endpoint remains a documented bounded TLS/source exception because upstream does not publish an authoritative checksum for this distribution method.

**Alternatives considered:**
- Use Corepack: would couple pnpm activation to Node/Corepack behavior and depart from the existing standalone provisioning model.
- Install with npm: requires Node 22.13 or newer at installation time and introduces an unnecessary npm-mediated dependency path.
- Use an unpinned `latest` channel: conflicts with the repository's reproducible component provisioning requirements.

### Pin one explicit current pnpm 12 stable version

Select the current stable pnpm 12 version from the authoritative npm registry at implementation time and record that same exact value in the role default, role README, and component inventory.

- Exact pins make repeated provisioning deterministic and let the existing installed-version check decide whether an upgrade is necessary.
- The implementation must not assume the version explored earlier remains current when the work begins.

**Alternatives considered:**
- Float on `latest`: reduces maintenance but allows upstream changes to alter a rerun.
- Upgrade only to the latest pnpm 11 patch: does not deliver the requested Rust-native pnpm 12 release.

### Preserve current user-scoped lifecycle

Keep the existing path, non-privileged user-role execution, removal of the previous global pnpm package before installation, post-install verification, and global-package reinstall behavior.

- pnpm 12 rejects mutating global operations run under `sudo`; the existing user-setup play avoids that condition.
- Preserving these mechanics reduces migration surface and maintains idempotency.

**Alternatives considered:**
- Rebuild the role around pnpm self-update: is unnecessary for a declarative provisioner and can obscure the selected version.

## Risks / Trade-offs

- [pnpm 12 behavior differs for some downstream projects] → Validate the role's own install/version behavior and document that lockfile or settings behavior in independently managed projects is outside this repository's scope.
- [The installer script has no authoritative checksum] → Retain the explicit inventory exception, use the official TLS endpoint, pin `PNPM_VERSION`, and verify the resulting binary's version.
- [The selected release changes before implementation] → Query the npm registry immediately before changing the pin and use the current stable pnpm 12 value found then.
- [A host has globally installed pnpm packages] → Preserve the existing removal and reinstall flow, and validate it with an isolated `PNPM_HOME` where practical.

## Migration Plan

1. Query the official npm registry for the current stable pnpm 12 release at implementation time.
2. Update the role's explicit version and paired documentation/inventory entries.
3. Run narrow Ansible syntax and role-level validation, then provision into an isolated test home if the environment permits.
4. Verify the installed pnpm reports the selected version and a second run does not reinstall it.
5. If validation exposes an installer or lifecycle incompatibility, restore the previous explicit pnpm 11 pin and investigate without weakening verification or using an unpinned fallback.

## Open Questions

- None for the provisioning change. Downstream project-specific compatibility issues, if encountered, should be assessed in those projects rather than absorbed into this dotfiles provisioner.
