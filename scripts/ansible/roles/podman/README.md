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
podman_version: "v6.1.1"
podman_build_dir: "/tmp/podman_build"
podman_network_handler: "pasta"
podman_runtime: "crun"
podman_compose_package: "podman-compose"
podman_container_image_commit: "08ce6b4207e7b151ea1c2830cdb1d4473cfd12aa"
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

This role uses a pinned Git tag and builds Podman from source, then configures rootless networking and user-level container settings. It removes the distribution `podman` and `podman-docker` packages so `/usr/local/bin/podman` is the only installation, installs the Debian `podman-compose` provider (configurable through `podman_compose_package`), and installs `/usr/local/bin/docker` as a Docker-compatible wrapper for it.

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
    podman_version: "v6.1.1"
    podman_network_handler: "slirp4netns"
    podman_runtime: "runc"
  roles:
    - podman
```

## Notes

- The role configures `/etc/containers/policy.json` and `/etc/containers/registries.conf` from `containers/image` at the reviewed immutable `podman_container_image_commit`. The project does not publish individual file checksums, so the full commit identity and TLS are the documented integrity boundary; see [`docs/PROVISIONING_INPUTS.md`](../../../../docs/PROVISIONING_INPUTS.md).
- Netavark and Aardvark-DNS `v2.1.0` are downloaded from reviewed release assets, checksum-verified, and installed at `/usr/local/libexec/podman`. The rootless `containers.conf` puts that directory first in `helper_binaries_dir`; the role removes Debian helper packages only after both managed helpers pass version verification, without resetting Podman storage.

## Network validation

After applying the role, run the focused checks as the configured rootless user:

```sh
podman network create podman-network-helper-check
podman network rm podman-network-helper-check
scripts/ansible/tests/test-podman-compose-network.sh
```

The Compose fixture uses an immutable BusyBox image digest and removes its project network and resources on exit. The role installs the `podman-compose` provider used by `podman compose`.
- Configuration is downloaded and validated in a staging directory. Existing managed configuration is backed up and restored if download, validation, or replacement fails.
- Rootless configuration includes `subuid` and `subgid` entries, user container config, and the unprivileged user namespace sysctl when available.
- On WSL, the role forces the Podman firewall driver to `iptables`.

## License

MIT
