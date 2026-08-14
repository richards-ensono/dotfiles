# GitHub Copilot CLI

This role installs the official [`@github/copilot`](https://www.npmjs.com/package/@github/copilot) npm package at an exact version in the user's local prefix.

## Defaults

```yaml
copilot_cli_enabled: true
copilot_cli_package: "@github/copilot"
copilot_cli_version: "1.0.80"
copilot_cli_install_prefix: "{{ ansible_env.HOME }}/.local"
```

The npm registry's package metadata supplies the tarball integrity value and npm verifies it during installation. The role deliberately does not use the floating `gh.io/copilot-install` script. The preceding `nvm` role provisions Node.js `v24.19.0`; this role invokes only its `nvm_npm_executable` path and fails explicitly if that runtime is unavailable.

The package is an upstream distribution rather than a repository-owned binary: npm registry availability and npm's integrity metadata are required. Authentication remains an interactive Copilot operation after provisioning.
