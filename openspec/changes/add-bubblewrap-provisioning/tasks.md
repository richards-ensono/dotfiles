## 1. Provision Bubblewrap

- [x] 1.1 Add the distribution-managed `bubblewrap` package to `packages_managed_packages` in `scripts/ansible/group_vars/all.yml`.
- [x] 1.2 Confirm the shared `packages` role provisions `bubblewrap` without adding agent-specific configuration or changing kernel security policy.

## 2. Validate command availability

- [x] 2.1 Extend `.vscode/test-ansible-idempotence.sh` to locate `bwrap` after the first playbook run and invoke `bwrap --version` successfully.
- [ ] 2.2 Run the narrow relevant validation, including the Ansible provisioning/idempotence test, and confirm the second run reports zero changes.

## 3. Restore provisioning-test baseline compatibility

- [ ] 3.1 Select a Netavark/Aardvark-DNS pair compatible with the Podman role and Debian Bookworm; retrieve authoritative publisher checksums and locally verify each configured asset before editing pins.
- [ ] 3.2 Update the coupled Podman helper versions, URLs, checksums, assertions, and `docs/COMPONENT_VERSION_INVENTORY.md` together, preserving the existing staged installation and rollback behavior.
- [ ] 3.3 Run the Podman helper-specific validation and the full Ansible provisioning/idempotence test; confirm the first pass reaches `bwrap --version` and the second pass reports zero changes.
