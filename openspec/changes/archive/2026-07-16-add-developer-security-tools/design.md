## Context

The Ansible playbook currently installs the shared package list and the `geerlingguy.go` role in its privileged system-setup play. It does not provision the requested Go analysis commands or `actionlint`; developers must install and update them manually. The existing Docker idempotence test checks `fd` after the first run and validates that the second run reports no changes.

## Goals / Non-Goals

**Goals:**
- Provision `govulncheck`, `staticcheck`, `gosec`, and `actionlint` through the standard Ansible playbook.
- Make each command machine-wide and discoverable on PATH after provisioning.
- Make tool versions declarative and keep installation idempotent.
- Verify all four commands in the provisioning test before its second-run idempotence assertion.

**Non-Goals:**
- Configure these tools in individual repositories, editors, CI workflows, or pre-commit hooks.
- Run vulnerability, static-analysis, security, or workflow checks as part of workstation provisioning.
- Support operating systems or package managers beyond the repository's current Debian/apt baseline.
- Manage developers' project-local Go dependencies or tool configuration files.

## Decisions

### Create a dedicated Ansible role for the standard Go developer tools

Create a system-level role that runs after `geerlingguy.go` in the system setup play. The role will own the requested commands, while shared, user-overridable tool names, module paths, and versions live in role defaults or centralized configuration according to the repository's variable conventions. This separates Go-installed developer commands from apt packages and prevents unrelated roles from accumulating tool-specific behavior.

**Alternatives considered:**
- Add all tools to the `packages` role: rejected because the requested commands are Go modules and apt availability/versioning is inconsistent across supported distributions.
- Add install commands to the `geerlingguy.go` role configuration: rejected because that external role owns Go runtime setup, not repository-specific developer tool policy.
- Add one-off tasks directly to `playbook.yml`: rejected because a dedicated role is clearer, reusable, and easier to test.

### Install pinned Go modules into a machine-wide PATH directory

The role will use `go install <module>@<version>` for each tool with an explicit `GOBIN` in a standard PATH directory such as `/usr/local/bin`. Version values will be declared rather than relying on implicit `latest`, and each tool will be checked before installation so repeated playbook runs converge without rebuilding unchanged versions.

**Alternatives considered:**
- Use `@latest`: rejected because provisioning would not be reproducible and future runs could change tool behavior unexpectedly.
- Install into a user's Go bin directory: rejected because availability would depend on a particular user and shell PATH configuration.
- Download arbitrary prebuilt binaries: rejected because Go modules provide a consistent installation mechanism for all four requested Go-based tools.

### Verify command availability in the existing provisioning test

After the first playbook run, extend the idempotence script to locate and invoke `govulncheck`, `actionlint`, `staticcheck`, and `gosec` with a non-destructive version or help invocation. Retain the existing second run and zero-change assertion to prove convergence.

**Alternative considered:** rely on Ansible task success only: rejected because it does not prove that every expected executable is available to developers on PATH.

## Risks / Trade-offs

- [A selected tool version requires a newer Go version than the provisioned runtime] → Select compatible pinned versions and fail early with the tool name and Go requirement if installation cannot proceed.
- [Go module downloads are unavailable or checksum verification fails] → Use the public Go module proxy/checksum database and allow the playbook to fail clearly rather than leaving a partially provisioned toolset.
- [A PATH directory contains an unrelated binary with the same name] → Inspect existing commands and only replace binaries managed by the role; fail clearly on an unmanaged conflict.
- [Tool versions become stale] → Keep each version in declarative variables so a future change can review and upgrade the toolset deliberately.

## Migration Plan

1. Add the dedicated role and its versioned tool configuration.
2. Insert the role after Go runtime provisioning in the privileged system setup play.
3. Run syntax and idempotence checks, including command availability after the initial run.
4. Roll back by removing the role from the playbook and its managed binaries if a tool causes provisioning failures; existing development environment configuration is otherwise unaffected.

## Open Questions

- None; exact compatible tool versions will be selected during implementation against the provisioned Go version.
