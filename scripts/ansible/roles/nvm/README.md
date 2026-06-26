# nvm

Ansible role to install Node Version Manager from a pinned installer script.

## Requirements

- Ansible 2.9 or newer
- A POSIX shell environment for the installer

## Role Variables

User-overridable variables from `defaults/main.yml`:

```yaml
nvm_version: "v0.40.4"
nvm_install_url: "https://raw.githubusercontent.com/nvm-sh/nvm/{{ nvm_version }}/install.sh"
nvm_install_checksum: "sha256:4b7412c49960c7d31e8df72da90c1fb5b8cccb419ac99537b737028d497aba4f"
```

## Version Strategy

This role downloads a pinned upstream installer script, validates it with a checksum, and runs it once to create `~/.nvm/nvm.sh`.

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - nvm
```

Install a different pinned version:

```yaml
- hosts: localhost
  vars:
    nvm_version: "v0.40.3"
    nvm_install_url: "https://raw.githubusercontent.com/nvm-sh/nvm/{{ nvm_version }}/install.sh"
    nvm_install_checksum: "sha256:replace-with-matching-checksum"
  roles:
    - nvm
```

## Notes

- The installer is removed after execution.
- Shell integration for `nvm` is handled elsewhere in the Chezmoi-managed shell config.

## License

MIT
