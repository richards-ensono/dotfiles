## Why

Neovim reports that the `fd` command is unavailable on provisioned hosts, so file-search features that depend on it cannot work. Provisioning should install and expose `fd` consistently, and automated validation should prevent this regression from recurring.

## What Changes

- Add `fd` to the Ansible-managed developer tooling for supported hosts.
- Ensure the installed package provides an executable available as `fd`, including handling distribution package naming differences when needed.
- Extend Ansible provisioning tests to verify that `fd` is present and executable after the playbook runs.

## Capabilities

### New Capabilities
- `fd-command-provisioning`: Provisioned development environments provide an executable `fd` command and validate its availability.

### Modified Capabilities
- None.

## Impact

- `scripts/ansible/group_vars/all.yml` and/or the packages role configuration that defines common developer packages.
- Ansible tasks needed to expose the expected `fd` command on supported Debian/apt hosts.
- The repository's Ansible idempotence or provisioning test script.
- No application API or user data changes.
