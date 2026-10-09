## 1. Provision Bubblewrap

- [x] 1.1 Add the distribution-managed `bubblewrap` package to `packages_managed_packages` in `scripts/ansible/group_vars/all.yml`.
- [x] 1.2 Confirm the shared `packages` role provisions `bubblewrap` without adding agent-specific configuration or changing kernel security policy.

## 2. Validate command availability

- [x] 2.1 Extend `.vscode/test-ansible-idempotence.sh` to locate `bwrap` after the first playbook run and invoke `bwrap --version` successfully.
- [x] 2.2 Run the narrow relevant validation, including the Ansible provisioning/idempotence test, and confirm the second run reports zero changes.

## 3. Migrate the Debian baseline, audit pins, and restore provisioning-test compatibility

- [x] 3.1 Replace every Docker developer-check image with `debian:trixie`, remove the Debian Bookworm-specific Ansible bootstrap branch, and verify Trixie uses distribution-provided Ansible packages.
- [x] 3.2 Audit every managed external-component pin family against authoritative publisher sources; record each family’s latest compatible stable candidate and disposition before changing any direct-download pin.
- [x] 3.3 Select a Netavark/Aardvark-DNS pair compatible with the Podman role and Debian 13/Trixie; retrieve authoritative publisher checksums and locally verify each configured asset before editing pins.
- [x] 3.4 Update only verified, compatible pin configurations and their coupled inventory, lock, or assertion files; preserve the existing staged Podman helper installation and rollback behavior.
- [x] 3.5 Run component-specific validation, the focused Podman helper checks, and the full Ansible provisioning/idempotence test; confirm the first pass reaches `bwrap --version` and the second pass reports zero changes.
