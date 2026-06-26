# dotnet

Ansible role to install the .NET SDK with the official `dotnet-install.sh` script.

## Requirements

- Ansible 2.9 or newer
- Internet access to download the installer script

## Role Variables

User-overridable variables from `defaults/main.yml`:

```yaml
dotnet_version: "10.0"
dotnet_sdk_version: "10.0"
dotnet_install_dir: "/usr/share/dotnet"
dotnet_install_script_url: "https://dot.net/v1/dotnet-install.sh"
```

## Version Strategy

This role uses the official installer script with a configured release channel, so it effectively installs the latest SDK available in that channel.

## Example Playbook

```yaml
- hosts: localhost
  roles:
    - dotnet
```

Install from a different release channel:

```yaml
- hosts: localhost
  vars:
    dotnet_version: "9.0"
    dotnet_sdk_version: "9.0"
  roles:
    - dotnet
```

## Notes

- The installer script is downloaded to a temporary directory and removed after the run.
- The role currently verifies the SDK through `~/.dotnet/dotnet --version` even though `dotnet_install_dir` is still documented as `/usr/share/dotnet`; that mismatch remains a Phase 3 cleanup item.

## License

MIT
