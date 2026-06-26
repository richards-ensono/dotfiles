# pnpm

Ansible role to install [pnpm](https://pnpm.io/) from the official installer script.

## Defaults

```yaml
pnpm_version: "11.4.0"
pnpm_install_url: "https://get.pnpm.io/install.sh"
pnpm_home: "{{ ansible_facts['env'].HOME }}/.local/share/pnpm"
pnpm_global_packages: []
```

## Global packages

Set `pnpm_global_packages` to package/version specs passed to `pnpm install --global`:

```yaml
pnpm_global_packages:
  - "@fission-ai/openspec@latest"
  - "typescript@5.9.3"
```

## Notes

- `pnpm_version` is pinned to the current `pnpm@latest` version at the time this role was added.
- The role installs only when pnpm is missing or installed version differs from `pnpm_version`.
- `pnpm_global_packages` entries are installed after pnpm itself is verified.
- Shell PATH integration is handled by the Chezmoi-managed shell config.
