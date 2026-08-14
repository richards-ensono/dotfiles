# Component Version Maintenance

## Purpose

Maintain an auditable inventory of managed component versions and their integrity metadata.

## Requirements

### Requirement: Managed component versions are maintained at current stable releases
The repository SHALL record the selected stable version for each externally sourced managed component in its provisioning configuration or an associated version inventory. The selected versions MUST correspond to the latest stable upstream releases evaluated for the change, except where a documented compatibility constraint requires a different version.

#### Scenario: A managed component is reviewed for an update
- **WHEN** a maintainer reviews the managed component inventory
- **THEN** the repository identifies its selected version, upstream source, and any documented reason it is not at the latest stable release

### Requirement: Version and integrity metadata remain coupled
For a component installed from a versioned direct-download asset, its configured version, download URL, and integrity metadata SHALL identify the same release asset.

#### Scenario: A component release is updated
- **WHEN** a maintainer changes a direct-download component version
- **THEN** the associated URL and SHA-256 checksum are updated to the corresponding upstream release asset

### Requirement: Provisioning configuration is validated
Repository validation SHALL check the changed provisioning configuration for syntax and idempotent managed-version behavior.

#### Scenario: Version metadata is internally inconsistent
- **WHEN** a task's configured version does not match its release URL, checksum, or installed-version check
- **THEN** provisioning validation fails before the inconsistent configuration is accepted
