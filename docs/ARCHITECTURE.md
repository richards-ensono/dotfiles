# Architecture

## Core split

This repository keeps two separate responsibilities:

- Chezmoi is the source of truth for user-facing dotfiles, templates, secrets, and platform-specific file placement.
- Ansible provisions packages, binaries, source builds, services, and system-level configuration.

The main guardrail is simple: Ansible must not patch files that are managed by Chezmoi in the home directory. If a shell, editor, prompt, or PowerShell behavior needs to change, edit the Chezmoi source file or template instead.

## Current inventory

### Chezmoi source layout

- `dot_*` files map to POSIX dotfiles such as `~/.bashrc`, `~/.profile`, and `~/.zshrc`.
- `dot_config/` holds XDG-style config content for Linux and cross-platform tools.
- `AppData/` holds Windows-specific sources.
- `dot_local/` holds user-local binaries and bundled assets.
- `private_*` holds private managed content.
- `readonly_*` is currently preserved as a managed reference surface and is not cleaned up automatically.
  Today that includes PowerShell and icon-related Windows-facing paths that are kept for compatibility and reference rather than as the canonical Linux source of truth.
- `.chezmoitemplates/` contains canonical shared templates that delegate paths reuse.

### Template delegation

- `dot_config/nvim/init.lua.tmpl` and `AppData/Local/nvim/init.lua.tmpl` both delegate to `.chezmoitemplates/nvim/init.lua`.
- `dot_config/powershell/Microsoft.PowerShell_profile.ps1.tmpl` and `readonly_Documents/PowerShell/Microsoft.PowerShell_profile.ps1.tmpl` both delegate to `.chezmoitemplates/pwsh/Microsoft.PowerShell_profile.ps1`.
- Small, path-specific templates can stay inline. Shared large configs should continue to be centralized under `.chezmoitemplates/`.

### Shell startup ownership

- `dot_profile` sources `dot_bashrc` for bash login shells and otherwise sources `dot_config/shell_common`.
- `dot_bashrc` sources `dot_config/shell_common`.
- `dot_zshrc` sources `dot_config/shell_common`, then `dot_config/zsh_aliases`, then `dot_config/windows_aliases`.
- `dot_config/zsh_aliases` also sources `dot_config/windows_aliases` today, so there is duplicate sourcing. That should be documented and resolved deliberately in a later change, not implicitly.
- `dot_zshrc` currently runs `chezmoi update` and `chezmoi apply` automatically when `~/.local/chezmoi` exists. That behavior is preserved until explicitly changed.

### Platform filtering and assumptions

`.chezmoiignore` currently drives platform-aware rendering using Chezmoi built-ins:

- `.chezmoi.os` distinguishes Linux from Windows.
- `.chezmoi.kernel.osrelease` is used to detect WSL by checking for `microsoft`.
- `.chezmoi.osRelease.id` is used to gate Debian and Ubuntu-specific scripts.

The current assumption is:

- Windows-specific sources live under `AppData/` and Windows-facing readonly paths.
- Linux user config lives under `dot_*`, `dot_config/`, and `dot_local/`.
- WSL-specific helper symlinks under `dot_local/bin/` only apply on Linux when the kernel release indicates WSL.

### WSL helper shims

The files under `dot_local/bin/` named `symlink_gpg`, `symlink_ssh`, `symlink_ssh-add`, and `symlink_scp` are deliberate Windows-interop shims for WSL environments.

- `symlink_gpg` targets `/mnt/c/Program Files/GnuPG/bin/gpg.exe`.
- `symlink_ssh`, `symlink_ssh-add`, and `symlink_scp` target the Windows OpenSSH binaries under `/mnt/c/Windows/System32/OpenSSH/`.

These are preserved because they provide Windows credential and agent interop from Linux shells. Any future cleanup should first confirm that Windows OpenSSH and GnuPG bridging is no longer needed.

### Ansible play sequence

The current playbook in `scripts/ansible/playbook.yml` runs in this order:

1. Debugging facts.
2. Shared preflight checks for supported OS family, package manager, required commands, and disk space.
3. System update and recovery block with `become: true`.
4. System roles with `become: true`.
5. User roles without `become`.
6. A best-effort LazyVim sync.
7. Final user cleanup roles.

### Current role categories

System roles:

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

User roles:

- `rootless-networking`
- `nvm`
- `bun`
- `hurricanehrndz.rustup`
- `cargo`
- `uv`
- `speckit`
- `dotnet`
- `copilot-cli`
- `antigravity-cli`
- `container-cleanup`

### External dependencies

The repository currently relies on these Galaxy roles and collections:

- Role `geerlingguy.go`
- Role `hurricanehrndz.rustup`
- Collection `ansible.posix`
- Collection `community.general`

## Validation gates

The lowest-cost checks already available in the repository are:

- `chezmoi diff`
- `chezmoi doctor`
- the Docker dry run at `.vscode/test-dotfiles.sh`
- the Docker Ansible idempotence run at `.vscode/test-ansible-idempotence.sh`
- `cd scripts/ansible && ansible-galaxy install -r requirements.yml && ansible-playbook playbook.yml --syntax-check`
- `ansible-lint playbook.yml` with the repository baseline in `.ansible-lint.yml`
- repo `yamllint`
- shell linting for the shared shell files and helper scripts

These checks should be run after architecture or provisioning changes before broader refactors are attempted.

## Confirmation items intentionally deferred

These areas are preserved as-is until explicitly confirmed:

- Whether `readonly_Documents/` and `readonly_Pictures/` are intentional long-term reference paths or eventual cleanup targets.
- Whether `dot_zshrc` should keep automatically running `chezmoi update` and `chezmoi apply`.
- Whether the WSL helper shims under `dot_local/bin/` should remain the preferred Windows OpenSSH and GnuPG bridge.
- Whether `dot_config/windows_aliases.tmpl` should keep hard-coded Windows user path probes or move to a data-driven candidate list.

## Change checklist

Use this before making follow-up changes:

1. Edit Chezmoi source files for dotfile behavior.
2. Edit Ansible roles, defaults, vars, or playbook data for provisioning behavior.
3. Do not use Ansible to mutate files that Chezmoi manages.
4. Prefer shared templates in `.chezmoitemplates/` when the same config is rendered to multiple destinations.
5. Run the narrowest relevant validation command after each change.
6. Do not create unsigned commits.
