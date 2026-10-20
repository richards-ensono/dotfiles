# Provisioning safety

## ADDED Requirements

### Requirement: Isolated continuous validation

The repository SHALL validate shell/YAML/Ansible inputs, Chezmoi rendering, and focused regressions in CI without applying provisioning to a real home directory. Workflow actions SHALL use immutable references and read-only repository permissions.

#### Scenario: Pull request validation

- WHEN a pull request targets main
- THEN CI runs static checks, isolated template validation and offline regression tests
- AND full provisioning idempotence remains a scheduled/manual isolated check.

### Requirement: Recoverable installation

.NET, Neovim and Podman installation SHALL stage and verify replacements before activation, reject existing recovery paths, restore prior managed state on activation/verification failure, and report failure.

#### Scenario: Replacement fails validation

- WHEN a staged replacement cannot be verified
- THEN the active installation remains unchanged.

#### Scenario: Activated replacement fails verification

- WHEN verification fails after replacement begins
- THEN the previous executable/runtime or configuration is restored
- AND the task fails visibly.

### Requirement: Preservation-aware Pi settings

Chezmoi SHALL merge its owned settings fragment into the destination's existing Pi settings, preserve unowned keys, reject invalid input without altering the file, and use an atomic restrictive-permission write.

#### Scenario: Local preferences exist

- WHEN the settings hook runs repeatedly
- THEN managed keys are enforced, unowned preferences are retained, and unchanged settings are not rewritten.
