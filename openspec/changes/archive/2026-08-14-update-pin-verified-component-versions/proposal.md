## Why

The provisioning configuration contains outdated component pins and several floating installation sources (default Git branches, `latest` channels, unversioned installer scripts, and unpinned Ansible collections). This makes developer environments non-reproducible and leaves the repository without a consistent integrity-verification policy for downloaded artifacts.

## What Changes

- Update explicitly managed development tools to their latest stable releases identified by the version audit.
- Replace floating version semantics with explicit, stable version pins wherever the upstream installation mechanism supports them.
- Verify downloaded release artifacts and installer scripts with SHA-256 checksums when authoritative checksums are available.
- Pin source-build Git revisions and package/collection versions so repeated provisioning produces the intended version.
- Define a documented exception policy for components that cannot be version- and hash-pinned through their supported upstream distribution method.
- Preserve the existing OS package-manager behavior for distribution-managed dependencies while documenting that their effective version is determined by the target distribution repository.

## Capabilities

### New Capabilities
- `reproducible-component-provisioning`: Provisions externally sourced development components at explicit stable versions with integrity verification or a documented exception.
- `component-version-maintenance`: Records and validates the managed component-version inventory so future upgrades can be made consistently.

### Modified Capabilities
- `developer-analysis-tool-provisioning`: Update the required Go analysis-tool versions and retain pinned-module installation behavior.

## Impact

- Affected Ansible role defaults, variables, and installation tasks under `scripts/ansible/roles/`.
- Affected Ansible Galaxy requirements in `scripts/ansible/requirements.yml`, bootstrap instructions in `README.md`, and versioned Neovim plugin configuration where applicable.
- May require authoritative upstream checksum acquisition and version-specific installer URLs or release assets.
- Changes the provisioning contract from opportunistic latest/default-branch resolution to explicit, reviewable versions.
