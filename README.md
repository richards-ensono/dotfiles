# Dotfiles and Provisioning

This repository manages a cross-platform developer environment with a strict split of responsibilities:

- Chezmoi owns user dotfiles, templates, and platform-specific file placement.
- Ansible owns package installation, downloaded binaries, source builds, and system-level setup.

That split is intentional. If a behavior change belongs in a dotfile, change the Chezmoi source tree. Do not patch managed dotfiles from Ansible.

## Install

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
- `yamllint .`, `ansible-lint playbook.yml`, and shell linting for repo scripts.

## Documentation

- [docs/README.md](docs/README.md) for the documentation index.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the Chezmoi and Ansible boundary, current inventory, and change guardrails.
- [docs/CHEZMOI_VARIABLES.md](docs/CHEZMOI_VARIABLES.md) for the built-in and repo-specific template variables used by this repo.
- [docs/ANSIBLE_ROLE_TEMPLATE.md](docs/ANSIBLE_ROLE_TEMPLATE.md) for the preferred Ansible role structure and idempotence checklist.
- [scripts/ansible/README.md](scripts/ansible/README.md) for play ordering, role categories, and privilege boundaries.

## SSH Push URL

```sh
chezmoi cd
git remote set-url --no-push origin https://github.com/richards-ensono/dotfiles.git
git remote set-url --push origin git@github.com:richards-ensono/dotfiles.git
```
