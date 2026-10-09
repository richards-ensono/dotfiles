## MODIFIED Requirements

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
