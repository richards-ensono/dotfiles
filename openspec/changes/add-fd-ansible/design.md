## Context

The shared Ansible package list provisions common command-line tools on Debian/apt hosts through the `packages` role. Neovim expects a command named `fd`, but Debian packages the tool as `fd-find` and exposes its executable as `fdfind`. The existing idempotence test confirms a converged second playbook run but does not assert that required developer commands are usable.

## Goals / Non-Goals

**Goals:**
- Install the distribution-supported `fd-find` package through the common Ansible package configuration.
- Expose its executable as `fd` in a standard PATH directory without overwriting an unrelated existing `fd` command.
- Verify the post-provisioning environment can invoke `fd`, while preserving the existing idempotence assertion.

**Non-Goals:**
- Supporting package managers or operating systems outside the repository's current Debian/apt baseline.
- Installing the Rust crate or a separately downloaded release of `fd`.
- Changing Neovim configuration or adding configuration-specific fallback behavior.

## Decisions

### Use the Debian package and create a compatibility symlink

Add `fd-find` to the shared package list, then use an idempotent Ansible file task to link the package's `fdfind` executable to `fd` in a standard PATH location (for example, `/usr/local/bin/fd`). This uses the supported system package, makes the Neovim-expected command name available, and lets Ansible report no changes on subsequent runs.

**Alternatives considered:**
- Install only `fd-find`: rejected because it leaves the executable named `fdfind`, so Neovim still cannot discover `fd`.
- Install via Cargo: rejected because it introduces a Rust toolchain dependency and bypasses the system package manager for a baseline utility.
- Modify Neovim to use `fdfind`: rejected because provisioning should satisfy the conventional `fd` command expected by tools.

### Preserve an existing non-symlink `fd` command

The compatibility task will inspect the target path and avoid replacing an existing command that is not the managed symlink. This prevents an unrelated package or user-installed binary from being silently overwritten; the playbook will fail clearly or skip with an explicit assertion if the target conflicts.

**Alternative considered:** force the link: rejected because it can unexpectedly replace an existing executable.

### Validate command availability in the provisioning test

After the first playbook run, the Ansible test script will use a PATH-aware command lookup and a lightweight `fd` invocation to prove the command is executable. The second run remains responsible for idempotence verification.

**Alternative considered:** rely solely on package-manager assertions: rejected because package installation alone does not prove the `fd` command name is available.

## Risks / Trade-offs

- [A host already owns `/usr/local/bin/fd`] → Detect the conflict before creating the link and fail with a clear remediation message rather than overwriting it.
- [The package executable path differs from the expected Debian path] → Verify the installed package's binary path in the test environment and encode that path in the managed task.
- [A command check passes but does not run the binary] → Include a minimal non-destructive `fd` invocation in the test.
- [The symlink is created outside package-manager ownership] → Manage it declaratively with Ansible and cover it with the existing second-run idempotence test.
