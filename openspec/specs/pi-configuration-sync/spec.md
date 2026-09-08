# Pi Configuration Sync

## Purpose

Synchronize repository-owned Pi model and extension configuration while preserving Pi-owned settings, runtime artifacts, and state.

## Requirements

### Requirement: Declarative Pi model configuration is synchronized
The chezmoi source SHALL declare and apply the Pi model configuration owned by this repository: default provider, default model, default thinking level, enabled models, and subagent model defaults.

#### Scenario: Apply on a host with existing Pi settings
- **WHEN** `chezmoi apply` runs on a host whose Pi settings include additional Pi-managed keys
- **THEN** the owned model configuration SHALL match the repository declaration and additional keys SHALL remain unchanged

#### Scenario: Apply on a host without Pi settings
- **WHEN** `chezmoi apply` runs and `~/.pi/agent/settings.json` does not exist
- **THEN** it SHALL create valid Pi settings containing the declared model configuration

### Requirement: Declarative Pi extension configuration is synchronized
The chezmoi source SHALL declare and apply the Pi extension package list owned by this repository.

#### Scenario: Apply updates extension declarations
- **WHEN** the repository extension package declaration differs from the target Pi settings
- **THEN** `chezmoi apply` SHALL replace the target package declaration with the declared list

#### Scenario: Pi extension runtime artifacts exist
- **WHEN** Pi has installed extension artifacts or dependencies under its agent directory
- **THEN** `chezmoi apply` SHALL NOT delete, replace, or otherwise synchronize those runtime artifacts

### Requirement: Pi-owned state is preserved
The configuration synchronization SHALL preserve Pi-owned settings and files outside the explicitly owned model and extension keys.

#### Scenario: Pi records changelog metadata
- **WHEN** Pi updates `lastChangelogVersion` in its settings file
- **THEN** a subsequent `chezmoi apply` SHALL preserve that value

#### Scenario: Pi owns agent-directory permissions and state
- **WHEN** Pi changes the permissions or creates sessions, missions, trust data, package files, or caches under `~/.pi/agent`
- **THEN** `chezmoi apply` SHALL NOT reset those permissions or remove those files

### Requirement: Repeated apply is idempotent
The synchronization mechanism SHALL converge after applying the same repository configuration more than once.

#### Scenario: Apply runs twice without configuration changes
- **WHEN** `chezmoi apply` is run twice and Pi does not change its configuration between runs
- **THEN** the second run SHALL leave the owned settings and Pi-owned state unchanged and SHALL not report Pi configuration drift

### Requirement: Settings updates are safe
The synchronization mechanism SHALL not replace a usable Pi settings file with invalid or incomplete JSON.

#### Scenario: Existing settings are invalid JSON
- **WHEN** the existing Pi settings file cannot be parsed as JSON
- **THEN** the apply operation SHALL fail with an actionable error and SHALL leave the existing file unchanged
