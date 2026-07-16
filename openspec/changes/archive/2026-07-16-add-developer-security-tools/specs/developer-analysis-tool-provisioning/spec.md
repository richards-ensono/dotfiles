## ADDED Requirements

### Requirement: Standard developer analysis tools are provisioned
The Ansible developer environment playbook SHALL provision the `govulncheck`, `staticcheck`, `gosec`, and `actionlint` commands as part of its standard working set. Each command MUST be available on PATH to the provisioned developer after a successful playbook run.

#### Scenario: Fresh environment receives the standard toolset
- **WHEN** the Ansible playbook completes successfully on a supported host
- **THEN** `govulncheck`, `staticcheck`, `gosec`, and `actionlint` are each discoverable on PATH and executable

### Requirement: Tool installation is declarative and idempotent
The playbook SHALL define the source module and version for every standard developer analysis tool. A repeated playbook run with unchanged tool configuration MUST NOT reinstall or update a tool that already matches its managed version.

#### Scenario: Playbook is rerun without configuration changes
- **WHEN** the playbook has already provisioned the standard developer analysis toolset and is run again with the same configuration
- **THEN** the tool-installation tasks report no changes for tools that already match the managed versions

### Requirement: Provisioning validation covers the standard toolset
The repository's Ansible provisioning validation SHALL check each standard developer analysis command after the initial playbook run and before asserting second-run idempotence.

#### Scenario: Validation runs after a successful first playbook run
- **WHEN** the Ansible provisioning validation completes its first playbook run
- **THEN** it verifies that `govulncheck`, `staticcheck`, `gosec`, and `actionlint` can each be located and invoked successfully

#### Scenario: A required developer tool is unavailable
- **WHEN** any standard developer analysis command cannot be found or invoked after the first playbook run
- **THEN** the provisioning validation fails with the unavailable command identified
