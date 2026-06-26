# Ansible Role Template

This document captures the preferred structure for repository-local Ansible roles.

## Directory shape

Use this layout for new roles unless the role is intentionally trivial:

```text
roles/<role>/
  defaults/main.yml
  vars/main.yml
  tasks/main.yml
  meta/main.yml
  README.md
```

- `defaults/main.yml`: user-overridable inputs such as versions, install roots, update flags, supported architectures, and toggles.
- `vars/main.yml`: internal constants that should not normally be overridden.
- `tasks/main.yml`: the role logic, ordered as checks, install/update, verify, and cleanup.
- `meta/main.yml`: supported platforms and high-level role metadata.
- `README.md`: role purpose, public variables, version strategy, and caveats.

## Task flow

Prefer this execution order inside `tasks/main.yml`:

1. Validate architecture or platform assumptions.
2. Probe the current installation state with `changed_when: false` and `failed_when: false` where missing commands are expected.
3. Decide whether install or update work is required.
4. Install or update only when the probe says it is needed.
5. Verify the final installed version or binary path.
6. Clean up temporary artifacts.

## Idempotence rules

- Prefer Ansible-native probes over shelling out to `grep`.
- Use `failed_when: false` for expected check failures instead of broad `ignore_errors: true`.
- Treat rolling `latest` channels as install-if-missing unless an explicit update flag is set.
- Use `creates`, version checks, or list commands before install steps so repeat runs stay quiet.
- Keep `changed_when` tied to a real install or update event.

## Architecture mapping pattern

Roles that download architecture-specific artifacts should expose a small, documented mapping in `defaults/main.yml`:

```yaml
tool_supported_architectures:
  - x86_64
  - aarch64

tool_arch_map:
  x86_64: amd64
  aarch64: arm64

tool_arch: "{{ tool_arch_map[ansible_architecture] }}"
```

Use a matching assertion in `tasks/main.yml` before download steps so unsupported hosts fail clearly.

## Build-from-source pattern

Roles that compile software from source, such as `neovim`, `tmux`, `gh`, `podman`, and `fzf`, should follow the same broad shape:

1. Install build dependencies first.
2. Create or reuse a stable build directory.
3. Clone or update the source at an explicit tag or version.
4. Clean stale build outputs only when the source state changed or a retry is needed.
5. Build with an explicit shell and documented environment variables.
6. Install with `become: true` only when the target path is system-wide.
7. Verify the resulting binary version.

## Preflight expectations

If a role assumes Debian-family packaging, available disk space, or essential tools such as `git`, `curl`, or `python3`, keep those assumptions aligned with the shared `preflight` role instead of re-encoding them inconsistently across roles.
