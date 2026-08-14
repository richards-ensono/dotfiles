# tmux

Ansible role to build and install tmux from a pinned source release.

## Requirements

- Ansible 2.9 or newer
- Debian or Ubuntu build environment
- `become: true` for dependency install and `make install`

## Role Variables

User-overridable variables from `defaults/main.yml`:

```yaml
tmux_version: "3.7b"
tmux_checksum: "sha256:87f2e99e3b685973f2ca002ffd6ed7e51a5744f7009daae5a15670b6d532db96"
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
    tmux_version: "3.7b"
    tmux_checksum: "sha256:replace-with-matching-checksum"
  roles:
    - tmux
```

## Notes

- The role installs build dependencies before downloading the source archive.
- The installed binary is verified with `tmux -V` from the configured install directory.

## License

MIT
