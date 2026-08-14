## MODIFIED Requirements

### Requirement: Tool installation is declarative and idempotent
The playbook SHALL define the source module and explicit stable version for every standard developer analysis tool. The configured version MUST be the selected current stable upstream module release for this change, unless a documented compatibility constraint requires otherwise. A repeated playbook run with unchanged tool configuration MUST NOT reinstall or update a tool that already matches its managed version.

#### Scenario: Playbook is rerun without configuration changes
- **WHEN** the playbook has already provisioned the standard developer analysis toolset and is run again with the same configuration
- **THEN** the tool-installation tasks report no changes for tools that already match the managed versions

#### Scenario: A managed analysis-tool version is upgraded
- **WHEN** a maintainer updates an analysis tool to its selected stable upstream module release
- **THEN** the module source and exact version are recorded together and the playbook installs that version with `go install`
