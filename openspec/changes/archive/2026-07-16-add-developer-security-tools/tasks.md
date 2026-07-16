## 1. Define the managed toolset

- [x] 1.1 Create the dedicated Ansible role structure for standard Go developer analysis tools, including its metadata and defaults.
- [x] 1.2 Declare compatible pinned Go module sources and versions for `govulncheck`, `staticcheck`, `gosec`, and `actionlint` in the role configuration.

## 2. Provision the tools

- [x] 2.1 Add idempotent role tasks that verify the Go runtime and install each configured module into a machine-wide PATH directory.
- [x] 2.2 Detect an existing unmanaged command conflict and fail with clear remediation rather than overwriting it.
- [x] 2.3 Add the role to the privileged system setup play after `geerlingguy.go` so the toolset is installed only after Go is available.
- [x] 2.4 Verify each managed command is present and executable at the end of the role.

## 3. Validate provisioning

- [x] 3.1 Extend `.vscode/test-ansible-idempotence.sh` to locate and invoke `govulncheck`, `staticcheck`, `gosec`, and `actionlint` after the first playbook run.
- [x] 3.2 Run `ansible-playbook playbook.yml --syntax-check` from `scripts/ansible`.
- [x] 3.3 Run the Ansible provisioning/idempotence test and confirm all four commands are usable and the unchanged second run reports zero changes.
