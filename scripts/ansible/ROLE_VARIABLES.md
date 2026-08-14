# Role Variables and Version Boundary

`group_vars/all.yml` contains repository-wide inputs. Role `defaults/main.yml` contains user-overridable values; `vars/main.yml` contains internal constants. The authoritative source/version/integrity record is [../../docs/COMPONENT_VERSION_INVENTORY.md](../../docs/COMPONENT_VERSION_INVENTORY.md).

## Managed role inputs

| Role | Selected input | Verification/source strategy |
|:--|:--|:--|
| `uv` | `0.12.4` | Official GitHub x86_64 GNU tarball, SHA-256 checked |
| `copilot_cli` | `@github/copilot` `1.0.80` | Official npm package; npm registry integrity verification |
| `oh_my_posh` | `v30.6.5` | Official Linux amd64/arm64 assets, architecture SHA-256 checked; riscv64 rejected |
| `pwsh` | `7.6.4` | Official GitHub Debian asset; upstream checksum not available in the verified release metadata |
| `gh` | `v2.97.0` | Official source repository tag |
| `podman` | `v6.1.0` | Official source repository tag; containers/image config uses immutable commit `df7e80d2d19872b61f352a8a182ec934dc0c2346` |
| `tmux` | `3.7b` | Official source archive, SHA-256 checked; invisible-island terminfo remains a documented moving-source exception |
| `nvm` | nvm `v0.40.6`; Node.js LTS `v24.19.0` | Versioned official installer ref plus exact nvm-managed Node/npm paths; nvm installer checksum unavailable |
| `pnpm` | `11.21.0` | Official installer receives exact version; script checksum unavailable |
| `dotnet` | SDK `10.0.400` | Official Microsoft x64/arm64 archives, SHA-512 checked (publisher-format exception) |
| `fzf` | `v0.74.2` | Official Git tag source build |
| `neovim` | `v0.12.4` | Official Git tag source build; plugin refs use immutable commits/lock |

The four developer analysis tools are pinned in `roles/developer_analysis_tools/defaults/main.yml`: govulncheck `v1.7.0`, staticcheck `v0.7.0`, gosec `v2.28.0`, and actionlint `v1.7.12`. Ownership markers preserve idempotence.

Ansible Galaxy inputs are pinned in `requirements.yml`: `geerlingguy.go` `1.1.0`, `hurricanehrndz.rustup` `v1.0.0`, `ansible.posix` `2.2.2`, and `community.general` `13.3.0`.

## Boundary and exceptions

- APT/YUM-owned packages remain intentionally unpinned. Their effective versions are selected by the target distribution repositories; this role set does not introduce unsupported OS snapshot pins.
- Antigravity CLI is not an active role in this checkout. If its documented upstream installer (`https://antigravity.google/cli/install.sh`) is enabled by a downstream configuration, it has no repository-published stable version or checksum and must remain an explicitly documented installer exception.
- Cargo packages (`tree-sitter-cli`, `ripgrep`, `fd-find`, `zoxide`, `du-dust`, `procs`, and `gping`) are not active role inputs in this checkout. Any downstream cargo installation must provide exact crates.io versions; crates.io package integrity is manager-owned rather than a repository artifact checksum.
- SpecKit is not made reproducible by a moving Git URL. The current role remains an upstream limitation (`uv tool install specify-cli --from git+https://github.com/github/spec-kit.git`) and should be treated as an exception until a publisher version/ref is available; no commit or checksum is invented here.
- Direct downloads are checked with authoritative upstream hashes where supplied. Missing PowerShell, pnpm, nvm, and tmux-term-info hashes are recorded exceptions, not silently treated as verified.
