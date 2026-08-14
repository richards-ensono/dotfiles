# Ansible Layout

This directory provisions the Linux and WSL environment. It does not own dotfiles.

If a change belongs in `.bashrc`, `.zshrc`, Neovim config, or PowerShell profile content, make that change in the Chezmoi source tree instead of patching the rendered file from Ansible.

Externally sourced role inputs are pinned to exact versions or immutable refs and use publisher checksums where available. APT/YUM package versions remain owned by the target distribution. See [../../docs/COMPONENT_VERSION_INVENTORY.md](../../docs/COMPONENT_VERSION_INVENTORY.md) for the complete boundary and documented upstream exceptions.

## Entry points

- `playbook.yml` is the main orchestration file.
- `requirements.yml` pins external Galaxy roles and collections.
- `inventory/hosts.yml` defines a local `localhost` target with `/usr/bin/python3`.
- `private_executable_exec.sh` bootstraps Ansible installation, installs Galaxy requirements, and runs the playbook.
- `roles/preflight/` fails early when the host is outside the supported OS/package-manager/command baseline.

## Play ordering

The current playbook runs in a simple sequence:

1. Debug host facts.
2. Run preflight checks for supported OS family, package manager, essential commands, and build disk space.
3. Update the base Debian or Ubuntu system with a recovery block.
4. Run system roles with `become: true`.
5. Run user roles without privilege escalation; `nvm` installs and verifies the pinned Node.js LTS/npm runtime before `copilot-cli` invokes its nvm-managed npm path.
6. Sync LazyVim plugins if Neovim is present.
7. Run final user cleanup roles.

## Role categories

System setup roles:

- `packages`
- `bat`
- `fzf`
- `geerlingguy.go`
- `gh`
- `neovim`
- `oh-my-posh`
- `pwsh`
- `tmux`
- `zsh`
- `wsl`
- `podman`

User setup roles:

- `rootless_networking`
- `nvm`
- `pnpm`
- `bun`
- `hurricanehrndz.rustup`
- `cargo`
- `uv`
- `speckit`
- `dotnet`
- `copilot_cli`
- `antigravity-cli`
- `container_cleanup`

## Privilege boundaries

- Package manager operations, system package installs, and machine-wide tooling happen in `become: true` plays.
- User-local tools and per-user runtime setup happen without `become`.
- Keep those boundaries clear when adding roles or moving tasks.

## External dependencies

Pinned Galaxy roles and collections currently include:

- `geerlingguy.go`
- `hurricanehrndz.rustup`
- `ansible.posix`
- `community.general`

## Variable guidance

Repository-wide provisioning inputs now live in `group_vars/all.yml`, including package lists, Go settings, and `uv_tools`. Keep role-specific defaults in `defaults/main.yml`.

See `ROLE_VARIABLES.md` for the current role-variable inventory. The maintained source/version/integrity record is `../../docs/COMPONENT_VERSION_INVENTORY.md`.

When extending the current layout:

- keep shared provisioning inputs centralized instead of duplicating them across roles,
- prefer `defaults/main.yml` for user-overridable role values,
- keep internal constants in `vars/main.yml` only when they should not be overridden.

## Validation

Use the narrowest check that matches your change:

```sh
cd scripts/ansible
ansible-galaxy install -r requirements.yml
ansible-playbook playbook.yml --syntax-check
```

For broader verification, run the repository Docker test tasks for syntax and full apply.

## Role conventions

See `../../docs/ANSIBLE_ROLE_TEMPLATE.md` for the preferred role shape, version-check flow, architecture mapping pattern, and build-from-source checklist introduced during the hardening pass.
