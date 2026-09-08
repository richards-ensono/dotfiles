# Component Version and Integrity Inventory

This is the review boundary for externally sourced provisioning inputs. Role variables remain the operational configuration; this document records their publisher, selected version/ref, asset, and verification method. Versions are point-in-time selections from the approved `update-pin-verified-component-versions` change.

## Versioned managed components

| Component | Publisher/source and selected version | Asset or package | Integrity |
|:--|:--|:--|:--|
| uv | Astral, GitHub release `0.12.9` | `uv-x86_64-unknown-linux-gnu.tar.gz` | Publisher `sha256.sum`, locally verified SHA-256 `ec7a99cd05e0cd7f80243f135ce1361c76835cb0ee60055d14d20eba8eba1460` |
| Oh My Posh | Jan De Dobbeleer, GitHub release `v31.1.2` | `posh-linux-amd64` / `posh-linux-arm64` | Publisher `checksums.txt`, locally verified SHA-256 amd64 `f691e8913cf5abaf941a2f73da4e5df3ceb0d99e979451ae1734347b775d843e`; arm64 `f89022231e1d031f46a5f8e6254bee1dd871c328432c4f9d3a05c823fe1d26a1`; riscv64 explicitly unsupported |
| .NET SDK | Microsoft official builds, `10.0.400` | versioned Linux x64/arm64 tarballs | SHA-512 x64 `1033977dd837150e0814cf0c5d5b17ceb63925fda7ba2158b47258a4bd7c048cf82eac3bc1166f3146f53124a3f5fba09db1de1260d2ce96399860303b404b48`; arm64 `a1b45da58e5591fff909a6126ac6bfc1ef9c12bc72c0625f7815e83a82be1a902317ee96926cbbf81324a45c6abf2ed8102a216d0507879cc166159af78d1b77` |
| Node.js | Official Node.js release index, current non-prerelease LTS `v24.20.0` (`Krypton`) | nvm-managed Node.js/npm runtime | `SHASUMS256.txt` locally verified the Linux x64 archive: SHA-256 `2f2c0da162318f0de47665410c7c8c2ed3d36c8f3105de4bbc61176c70a7cbf2`; dependent tasks use the exact `~/.nvm/versions/node/v24.20.0/bin/npm` path rather than OS Node/npm |
| GitHub Copilot CLI | Official npm registry, `@github/copilot@1.0.82` | npm package tarball | Invokes the nvm-managed npm executable; npm verifies registry `dist.integrity` (`sha512-+mDIwBO3dCpL3k2rVLc4+1tFzqcVBTJNA/0co+okEpmCgcHjaz91Cqq7++pJKN5yJQuGC6bKangm7PSoheI1Xw==`); the package declares no Node engine restriction and is compatible with selected Node 24 LTS |
| GitHub CLI | `cli/cli` release `v2.100.0`, resolved to `45437bc7eeeb3359bbfddd1742f79de7652fd3e2` | source build | Git-source exception: official lightweight tag resolves to the configured immutable commit; build dependencies/modules remain publisher/package-manager owned |
| Podman | `containers/podman` source tag `v6.1.1` | source build | Git tag; `containers/image` policy and registries files use immutable commit `08ce6b4207e7b151ea1c2830cdb1d4473cfd12aa`; Netavark and Aardvark-DNS `2.1.0` Linux x64 assets have configured SHA-256 values |
| PowerShell | Microsoft, GitHub release `v7.6.4` | Debian amd64/arm64 package | Exact release URL; no authoritative checksum was supplied by the verified publisher metadata, so the role records a bounded TLS/source exception |
| tmux | upstream GitHub release `3.7c` | `tmux-3.7c.tar.gz` source tarball | GitHub release-asset SHA-256, locally verified: `7c60cae9a0e25288e2e24750aafc9e8800fc7fd4555e447e1b29ee4201cfb3bf` |
| nvm | `nvm-sh/nvm` Git ref `v0.40.6` | `install.sh` at the versioned ref; installs Node.js LTS `v24.19.0` | Upstream does not publish an authoritative installer checksum; TLS plus immutable ref is the documented exception. The role asserts the exact nvm-managed Node.js and npm executables before dependent roles run |
| pnpm | npm registry, stable `12.3.4` | official installer with `PNPM_VERSION=12.3.4` via `https://get.pnpm.io/install.sh` | Registry selection evidence: exact package metadata provides `dist.integrity` `sha512-lhqkH7B32joEpEHZ+OFevAyW2o73ELLrZ7+e58sGEOq9SPH9hfUc/+c4RnhfoPh8VqOocqHYk/hEZ0G1zORUVw==`; installer exception: this endpoint has no independently published authoritative script checksum, so its content cannot meet the normal checksum gate. A maintainer-approved exception retains official HTTPS, an exact `PNPM_VERSION`, and installed-version verification as compensating controls; these do not establish installer-content integrity. Revisit when pnpm publishes an authoritative checksum or the role moves to a checksum-backed distribution. |
| fzf | `junegunn/fzf` Git tag `v0.74.3`, resolved to `15f64c492a08f0840b81540c7d1de35737448086` | source build | Git-source exception: official annotated tag resolves to the configured immutable commit |
| Neovim | `neovim/neovim` Git tag `v0.12.5`, resolved to `5885a30e1e1225349079e7a1c4a3848aa8e43e42` | source build | Git-source exception: official annotated tag resolves to the configured immutable commit |

## Package/module and configuration sources

- Go runtime is owned by `geerlingguy.go` `1.1.0` with the existing repository Go version/checksum inputs. The five analysis tools use exact modules: `golang.org/x/vuln/cmd/govulncheck@v1.7.0`, `honnef.co/go/tools/cmd/staticcheck@v0.7.0`, `github.com/securego/gosec/v2/cmd/gosec@v2.28.0`, `github.com/rhysd/actionlint/cmd/actionlint@v1.7.12`, and `github.com/google/osv-scanner/v2/cmd/osv-scanner@v2.5.1`. Ownership markers make reruns idempotent.
- Galaxy is pinned to `hurricanehrndz.rustup` `v1.0.0`, `ansible.posix` `2.2.2`, and `community.general` `13.3.0` in addition to `geerlingguy.go`.
- Neovim's LazyVim lock is the immutable plugin inventory. Explicit plugin declarations are pinned to commits, including Telescope (`a0bbec21143c7bc5f8bb02e0005fa0b982edc026`), Treesitter (`65a266bf693d3fc856dd341c25edea1a0917a30f`), CopilotChat (`451d365928a994cda3505a84905303f790e28df8`), and copilot.vim (`a12fd5672110c8aa7e3c8419e28c96943ca179be`). Lazy.nvim bootstrap is detached at `85c7ff3711b730b4030d03144f6db6375044ae82`.
- SpecKit is an upstream exception: the role's `uv tool install specify-cli --from git+https://github.com/github/spec-kit.git` has no publisher version/ref in the current mechanism. It is not presented as reproducible and no checksum is fabricated.
- Antigravity CLI is not an active role in this checkout. Its known upstream installer (`https://antigravity.google/cli/install.sh`) has no selected stable version or publisher checksum; downstream enablement must retain that explicit exception.
- Cargo packages (`tree-sitter-cli`, `ripgrep`, `fd-find`, `zoxide`, `du-dust`, `procs`, `gping`) are not active role inputs here. Downstream use must specify exact crates.io versions; crates.io checksum/integrity is package-manager owned.

## Repository-wide pin review coverage

The provisioning table above is not the whole review boundary. The version-maintenance skill must also review these tracked pins and their coupled integrity controls:

- CI pins: GitHub Actions, Python, `pre-commit`, Ansible, Ansible Lint, and the checksum-verified Chezmoi Debian package in `.github/workflows/ci.yml`.
- Pre-commit hook revisions in `.pre-commit-config.yaml`.
- The BusyBox OCI digest used by `scripts/ansible/tests/podman-compose-network.yml`.
- Lazy.nvim's bootstrap commit, five explicit Neovim plugin commits, and all 40 plugin commits in `.chezmoitemplates/nvim/lazy-lock.json`. The lockfile is an immutable Git-commit inventory, not a direct-download checksum manifest.
- Version-looking values that do *not* select external component content—such as Oh My Posh theme schema versions and Ansible platform compatibility ranges—are excluded from release maintenance.

The 2026-09 structural review corrected this inventory's stale Podman tag (`v6.1.0` to the configured `v6.1.1`) and `containers/image` commit. It identified no untracked package-manager manifest (such as `package.json`, `Cargo.toml`, `go.mod`, or Python dependency manifest) at the repository root. A future release review must query authoritative upstream sources at execution time; this document is an inventory, not evidence that a release is still current.

## Ownership and bounded exceptions

- Packages installed through configured APT/YUM repositories are intentionally distribution-managed. Their effective versions vary with the target OS repository; this change does not add unsupported package version pins.
- The `packages_unlisted_packages` Dive `.deb` remains an externally versioned URL (`v0.13.1`) without a verified publisher checksum and is a documented exception in `group_vars/all.yml`; it is not silently considered hash-verified.
- The bootstrap commands in the repository's user documentation and test helpers necessarily fetch Chezmoi/bootstrap scripts before Ansible can run. They are transport/bootstrap exceptions, not substitutes for the pinned Ansible component boundary. Release provisioning itself must use the role pins above.
- tmux's styled `tmux-256color` fallback obtains `terminfo.src.gz` from the upstream `current` endpoint only when the local entry is missing. The endpoint has no version/checksum mechanism in the current role and is retained as a bounded compatibility exception.
- Source builds are pinned by Git tag/ref rather than release-archive checksum. Direct downloaded executable/archive assets use `get_url` checksums whenever the publisher supplies an authoritative value. SHA-512 for .NET is an upstream-format exception to the preferred SHA-256 policy.
