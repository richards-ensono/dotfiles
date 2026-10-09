# Component Version and Integrity Inventory

This is the review boundary for externally sourced provisioning inputs. Role variables remain the operational configuration; this document records their publisher, selected version/ref, asset, and verification method. Versions are point-in-time selections from the approved `update-pin-verified-component-versions` change.

## Versioned managed components

| Component | Publisher/source and selected version | Asset or package | Integrity |
|:--|:--|:--|:--|
| uv | Astral, GitHub release `0.12.4` | `uv-x86_64-unknown-linux-gnu.tar.gz` | SHA-256 `c8c60f47e6f88d18dbf6f33d7279fb1fbf7ae76631768152cf5578c3d65729b4` |
| Oh My Posh | Jan De Dobbeleer, GitHub release `v30.6.5` | `posh-linux-amd64` / `posh-linux-arm64` | SHA-256 amd64 `079febf68932744a6c8d05179a2798bca083613275eca6de41b1efe9c82e15c8`; arm64 `34d81d2871cd2b211878d3e31bb7c8d7c5e70088170ee526be222a2e6b843c4d`; riscv64 explicitly unsupported |
| .NET SDK | Microsoft official builds, `10.0.400` | versioned Linux x64/arm64 tarballs | SHA-512 x64 `1033977dd837150e0814cf0c5d5b17ceb63925fda7ba2158b47258a4bd7c048cf82eac3bc1166f3146f53124a3f5fba09db1de1260d2ce96399860303b404b48`; arm64 `a1b45da58e5591fff909a6126ac6bfc1ef9c12bc72c0625f7815e83a82be1a902317ee96926cbbf81324a45c6abf2ed8102a216d0507879cc166159af78d1b77` |
| Node.js | Official Node.js release index, current non-prerelease LTS `v24.19.0` (`Krypton`) | nvm-managed Node.js/npm runtime | Installed by the nvm role from the official release selected at `https://nodejs.org/dist/index.json`; dependent tasks use the exact `~/.nvm/versions/node/v24.19.0/bin/npm` path rather than OS Node/npm |
| GitHub Copilot CLI | Official npm registry, `@github/copilot@1.0.80` | npm package tarball | Invokes the nvm-managed npm executable; npm verifies registry `dist.integrity` (`sha512-6tf93ZF56KOiTTAjK/UhLZkl1W543IzaTQly288kockJZFswpRTnQEI00Yvacpb39DTvTYu3/ha9SeKpo/pgZQ==`); package-manager behavior is intentional |
| GitHub CLI | `cli/cli` source tag `v2.97.0` | source build | Git tag; build dependencies/modules remain publisher/package-manager owned |
| Podman | `containers/podman` source tag `v6.1.0` | source build | Checkout verified against full commit `cade97a52ebdf9dbf9e81de8009015776837a074`; `containers/image` policy and registries files use immutable commit `df7e80d2d19872b61f352a8a182ec934dc0c2346` |
| PowerShell | Microsoft, GitHub release `v7.6.4` | Debian amd64/arm64 package | Exact release URL; no authoritative checksum was supplied by the verified publisher metadata, so the role records a bounded TLS/source exception |
| tmux | upstream release `3.7b` | source tarball | SHA-256 `87f2e99e3b685973f2ca002ffd6ed7e51a5744f7009daae5a15670b6d532db96` |
| nvm | `nvm-sh/nvm` Git ref `v0.40.6` | `install.sh` at the versioned ref; installs Node.js LTS `v24.19.0` | Upstream does not publish an authoritative installer checksum; TLS plus immutable ref is the documented exception. The role asserts the exact nvm-managed Node.js and npm executables before dependent roles run |
| pnpm | official installer with `PNPM_VERSION=11.21.0` | `https://get.pnpm.io/install.sh` | Installer endpoint has no independently published authoritative checksum; exact resulting version plus TLS is the documented exception |
| fzf | `junegunn/fzf` Git tag `v0.74.2` | source build | Immutable Git tag |
| Neovim | `neovim/neovim` Git tag `v0.12.4` | source build | Checkout verified against full commit `68ea43cd0c28af25cd47731308c94fedfcfd1b0b` |

## CI-only validation inputs

These inputs do not change provisioned component versions. Action commits were resolved from their current stable GitHub releases; Python tool versions were checked against PyPI and tested with Python 3.13.

- `actions/checkout` v7.0.1: `3d3c42e5aac5ba805825da76410c181273ba90b1`.
- `actions/setup-python` v7.0.0: `5fda3b95a4ea91299a34e894583c3862153e4b97`.
- `actions/setup-node` v7.1.0: `949feb2413d6458794dcd2491c4babbbce0c15c1`.
- Validation tools: ansible-core 2.21.5, ansible-lint 26.9.0, yamllint 1.38.0, pre-commit 4.6.2; ShellCheck remains distribution-managed.
- Chezmoi v2.73.0: release metadata SHA-256 `b597729b687af4488a848240134cb633de8ca0f04e0d26d48f400ee2ac338ffa` for the Linux amd64 tarball; `266938399108028a5b6dc7a137026e3ead747304122e5fe381d5396e496620f6` for the Windows amd64 ZIP.
- The existing scheduled/manual integration image remains `debian:bookworm`, intentionally distribution-managed rather than claimed to be immutable. Galaxy/component provisioning pins remain unchanged.

## Package/module and configuration sources

- Go runtime is owned by `geerlingguy.go` `1.1.0` with the existing repository Go version/checksum inputs. The four analysis tools use exact modules: `golang.org/x/vuln/cmd/govulncheck@v1.7.0`, `honnef.co/go/tools/cmd/staticcheck@v0.7.0`, `github.com/securego/gosec/v2/cmd/gosec@v2.28.0`, and `github.com/rhysd/actionlint/cmd/actionlint@v1.7.12`. Ownership markers make reruns idempotent.
- Galaxy is pinned to `hurricanehrndz.rustup` `v1.0.0`, `ansible.posix` `2.2.2`, and `community.general` `13.3.0` in addition to `geerlingguy.go`.
- Neovim's LazyVim lock is the immutable plugin inventory. Explicit plugin declarations are pinned to commits, including Telescope (`a0bbec21143c7bc5f8bb02e0005fa0b982edc026`), Treesitter (`65a266bf693d3fc856dd341c25edea1a0917a30f`), CopilotChat (`451d365928a994cda3505a84905303f790e28df8`), and copilot.vim (`a12fd5672110c8aa7e3c8419e28c96943ca179be`). Lazy.nvim bootstrap is detached at `85c7ff3711b730b4030d03144f6db6375044ae82`.
- SpecKit is an upstream exception: the role's `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git` has no publisher version/ref in the current mechanism. It is not presented as reproducible and no checksum is fabricated.
- Antigravity CLI is not an active role in this checkout. Its known upstream installer (`https://antigravity.google/cli/install.sh`) has no selected stable version or publisher checksum; downstream enablement must retain that explicit exception.
- Cargo packages (`tree-sitter-cli`, `ripgrep`, `fd-find`, `zoxide`, `du-dust`, `procs`, `gping`) are not active role inputs here. Downstream use must specify exact crates.io versions; crates.io checksum/integrity is package-manager owned.

## Ownership and bounded exceptions

- Packages installed through configured APT/YUM repositories are intentionally distribution-managed. Their effective versions vary with the target OS repository; this change does not add unsupported package version pins.
- The `packages_unlisted_packages` Dive `.deb` remains an externally versioned URL (`v0.13.1`) without a verified publisher checksum and is a documented exception in `group_vars/all.yml`; it is not silently considered hash-verified.
- The bootstrap commands in the repository's user documentation and test helpers necessarily fetch Chezmoi/bootstrap scripts before Ansible can run. They are transport/bootstrap exceptions, not substitutes for the pinned Ansible component boundary. Release provisioning itself must use the role pins above.
- tmux's styled `tmux-256color` fallback obtains `terminfo.src.gz` from the upstream `current` endpoint only when the local entry is missing. The endpoint has no version/checksum mechanism in the current role and is retained as a bounded compatibility exception.
- Source builds are pinned by Git tag/ref rather than release-archive checksum. Direct downloaded executable/archive assets use `get_url` checksums whenever the publisher supplies an authoritative value. SHA-512 for .NET is an upstream-format exception to the preferred SHA-256 policy.
