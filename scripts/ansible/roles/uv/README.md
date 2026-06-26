# uv

Ansible role to install the `uv` Python package manager and optional `uv tool` packages.

## Requirements

- Ansible 2.9 or newer
- Linux system matching the configured `uv_platform`

## Role Variables

User-overridable variables from `defaults/main.yml`:

```yaml
uv_version: "0.11.14"
uv_platform: "x86_64-unknown-linux-gnu"
uv_download_url: "https://github.com/astral-sh/uv/releases/download/{{ uv_version }}/uv-{{ uv_platform }}.tar.gz"
uv_checksum: "sha256:f3b623eb0e6141a7053d571d59a0bdc341e0f238ea8f5f0b4815ddbec9a2a296"
uv_install_dir: "{{ ansible_env.HOME }}/.local/bin"
```

Internal variables from `vars/main.yml`:

```yaml
uv_install_script_url: "https://astral.sh/uv/install.sh"
```

Shared input from `group_vars/all.yml`:

```yaml
uv_tools:
  - pre-commit
```

## Version Strategy

This role installs a pinned upstream binary tarball and validates it with a checksum before placing `uv` and `uvx` in the configured install directory.

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - uv
```

Install a different pinned version and tool list:

```yaml
- hosts: localhost
  vars:
    uv_version: "0.11.13"
    uv_tools:
      - pre-commit
      - ruff
  roles:
    - uv
```

## Notes

- The role verifies the installed `uv` binary with `uv --version`.
- Additional `uv tool install` behavior is documented centrally in `scripts/ansible/ROLE_VARIABLES.md` and is a later idempotence-hardening target.

## License

MIT
