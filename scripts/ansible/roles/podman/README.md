# podman

Ansible role to build and install Podman from source and configure rootless operation.

## Requirements

- Ansible 2.9 or newer
- Debian or Ubuntu
- Go installed and available at `/usr/local/go/bin`
- `become: true` for the system and rootless configuration steps

## Role Variables

User-overridable variables from `defaults/main.yml`:

```yaml
podman_version: "v5.8.2"
podman_build_dir: "/tmp/podman_build"
podman_network_handler: "pasta"
podman_runtime: "crun"
```

Internal variables from `vars/main.yml`:

```yaml
podman_git_repo: "https://github.com/containers/podman.git"

podman_package_map:
  pasta: "passt"
  slirp4netns: "slirp4netns"
  crun: "crun"
  runc: "runc"

podman_build_tags: "seccomp apparmor"
podman_user: "{{ ansible_env.SUDO_USER | default(ansible_user_id) }}"
```

## Version Strategy

This role uses a pinned Git tag and builds Podman from source, then configures rootless networking and user-level container settings.

## Example Playbook

```yaml
- hosts: localhost
  become: true
  roles:
    - podman
```

Override the pinned version or runtime choices:

```yaml
- hosts: localhost
  become: true
  vars:
    podman_version: "v5.8.1"
    podman_network_handler: "slirp4netns"
    podman_runtime: "runc"
  roles:
    - podman
```

## Notes

- The role configures `/etc/containers/policy.json` and `/etc/containers/registries.conf` from upstream defaults.
- Rootless configuration includes `subuid` and `subgid` entries, user container config, and the unprivileged user namespace sysctl when available.
- On WSL, the role forces the Podman firewall driver to `iptables`.

## License

MIT
