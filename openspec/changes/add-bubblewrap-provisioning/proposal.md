## Why

Agent-driven commands need a locally available, unprivileged namespace-sandboxing utility. Bubblewrap is available from the supported Debian/apt repositories and provides the `bwrap` command required to run those commands with explicitly scoped isolation.

## What Changes

- Add the distribution-managed `bubblewrap` package to the shared Ansible system package configuration.
- Verify after the first Ansible provisioning run that `bwrap` is discoverable on `PATH` and executes its version command.
- Repair the pinned Podman network-helper pair so it remains compatible with the Debian Bookworm idempotence-test baseline, using an authoritative upstream release and checksum verification.
- Retain the existing two-pass idempotence assertion for provisioning.

## Capabilities

### New Capabilities
- `bubblewrap-command-provisioning`: Provision and validate the `bwrap` command on supported hosts.

### Modified Capabilities

- `bubblewrap-command-provisioning`: Keep the provisioning test baseline able to complete its first playbook run before validating `bwrap`.

## Impact

- `scripts/ansible/group_vars/all.yml` gains one Debian/apt-managed package.
- `.vscode/test-ansible-idempotence.sh` gains command-availability coverage for `bwrap`.
- `scripts/ansible/roles/podman/defaults/main.yml` and `docs/COMPONENT_VERSION_INVENTORY.md` gain a coupled, verified update for the Podman network-helper pair.
- No agent sandbox policy, Bubblewrap command wrapper, or API changes are introduced.
