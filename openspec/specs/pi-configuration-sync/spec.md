# Pi Configuration Sync

## Purpose

Synchronize repository-owned Pi model, extension, and default-tool configuration while preserving Pi-owned settings, runtime artifacts, and state.

## Requirements

### Requirement: Declarative Pi model configuration is synchronized
The chezmoi source SHALL declare and apply the Pi model configuration owned by this repository: default provider, default model, default thinking level, enabled models, and subagent model defaults.

#### Scenario: Apply on a host with existing Pi settings
- **WHEN** `chezmoi apply` runs on a host whose Pi settings include additional Pi-managed keys
- **THEN** the owned model configuration SHALL match the repository declaration and additional keys SHALL remain unchanged

#### Scenario: Apply on a host without Pi settings
- **WHEN** `chezmoi apply` runs and `~/.pi/agent/settings.json` does not exist
- **THEN** it SHALL create valid Pi settings containing the declared model configuration

### Requirement: Declarative Pi default tool configuration is synchronized
The chezmoi source SHALL declare and apply `defaultTools: ["+codemode"]` as a repository-owned setting. The declaration SHALL enable CodeMode additively without replacing Pi's inherited default tools.

#### Scenario: Apply enables additive CodeMode configuration
- **WHEN** `chezmoi apply` synchronizes Pi settings on a host without an existing `defaultTools` key
- **THEN** the target settings SHALL contain `defaultTools: ["+codemode"]`
- **AND** Pi's default selection SHALL retain its normal default tools and add CodeMode when no project or explicit CLI tool-selection override is in effect

#### Scenario: Existing default tool configuration differs
- **WHEN** `chezmoi apply` synchronizes Pi settings with an existing machine-local `defaultTools` value
- **THEN** the target `defaultTools` SHALL be replaced with the repository declaration
- **AND** unrelated Pi-owned settings SHALL remain unchanged

#### Scenario: Apply creates missing settings
- **WHEN** `chezmoi apply` synchronizes Pi settings and `~/.pi/agent/settings.json` does not exist
- **THEN** it SHALL create valid JSON containing the additive CodeMode declaration and all other managed settings

### Requirement: Declarative Pi extension configuration is synchronized
The chezmoi source SHALL declare and apply the Pi extension package list owned by this repository. That list SHALL contain `npm:graphify-pi` exactly once alongside the existing extension declarations, including `npm:@narumitw/pi-chrome-devtools`.

#### Scenario: Apply updates extension declarations
- **WHEN** the repository extension package declaration differs from the target Pi settings
- **THEN** `chezmoi apply` SHALL replace the target package declaration with the declared list

#### Scenario: Locally declared Graphify is retained by synchronization
- **WHEN** existing Pi settings contain `npm:graphify-pi` and the managed settings are synchronized
- **THEN** the target package list SHALL contain `npm:graphify-pi` exactly once and SHALL match the full repository declaration

#### Scenario: Graphify is not yet locally declared
- **WHEN** Pi settings without `npm:graphify-pi` are synchronized
- **THEN** the target package list SHALL include `npm:graphify-pi` while retaining all existing repository-managed extension declarations

#### Scenario: Pi extension runtime artifacts exist
- **WHEN** Pi has installed extension artifacts or dependencies under its agent directory
- **THEN** `chezmoi apply` SHALL NOT delete, replace, or otherwise synchronize those runtime artifacts

### Requirement: Pi-owned state is preserved
The configuration synchronization SHALL preserve Pi-owned settings and files outside the explicitly owned model, extension package, and default tool selection keys. Existing managed model values SHALL remain unchanged by the addition of CodeMode and Graphify declarations.

#### Scenario: Pi records changelog metadata
- **WHEN** Pi updates `lastChangelogVersion` in its settings file
- **THEN** a subsequent `chezmoi apply` SHALL preserve that value

#### Scenario: Pi owns agent-directory permissions and state
- **WHEN** Pi changes the permissions or creates sessions, missions, trust data, package files, or caches under `~/.pi/agent`
- **THEN** `chezmoi apply` SHALL NOT reset those permissions or remove those files

#### Scenario: Other Pi settings accompany new declarations
- **WHEN** Pi settings contain a theme, additional unowned top-level settings, or unowned subagent settings before synchronization
- **THEN** synchronization SHALL preserve those values while applying the managed CodeMode and extension declarations
- **AND** existing managed model preferences and all pre-existing managed extension declarations SHALL remain unchanged

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
