## ADDED Requirements

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

## MODIFIED Requirements

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
