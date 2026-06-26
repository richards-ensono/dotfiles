# Ansible Layout

This directory provisions the Linux and WSL environment. It does not own dotfiles.

If a change belongs in `.bashrc`, `.zshrc`, Neovim config, or PowerShell profile content, make that change in the Chezmoi source tree instead of patching the rendered file from Ansible.

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
5. Run user roles without privilege escalation.
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

- `rootless-networking`
- `nvm`
- `pnpm`
- `bun`
- `hurricanehrndz.rustup`
- `cargo`
- `uv`
- `speckit`
- `dotnet`
- `copilot-cli`
- `antigravity-cli`
- `container-cleanup`

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

See `ROLE_VARIABLES.md` for the current role-variable inventory and version strategy notes for the Phase 3 cleanup targets.

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
