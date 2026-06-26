# Documentation Index

Use the top-level `README.md` for install and quick-start guidance. This directory collects the longer-lived architecture and implementation references.

## Core docs

- [../README.md](../README.md) for installation and validation entry points.
- [ARCHITECTURE.md](ARCHITECTURE.md) for the Chezmoi and Ansible ownership boundary, current inventory, and change guardrails.
- [CHEZMOI_VARIABLES.md](CHEZMOI_VARIABLES.md) for built-in template facts and repo data keys.
- [ANSIBLE_ROLE_TEMPLATE.md](ANSIBLE_ROLE_TEMPLATE.md) for the preferred Ansible role structure, idempotence notes, and source-build pattern.
- [../scripts/ansible/README.md](../scripts/ansible/README.md) for play ordering, role categories, and privilege boundaries.

## Plans

- `plans/` contains implementation plans and staged follow-up work.

## Current state

The architecture hardening pass has documented the current Chezmoi and Ansible split, added a shared Ansible preflight role, and expanded validation with stricter Chezmoi Docker checks, a Docker idempotence script, repo YAML linting, and a documented `ansible-lint` baseline.

The remaining optional cleanup items are intentionally documented rather than auto-applied where they would change user-facing behavior.
