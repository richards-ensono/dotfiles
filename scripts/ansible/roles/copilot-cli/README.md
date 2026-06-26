# Ansible Role: GitHub Copilot CLI

This Ansible role installs the GitHub Copilot CLI, bringing AI-powered coding assistance directly to your command line.

## Description

The GitHub Copilot CLI is an AI-powered terminal tool that provides:

- Terminal-native development with Copilot coding agent
- GitHub integration with natural language access to repositories, issues, and PRs
- Agentic capabilities for building, editing, debugging, and refactoring code
- MCP-powered extensibility with custom server support
- Full control with preview before execution

## Requirements

- Ansible 2.9 or higher
- Supported platforms: Debian, Ubuntu (Linux)
- An active GitHub Copilot subscription
- Internet connection for downloading the installation script

## Role Variables

Available variables are listed below, along with default values (see `defaults/main.yml`):

```yaml
# Whether to install copilot-cli
copilot_cli_enabled: true

# Version to install - "latest" or specific version like "v0.0.406"
copilot_cli_version: "latest"

# When using the latest channel, reinstall only when this is true
copilot_cli_update_latest: false

# Installation prefix (binary will be installed to PREFIX/bin/)
copilot_cli_install_prefix: "{{ ansible_env.HOME }}/.local"
```

Additional variables in `vars/main.yml`:

```yaml
# Installation script URL
copilot_cli_install_script_url: "https://gh.io/copilot-install"
```

## Dependencies

None.

## Example Playbook

Basic usage with defaults (installs latest version to `~/.local/bin`):

```yaml
- hosts: localhost
  roles:
    - copilot-cli
```

Install a specific version:

```yaml
- hosts: localhost
  vars:
    copilot_cli_version: "v0.0.406"
  roles:
    - copilot-cli
```

Install to a custom location:

```yaml
- hosts: localhost
  vars:
    copilot_cli_install_prefix: "/usr/local"
  become: true
  roles:
    - copilot-cli
```

## Post-Installation

After installation:

1. Ensure the installation directory is in your PATH:

   ```bash
   export PATH="$HOME/.local/bin:$PATH"
   ```

2. Launch the CLI:

   ```bash
   copilot
   ```

3. On first launch, authenticate using the `/login` slash command

4. Start using Copilot with natural language commands

## Updating

When `copilot_cli_version: "latest"`, the role behaves as install-if-missing by default.
Set `copilot_cli_update_latest: true` when you want a run to refresh the latest channel explicitly.

To update to a specific version, set the version variable and re-run:

```yaml
copilot_cli_version: "v0.0.410"
```

To force a refresh of the latest channel:

```yaml
copilot_cli_version: "latest"
copilot_cli_update_latest: true
```

## Authentication

GitHub Copilot CLI supports two authentication methods:

1. **Interactive login** (recommended):
   - Launch `copilot`
   - Use the `/login` command
   - Follow on-screen instructions

2. **Personal Access Token (PAT)**:
   - Create a fine-grained PAT with "Copilot Requests" permission at <https://github.com/settings/personal-access-tokens/new>
   - Set environment variable: `export GH_TOKEN=your_token` or `export GITHUB_TOKEN=your_token`

## Additional Resources

- [Official Documentation](https://docs.github.com/copilot/concepts/agents/about-copilot-cli)
- [GitHub Repository](https://github.com/github/copilot-cli)
- [Copilot Plans](https://github.com/features/copilot/plans)

## License

MIT

## Author Information

This role was created by Richard Slater as part of a chezmoi-managed dotfiles collection.
