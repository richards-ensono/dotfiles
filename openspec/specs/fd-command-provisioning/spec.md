# fd Command Provisioning

## Purpose

Ensure Ansible system setup provisions the `fd` command and verifies its availability after provisioning.

## Requirements

### Requirement: Provision the fd command
The Ansible system setup SHALL install the supported package that supplies `fd` functionality and SHALL make an executable named `fd` available on the provisioned host's standard PATH. The provisioning logic MUST NOT replace a pre-existing non-managed `fd` executable or file.

#### Scenario: Fresh supported host receives fd
- **WHEN** the Ansible playbook runs on a supported Debian/apt host that has no conflicting `fd` path
- **THEN** the host has an executable `fd` command available on its standard PATH after provisioning completes

#### Scenario: Existing fd path conflicts with managed command
- **WHEN** the Ansible playbook finds a pre-existing non-managed file or executable at the intended `fd` path
- **THEN** the playbook does not overwrite the path and reports the conflict clearly

### Requirement: Validate fd after provisioning
The repository's automated Ansible provisioning test SHALL verify that `fd` is discoverable on PATH and executable after the playbook's first successful run. The test MUST retain its assertion that the second playbook run is idempotent.

#### Scenario: Provisioning test validates fd availability
- **WHEN** the automated Ansible provisioning test completes its first playbook run
- **THEN** it confirms that `fd` can be located on PATH and invoked successfully before executing the second run

#### Scenario: fd is unavailable after provisioning
- **WHEN** the first playbook run completes without an executable `fd` command on PATH
- **THEN** the automated Ansible provisioning test fails with an error that identifies the missing command
