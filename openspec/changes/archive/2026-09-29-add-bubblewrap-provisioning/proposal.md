## Why

Agent-driven commands need a locally available, unprivileged namespace-sandboxing utility. Bubblewrap is available from the supported Debian/apt repositories and provides the `bwrap` command required to run those commands with explicitly scoped isolation.

## What Changes

- Add the distribution-managed `bubblewrap` package to the shared Ansible system package configuration.
- Verify after the first Ansible provisioning run that `bwrap` is discoverable on `PATH` and executes its version command.
- Audit every externally sourced managed version-pin family from authoritative publisher sources, recording each current, compatibility-held, blocked, or updated disposition.
- Migrate the repository’s Debian Docker test baseline to Debian 13/Trixie, retire the Debian Bookworm-specific Ansible bootstrap path, and apply only verified, stable, compatible pin updates, including the Podman network-helper pair required by that baseline.
- Retain the existing two-pass idempotence assertion for provisioning.

## Capabilities

### New Capabilities
- `bubblewrap-command-provisioning`: Provision and validate the `bwrap` command on supported hosts.

### Modified Capabilities

- `bubblewrap-command-provisioning`: Keep the provisioning test baseline able to complete its first playbook run before validating `bwrap`, while preserving reproducible external-component provisioning.

## Impact

- `scripts/ansible/group_vars/all.yml` gains one Debian/apt-managed package.
- `.vscode/test-ansible-idempotence.sh` gains command-availability coverage for `bwrap`.
- `.vscode/tasks.json` moves all Docker developer checks to `debian:trixie`; `scripts/ansible/private_executable_exec.sh` removes its Debian Bookworm-specific PPA path.
- Managed pin configuration, locks where their documented update process applies, and `docs/COMPONENT_VERSION_INVENTORY.md` may receive coupled, verified updates for every reviewed pin family; the Podman network-helper pair is a required compatibility repair.
- No agent sandbox policy, Bubblewrap command wrapper, or API changes are introduced.
