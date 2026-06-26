# gh

Ansible role to build and install the GitHub CLI from source.

## Requirements

- Ansible 2.9 or newer
- Debian or Ubuntu build environment
- Go installed and available at `/usr/local/go/bin`

## Role Variables

User-overridable variables from `defaults/main.yml`:

```yaml
gh_version: "v2.92.0"
gh_build_dir: "/tmp/gh_build"
```

Internal variables from `vars/main.yml`:

```yaml
gh_git_repo: "https://github.com/cli/cli.git"
```

## Version Strategy

This role uses a pinned Git tag and builds GitHub CLI from source into `/usr/local`.

## Example Playbook

```yaml
- hosts: localhost
  become: true
  roles:
    - gh
```

Build a different pinned version:

```yaml
- hosts: localhost
  become: true
  vars:
    gh_version: "v2.91.0"
  roles:
    - gh
```

## Notes

- The role installs build dependencies before compiling.
- The CA certificate environment is set explicitly during the build to avoid SSL issues in source builds.

## License

MIT
