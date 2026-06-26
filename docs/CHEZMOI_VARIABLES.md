# Chezmoi Variables

This repository uses both Chezmoi built-in facts and repo-defined data keys.

## Built-in facts used by this repo

| Variable                    | Purpose in this repo                                                 | Current examples                                    |
| :-------------------------- | :------------------------------------------------------------------- | :-------------------------------------------------- |
| `.chezmoi.os`               | Select Linux vs Windows source paths and templates.                  | `.chezmoiignore`, `dot_config/windows_aliases.tmpl` |
| `.chezmoi.username`         | Derive repo-level identity defaults.                                 | `.chezmoi.toml.tmpl`                                |
| `.chezmoi.kernel.osrelease` | Detect WSL by checking for `microsoft` in the kernel release string. | `.chezmoiignore`, `dot_config/windows_aliases.tmpl` |
| `.chezmoi.osRelease.id`     | Gate distro-specific Linux content.                                  | `.chezmoiignore`                                    |

## Repo data keys

`.chezmoi.toml.tmpl` currently defines these data keys under `[data]`:

| Key           | Meaning                                                       | Current source       |
| :------------ | :------------------------------------------------------------ | :------------------- |
| `email`       | Default Git or contact email selected by username.            | `.chezmoi.toml.tmpl` |
| `name`        | Default Git author name.                                      | `.chezmoi.toml.tmpl` |
| `role`        | High-level persona marker used for personal vs work behavior. | `.chezmoi.toml.tmpl` |
| `signing_key` | GPG Signing key used to sign commits and messages             | `.chezmoi.toml.tmpl` |

## Guidance for future template work

1. Use built-in facts for platform and environment detection.
2. Use repo data keys for user- or environment-specific behavior that should stay easy to override in one place.
3. Prefer adding small, well-named data keys in `.chezmoi.toml.tmpl` over repeating hard-coded usernames or paths across templates.
4. Keep WSL detection consistent by reusing the existing `.chezmoi.kernel.osrelease | lower | contains "microsoft"` pattern unless a stronger shared helper is introduced.

## Common patterns in this repo

### Conditional identity values for clean-container runs

`dot_gitconfig.tmpl` only writes Git identity fields when values are available:

1. `name` comes from the top-level Chezmoi data key.
2. `email` comes from the top-level Chezmoi data key, or from `CHEZMOI_EMAIL` during source-only validation.
3. `signingkey` comes from the top-level Chezmoi data key `signing_key`.

That keeps source-only Docker validation green without inventing identity values when no Chezmoi config file has been initialized inside the container.

### Platform-gated files

`.chezmoiignore` is the main guardrail for whether a source path should apply on Linux, Windows, WSL, or Debian/Ubuntu-like systems.

### Delegate templates

Shared configs use path-specific delegates such as:

- `dot_config/nvim/init.lua.tmpl`
- `AppData/Local/nvim/init.lua.tmpl`
- `dot_config/powershell/Microsoft.PowerShell_profile.ps1.tmpl`
- `readonly_Documents/PowerShell/Microsoft.PowerShell_profile.ps1.tmpl`

Those files should stay thin and pass the current context through to the canonical template in `.chezmoitemplates/`.

### Path discovery

`dot_config/windows_aliases.tmpl` currently probes a small hard-coded set of Windows user directories under `/mnt/c/Users/...`. A later cleanup can move that to data-driven candidates, but current behavior is preserved for now.
