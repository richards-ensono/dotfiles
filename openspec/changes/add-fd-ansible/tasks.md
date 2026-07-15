## 1. Provision fd

- [x] 1.1 Add the supported Debian `fd-find` package to the shared Ansible package configuration.
- [x] 1.2 Add an idempotent Ansible task that exposes the package executable as `fd` on PATH without replacing a conflicting non-managed target.
- [x] 1.3 Ensure the task reports a clear failure when a pre-existing non-managed `fd` target conflicts with provisioning.

## 2. Validate provisioning

- [x] 2.1 Extend `.vscode/test-ansible-idempotence.sh` to verify that `fd` is discoverable on PATH and can be invoked after the first playbook run.
- [ ] 2.2 Run the Ansible provisioning/idempotence test and confirm both `fd` availability and a zero-change second run.
