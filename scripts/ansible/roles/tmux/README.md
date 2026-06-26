# tmux

Ansible role to build and install tmux from a pinned source release.

## Requirements

- Ansible 2.9 or newer
- Debian or Ubuntu build environment
- `become: true` for dependency install and `make install`

## Role Variables

User-overridable variables from `defaults/main.yml`:

```yaml
tmux_version: "3.6a"
tmux_checksum: "sha256:b6d8d9c76585db8ef5fa00d4931902fa4b8cbe8166f528f44fc403961a3f3759"
```

Internal variables from `vars/main.yml`:

```yaml
tmux_src_dir: "/usr/local/src/tmux"
tmux_install_dir: "/usr/local"
```

## Version Strategy

This role downloads a pinned tmux source release, validates it with a checksum, then builds and installs it from source.

## Example Playbook

```yaml
- hosts: localhost
  become: true
  roles:
    - tmux
```

Install a different pinned release:

```yaml
- hosts: localhost
  become: true
  vars:
    tmux_version: "3.5a"
    tmux_checksum: "sha256:replace-with-matching-checksum"
  roles:
    - tmux
```

## Notes

- The role installs build dependencies before downloading the source archive.
- The installed binary is verified with `tmux -V` from the configured install directory.

## License

MIT
