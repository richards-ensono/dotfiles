## Why

Provisioned developer environments lack a consistent baseline of Go vulnerability, static-analysis, security, and GitHub Actions workflow validation tools. Adding these tools to the Ansible playbook lets developers run the same checks locally without manual, per-machine installation.

## What Changes

- Provision `govulncheck`, `staticcheck`, and `gosec` as Go-based developer analysis tools.
- Provision `actionlint` for validating GitHub Actions workflow files.
- Make all four commands available on PATH after a standard Ansible playbook run.
- Add automated provisioning validation for command availability while retaining the existing idempotence check.

## Capabilities

### New Capabilities
- `developer-analysis-tool-provisioning`: Provisioned developer environments provide the standard Go security and static-analysis commands plus GitHub Actions workflow linting.

### Modified Capabilities
- None.

## Impact

- `scripts/ansible/group_vars/all.yml` and the Ansible roles responsible for shared packages, Go tooling, or user-local tools.
- `scripts/ansible/playbook.yml` if a dedicated role must be included in play ordering.
- `.vscode/test-ansible-idempotence.sh` or equivalent provisioning validation.
- Go module downloads and an `actionlint` package or release source; no application API or user data changes.
