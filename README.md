# Dotfiles and Provisioning

This repository manages a cross-platform developer environment with a strict split of responsibilities:

- Chezmoi owns user dotfiles, templates, and platform-specific file placement.
- Ansible owns package installation, downloaded binaries, source builds, and system-level setup.

That split is intentional. If a behavior change belongs in a dotfile, change the Chezmoi source tree. Do not patch managed dotfiles from Ansible.

Provisioning pinning boundary: Ansible role inputs own exact versions, immutable source refs, and authoritative artifact checksums for externally sourced tools. APT/YUM packages remain intentionally distribution-managed. Known upstream limitations (such as installer scripts without publisher checksums) are bounded and recorded in [docs/COMPONENT_VERSION_INVENTORY.md](docs/COMPONENT_VERSION_INVENTORY.md); bootstrap downloads happen before provisioning and are not a substitute for those pins.

## Install

Ensure Node.js is already on PATH before running `chezmoi apply` (including `init --apply`): the preservation-aware Pi settings hook requires it. The hook fails visibly rather than discarding existing settings when prerequisites or validation are missing.

### Windows

```powershell
winget install twpayne.chezmoi
chezmoi init --apply --verbose richards-ensonos
```

### Linux

```sh
sudo apt update && sudo apt install --yes curl git unzip
curl -s https://ohmyposh.dev/install.sh | bash -s
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply richards-ensono
```

### Transient environments

```sh
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --one-shot richards-ensono
```

## Validate

```sh
chezmoi diff
cd scripts/ansible && ansible-galaxy install -r requirements.yml && ansible-playbook playbook.yml --syntax-check
```

For broader validation, use the repository tasks and helper scripts:

- `.vscode/test-dotfiles.sh` for Docker-based Chezmoi rendering and doctor checks.
- `.vscode/test-ansible-idempotence.sh` for a two-pass Docker Ansible apply.
- `yamllint .`, `cd scripts/ansible && ansible-lint`, and shell linting for repo scripts.
- [Provisioning regression tests](scripts/ansible/tests/README.md) for offline rollback, immutable-source, and cross-platform Pi/rendering checks.
- `.github/workflows/ci.yml` runs lint/regressions on PRs and schedules the broader two-pass provisioning check.

Install the local validation hook with `pre-commit install` and run `pre-commit run --all-files` before committing. Node.js is required for the Pi settings merge hook and isolated template tests.

## Documentation

- [docs/README.md](docs/README.md) for the documentation index.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the Chezmoi and Ansible boundary, current inventory, and change guardrails.
- [docs/CHEZMOI_VARIABLES.md](docs/CHEZMOI_VARIABLES.md) for the built-in and repo-specific template variables used by this repo.
- [docs/ANSIBLE_ROLE_TEMPLATE.md](docs/ANSIBLE_ROLE_TEMPLATE.md) for the preferred Ansible role structure and idempotence checklist.
- [docs/COMPONENT_VERSION_INVENTORY.md](docs/COMPONENT_VERSION_INVENTORY.md) for externally sourced component versions, integrity metadata, ownership, and bounded exceptions.
- [scripts/ansible/README.md](scripts/ansible/README.md) for play ordering, role categories, and privilege boundaries.

## SSH Push URL

```sh
chezmoi cd
git remote set-url --no-push origin https://github.com/richards-ensono/dotfiles.git
git remote set-url --push origin git@github.com:richards-ensono/dotfiles.git
```
