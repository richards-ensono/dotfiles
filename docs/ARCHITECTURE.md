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

### Pi settings ownership

`run_after_merge-pi-settings.js.tmpl` merges `.chezmoitemplates/pi/settings.json` into the explicit Chezmoi destination. Node.js must be available before applying the hook. The fragment owns its top-level keys and merges `subagents` one level deep; theme, changelog state and other unowned preferences remain local. The former `dot_pi/agent/settings.json` is no longer whole-file managed. AGENTS instructions and skills remain managed normally.

Invalid JSON, non-object settings, symlink destinations and detected concurrent edits fail without replacing existing settings. Writes use an exclusive mode-0600 temporary file and atomic rename. The hook never reads or writes Pi authentication files.

### Recoverable installations

.NET stages its verified SDK directory on the destination filesystem, retaining existing user-installed tools and side-by-side SDK state before overlaying the downloaded SDK. Neovim stages the complete `make install` output and replaces its binary and runtime as a recovery unit, retaining ancillary manuals. Podman stages its complete installation payload (including rootlessport/Quadlet where produced) and independently validates downloaded JSON/TOML configuration before replacement. Existing distro-owned networking helpers are retained.

The internal `scripts/ansible/tasks/activate-staged.yml` transaction preserves destinations as `.ansible-backup`, refuses pre-existing recovery paths, verifies activated output and restores successfully preserved files on failure. Cleanup of backups happens only after verification. If recovery itself fails, do not delete backup paths: they may be the only surviving installation. This is recoverable activation, not a filesystem-wide atomic swap across multiple files; avoid concurrent provisioning or using affected programs during replacement.

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

- `rootless_networking`
- `nvm`
- `bun`
- `hurricanehrndz.rustup`
- `cargo`
- `uv`
- `speckit`
- `dotnet`
- `copilot_cli`
- `antigravity-cli`
- `container_cleanup`

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
- `cd scripts/ansible && ansible-lint` with the production profile in `.ansible-lint.yml`, including dynamically included task fragments
- repo `yamllint`
- shell linting for the shared shell files and helper scripts

These checks should be run after architecture or provisioning changes before broader refactors are attempted. The GitHub workflow runs static validation, offline installer regressions, and isolated Chezmoi/Pi checks on Linux and Windows. Full provisioning idempotence is scheduled/manual. See [provisioning regression tests](../scripts/ansible/tests/README.md) for commands and integration limitations. Repository-only workflow, specification and test files are excluded from Chezmoi deployment.

The public `developer_analysis_tools` inventory input intentionally retains its established name, with a narrow documented role-prefix lint exception. Internal cleanup/networking/tool-install registers use role-prefixed names.

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
