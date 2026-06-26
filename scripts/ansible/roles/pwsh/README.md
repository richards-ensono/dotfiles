# pwsh

Ansible role to install PowerShell on supported Linux systems.

## Requirements

- Ansible 2.9 or newer
- Debian or Ubuntu
- A supported architecture: `x86_64` or `aarch64`

## Role Variables

User-overridable variables from `defaults/main.yml`:

```yaml
pwsh_target_version: "7.6.1"
```

Internal variables from `vars/main.yml`:

```yaml
pwsh_arch_map:
  x86_64: "amd64"
  aarch64: "arm64"

pwsh_arch: "{{ pwsh_arch_map[ansible_facts['architecture']] | default('amd64') }}"
pwsh_supported_architectures:
  - x86_64
  - aarch64
```

## Version Strategy

This role installs a pinned PowerShell `.deb` directly from the upstream GitHub release for the configured version.
If PowerShell is already installed at the same or a newer version, the role leaves it in place.

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - pwsh
```

Install a different pinned version:

```yaml
- hosts: localhost
  vars:
    pwsh_target_version: "7.6.0"
  roles:
    - pwsh
```

## Notes

- The role skips installation on unsupported architectures.

## License

MIT
