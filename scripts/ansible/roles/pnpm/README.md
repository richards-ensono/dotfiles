# pnpm

Ansible role to install [pnpm](https://pnpm.io/) from the official version-selecting installer script.

## Defaults

```yaml
pnpm_version: "11.21.0"
pnpm_install_url: "https://get.pnpm.io/install.sh"
pnpm_home: "{{ ansible_facts['env'].HOME }}/.local/share/pnpm"
pnpm_global_packages: []
```

The installer receives the exact `PNPM_VERSION` value and the role verifies the resulting executable version. The official installer endpoint does not publish an independently authoritative checksum for the script; this is recorded as a bounded TLS/source exception in `docs/COMPONENT_VERSION_INVENTORY.md`.

Global package entries should include explicit versions (for example `typescript@5.9.3`), not `latest`.
