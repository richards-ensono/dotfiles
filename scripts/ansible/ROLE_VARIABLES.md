# Role Variables

This file documents the current role-variable surface for the Phase 3 cleanup pass.

Conventions intended by this repository:

- `group_vars/all.yml` holds repository-wide provisioning inputs.
- `defaults/main.yml` should hold user-overridable role settings.
- `vars/main.yml` should hold internal constants that are not intended to be overridden casually.

The roles below are the current priority set because they carry versions, install paths, or external download behavior.

## Summary

| Role              | Files                                             | Current strategy                                                        |
|:------------------|:--------------------------------------------------|:------------------------------------------------------------------------|
| `uv`              | `defaults/main.yml`, `vars/main.yml`, `README.md` | Pinned release tarball with checksum                                    |
| `copilot-cli`     | `defaults/main.yml`, `vars/main.yml`, `README.md` | Official installer script, `latest` by default, optional pinned version |
| `antigravity-cli` | `defaults/main.yml`, `README.md`                  | Official installer script, latest only                                  |
| `oh-my-posh`      | `defaults/main.yml`                               | Pinned binary download with partial checksum coverage                   |
| `pwsh`            | `defaults/main.yml`, `vars/main.yml`, `README.md` | Pinned GitHub `.deb` download without checksum                          |
| `gh`              | `defaults/main.yml`, `vars/main.yml`, `README.md` | Pinned source build from Git tag                                        |
| `podman`          | `defaults/main.yml`, `vars/main.yml`, `README.md` | Pinned source build from Git tag                                        |
| `tmux`            | `defaults/main.yml`, `vars/main.yml`, `README.md` | Pinned source release with checksum                                     |
| `nvm`             | `defaults/main.yml`, `README.md`                  | Pinned installer script with checksum                                   |
| `pnpm`            | `defaults/main.yml`, `README.md`                  | Pinned official installer script without checksum                       |
| `dotnet`          | `defaults/main.yml`, `README.md`                  | Channel-based installer script without checksum                         |
| `cargo`           | `defaults/main.yml`, `vars/main.yml`, `README.md` | Latest from crates.io via `cargo install`                               |

## Roles

### `uv`

- Files: `defaults/main.yml`, `vars/main.yml`, `README.md`
- User-overridable variables:
  - `uv_version`: `0.11.14`
  - `uv_platform`: `x86_64-unknown-linux-gnu`
  - `uv_download_url`: GitHub release URL template
  - `uv_checksum`: `sha256:f3b623eb0e6141a7053d571d59a0bdc341e0f238ea8f5f0b4815ddbec9a2a296`
  - `uv_install_dir`: `{{ ansible_env.HOME }}/.local/bin`
- Internal variables:
  - `uv_install_script_url`: `https://astral.sh/uv/install.sh`
- Shared input from `group_vars/all.yml`:
  - `uv_tools`
- Strategy: pinned binary release with checksum validation.
- Current gap: tool-install/update behavior is still only lightly documented and remains a later idempotence-hardening target.

### `copilot-cli`

- Files: `defaults/main.yml`, `vars/main.yml`, `README.md`
- User-overridable variables:
  - `copilot_cli_enabled`: `true`
  - `copilot_cli_version`: `latest`
  - `copilot_cli_install_prefix`: `{{ ansible_env.HOME }}/.local`
- Internal variables:
  - `copilot_cli_install_script_url`: `https://gh.io/copilot-install`
- Strategy: official installer script, latest by default, supports explicit version override.
- Current gap: no checksum validation for the installer script.

### `antigravity-cli`

- Files: `defaults/main.yml`, `README.md`
- User-overridable variables:
  - `antigravity_cli_enabled`: `true`
  - `antigravity_cli_install_prefix`: `{{ ansible_env.HOME }}/.local`
  - `antigravity_cli_install_dir`: `{{ ansible_env.HOME }}/.local/bin`
  - `antigravity_cli_binary_name`: `agy`
  - `antigravity_cli_binary_path`: derived from install dir and binary name
  - `antigravity_cli_install_script_url`: `https://antigravity.google/cli/install.sh`
  - `antigravity_cli_legacy_binary_name`: `gemini`
- Strategy: official installer script with latest behavior and legacy Gemini cleanup.
- Current gap: no explicit version pinning or checksum validation.

### `oh-my-posh`

- Files: `defaults/main.yml`
- User-overridable variables:
  - `oh_my_posh_bin_path`: `/usr/local/bin/oh-my-posh`
  - `oh_my_posh_arch_map`: architecture mapping for downloads
  - `oh_my_posh_version`: `v29.13.1`
  - `oh_my_posh_checksums`: architecture-keyed checksum map
  - `oh_my_posh_arch`: derived from `ansible_architecture`
  - `oh_my_posh_checksum`: derived from the checksum map
  - `oh_my_posh_supported_architectures`: `x86_64`, `aarch64`, `riscv64`
- Strategy: pinned binary download with checksum support.
- Current gap: checksum coverage is incomplete for all supported architectures.

### `pwsh`

- Files: `defaults/main.yml`, `vars/main.yml`
- User-overridable variables:
  - `pwsh_target_version`: `7.6.1`
- Internal variables:
  - `pwsh_arch_map`: `x86_64 -> amd64`, `aarch64 -> arm64`
  - `pwsh_arch`: derived from the architecture map
  - `pwsh_supported_architectures`: `x86_64`, `aarch64`
- Strategy: pinned GitHub `.deb` download plus a Debian 13+ `libicu72` dependency path.
- Current gap: no checksum validation.

### `gh`

- Files: `defaults/main.yml`, `vars/main.yml`, `README.md`
- User-overridable variables:
  - `gh_version`: `v2.92.0`
  - `gh_build_dir`: `/tmp/gh_build`
- Internal variables:
  - `gh_git_repo`: `https://github.com/cli/cli.git`
- Strategy: pinned source build from Git tag.
- Current gap: source-build dependencies and update strategy are still only lightly documented.

### `podman`

- Files: `defaults/main.yml`, `vars/main.yml`, `README.md`
- User-overridable variables:
  - `podman_version`: `v5.8.2`
  - `podman_build_dir`: `/tmp/podman_build`
  - `podman_network_handler`: `pasta`
  - `podman_runtime`: `crun`
- Internal variables:
  - `podman_git_repo`: `https://github.com/containers/podman.git`
  - `podman_package_map`: runtime and network package map
  - `podman_build_tags`: `seccomp apparmor`
  - `podman_user`: derived from `SUDO_USER` or `ansible_user_id`
- Strategy: pinned source build from Git tag plus rootless configuration.
- Current gap: runtime and network choices remain lightly documented compared with the build and rootless setup.

### `tmux`

- Files: `defaults/main.yml`, `vars/main.yml`, `README.md`
- User-overridable variables:
  - `tmux_version`: `3.6a`
  - `tmux_checksum`: `sha256:b6d8d9c76585db8ef5fa00d4931902fa4b8cbe8166f528f44fc403961a3f3759`
- Internal variables:
  - `tmux_src_dir`: `/usr/local/src/tmux`
  - `tmux_install_dir`: `/usr/local`
- Strategy: pinned source release with checksum validation.
- Current gap: source-build dependency and upgrade flow are still lighter than the central Phase 3 notes.

### `nvm`

- Files: `defaults/main.yml`, `README.md`
- User-overridable variables:
  - `nvm_version`: `v0.40.4`
  - `nvm_install_url`: installer URL template
  - `nvm_install_checksum`: `sha256:4b7412c4166905d13ea272117f5c6bf6c674c0074fc4c78d82784f8750b9585d`
- Strategy: pinned installer script with checksum validation.
- Current gap: shell integration still lives outside the role in the Chezmoi-managed shell config.

### `pnpm`

- Files: `defaults/main.yml`, `README.md`
- User-overridable variables:
  - `pnpm_version`: `11.4.0`
  - `pnpm_install_url`: `https://get.pnpm.io/install.sh`
  - `pnpm_home`: `{{ ansible_facts['env'].HOME }}/.local/share/pnpm`
  - `pnpm_global_packages`: package/version specs installed with `pnpm install --global`, default `[]`
- Strategy: pinned official installer script using the current `pnpm@latest` version at the time this role was added; optional global packages from configured package/version specs.
- Current gap: installer script is not checksum-validated.

### `dotnet`

- Files: `defaults/main.yml`, `README.md`
- User-overridable variables:
  - `dotnet_version`: `10.0`
  - `dotnet_sdk_version`: `10.0`
  - `dotnet_install_dir`: `/usr/share/dotnet`
  - `dotnet_install_script_url`: `https://dot.net/v1/dotnet-install.sh`
- Strategy: channel-based installer script, effectively latest within the configured channel.
- Current gap: `dotnet_install_dir` does not match the current user-local installation behavior, and the installer script is not checksum-validated.

### `cargo`

- Files: `defaults/main.yml`, `vars/main.yml`
- User-overridable variables:
  - `cargo_packages`: package list containing `tree-sitter-cli`, `ripgrep`, `fd-find`, `zoxide`, `du-dust`, `procs`, and `gping`
- Internal variables:
  - none today
  - per-package `binary` overrides where the installed command differs from the package name
- Strategy: latest crates.io packages via `cargo install`.
- Current gap: no version pinning, and current install behavior should be hardened for idempotence in a later phase.

## Follow-up targets

The next useful Phase 3 cleanup steps are:

1. Continue moving any remaining user-overridable role settings out of `vars/` where they still behave like public inputs.
2. Standardize the version model per role: checksum-pinned release, pinned source build, or installer-driven latest.
3. Close the known data gaps, especially the incomplete `oh-my-posh` checksum map and the misleading `.NET` install path variable.
