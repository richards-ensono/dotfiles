## ADDED Requirements

### Requirement: Provision the Bubblewrap command
The Ansible system setup SHALL install the distribution-managed `bubblewrap` package through the shared package configuration on supported Debian/apt hosts. After provisioning, the host SHALL expose an executable `bwrap` command on its standard `PATH`.

#### Scenario: Fresh supported host receives Bubblewrap
- **WHEN** the Ansible playbook runs on a supported Debian/apt host where `bubblewrap` is not installed
- **THEN** it installs the distribution-managed package and `bwrap` is executable on the host's standard `PATH`

#### Scenario: Bubblewrap is already installed
- **WHEN** the Ansible playbook runs on a supported host that already has the configured `bubblewrap` package installed
- **THEN** the shared package installation task does not report a change for Bubblewrap

### Requirement: Validate Bubblewrap after provisioning
The repository's automated Ansible provisioning test SHALL verify after its first successful playbook run that `bwrap` is discoverable on `PATH` and that `bwrap --version` executes successfully. The test MUST retain its assertion that the second playbook run is idempotent.

#### Scenario: Provisioning test validates Bubblewrap availability
- **WHEN** the automated Ansible provisioning test completes its first playbook run
- **THEN** it locates `bwrap` on `PATH` and successfully invokes it with `--version` before starting the second playbook run

#### Scenario: Bubblewrap is unavailable after provisioning
- **WHEN** the first playbook run completes without an executable `bwrap` command on `PATH` or the version command fails
- **THEN** the automated provisioning test fails with an error identifying the Bubblewrap command failure

### Requirement: Preserve the provisioning-test baseline
The repository's Docker-based developer checks SHALL use the Debian 13/Trixie baseline. The pinned Podman network-helper executables used by the shared Ansible provisioning play SHALL be compatible with that runtime. The helper release pair SHALL be selected from authoritative upstream sources and configured only with corresponding publisher-provided checksums.

#### Scenario: First provisioning pass reaches Bubblewrap validation
- **WHEN** the automated provisioning test runs on its Debian 13/Trixie baseline
- **THEN** the Podman network-helper provisioning succeeds and the test reaches the post-provisioning `bwrap` availability and version checks

#### Scenario: Incompatible helper artifact is considered
- **WHEN** a candidate Podman helper artifact requires a glibc version unavailable on the Debian 13/Trixie baseline or lacks an authoritative checksum
- **THEN** it is not configured for provisioning

#### Scenario: Legacy Bookworm bootstrap is not selected
- **WHEN** Ansible is bootstrapped on Debian 13/Trixie
- **THEN** it uses the distribution-provided Ansible packages and does not add the Bookworm-specific external PPA path

### Requirement: Audit managed external-component pins
The repository SHALL review every managed external-component pin family against its authoritative publisher source before changing a direct-download pin. The version inventory SHALL record each family’s selected stable version and integrity evidence, compatibility hold, blocked status, or documented exception.

#### Scenario: A direct-download pin requires repair
- **WHEN** a direct-download artifact must change to restore provisioning compatibility
- **THEN** the repository reviews every managed pin family and applies only stable, compatible candidates whose publisher-provided integrity metadata matches the exact configured assets

#### Scenario: A reviewed family cannot be updated
- **WHEN** a pin family has no compatible current stable candidate or no usable authoritative integrity evidence
- **THEN** its operational pin remains unchanged and the inventory records the compatibility hold, blocked status, or exception
