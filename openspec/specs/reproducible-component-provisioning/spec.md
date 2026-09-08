# Reproducible Component Provisioning

## Purpose

Ensure externally sourced development components are provisioned at explicit, verifiable versions or have documented verification exceptions.

## Requirements

### Requirement: Externally sourced components use explicit stable versions
The provisioning configuration SHALL declare an explicit stable version, tag, commit, or package version for every component obtained outside the target operating system package manager. The playbook MUST NOT resolve a default Git branch, an unqualified `latest` channel, or an unversioned installer for such a component unless the component is documented as an approved exception. An upgrade of an installer-managed package manager MUST select and record an explicit current stable version rather than changing to a floating release channel.

#### Scenario: A fresh environment is provisioned
- **WHEN** the playbook provisions an externally sourced component on a fresh supported host
- **THEN** it obtains the version declared in repository configuration rather than an upstream default branch or latest channel

#### Scenario: Provisioning is repeated without configuration changes
- **WHEN** the playbook is rerun with the same component configuration
- **THEN** it retains the declared component version and does not upgrade it because an upstream default has changed

#### Scenario: An installer-managed package manager is upgraded
- **WHEN** a maintainer updates the selected release of an installer-managed package manager
- **THEN** the configuration and associated version inventory record the same explicit current stable version

### Requirement: Downloaded executable content is integrity verified
The provisioning configuration SHALL verify a direct-download executable, archive, or installer script against an authoritative SHA-256 checksum before executing, extracting, or installing it whenever the upstream publisher provides a checksum for that asset.

#### Scenario: A release archive has an authoritative checksum
- **WHEN** a task downloads a release archive whose publisher provides a SHA-256 checksum
- **THEN** the task verifies the archive using that checksum before extraction or installation

#### Scenario: A downloaded asset fails checksum verification
- **WHEN** the bytes returned for a verified direct-download asset do not match its configured SHA-256 checksum
- **THEN** provisioning fails and the asset is not executed, extracted, or installed

### Requirement: Verification exceptions are explicit
The repository SHALL document every externally sourced component that cannot be version- or SHA-256-pinned through its supported upstream distribution method, including the reason and the applicable verification limitation.

#### Scenario: An upstream does not publish an authoritative checksum
- **WHEN** a managed component has no authoritative checksum for its required distribution method
- **THEN** its exception is recorded with the source, reason, and mitigation rather than a fabricated checksum

### Requirement: Distribution package ownership is preserved
The repository SHALL continue to obtain operating-system-managed packages from the configured APT or YUM repositories without introducing unsupported package-version pins.

#### Scenario: A target-distribution package is provisioned
- **WHEN** the playbook installs a package owned by the target operating system package manager
- **THEN** it uses the configured distribution repository and documents that the effective version is distribution-dependent
