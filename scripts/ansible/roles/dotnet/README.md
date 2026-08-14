# dotnet

Ansible role to install the official .NET SDK Linux archive with an exact version and architecture-specific integrity verification.

## Defaults

```yaml
dotnet_sdk_version: "10.0.400"
dotnet_install_dir: "{{ ansible_env.HOME }}/.dotnet"
```

The role uses Microsoft's versioned `builds.dotnet.microsoft.com` assets for Linux x64 and arm64 and verifies them before extraction. Microsoft publishes SHA-512 values for these assets; `sha512:` checksums are therefore an upstream-format exception to the repository's preferred SHA-256 policy. No SHA-256 value is fabricated.

The archive is extracted into the user-local directory and the installed SDK version is checked exactly. Unsupported architectures fail before any download.
