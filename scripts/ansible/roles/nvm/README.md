# nvm

Ansible role to install Node Version Manager from the versioned upstream GitHub installer script.

## Defaults

```yaml
nvm_version: "v0.40.6"
nvm_install_url: "https://raw.githubusercontent.com/nvm-sh/nvm/{{ nvm_version }}/install.sh"
nvm_dir: "{{ ansible_facts['env'].HOME }}/.nvm"
nvm_node_version: "v24.19.0"
nvm_node_bin: "{{ nvm_dir }}/versions/node/{{ nvm_node_version }}/bin"
nvm_node_executable: "{{ nvm_node_bin }}/node"
nvm_npm_executable: "{{ nvm_node_bin }}/npm"
```

The role installs the exact Node.js LTS version through nvm after installing nvm, and verifies both `nvm_node_executable` and `nvm_npm_executable`. These stable paths are intended for dependent Ansible tasks; they must not be replaced with distribution-managed `node` or bare `npm`. If either executable is unavailable, the role fails with an actionable message.

The Git ref is pinned to the selected release. nvm upstream does not publish an authoritative checksum for `install.sh`, so the role uses TLS plus the immutable release ref as a documented bounded exception; it does not invent a checksum. The installer is removed after execution and shell integration remains in the Chezmoi-managed shell config.
