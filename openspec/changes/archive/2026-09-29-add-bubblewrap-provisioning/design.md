## Context

The common `packages` role already installs the shared `packages_managed_packages` list during the privileged system-setup play. The repository supports Debian hosts using apt, and distribution packages deliberately remain version-managed by the configured distribution repositories. The existing Docker idempotence test confirms a small set of provisioned command-line tools are discoverable and executable after the first playbook run, then confirms the second run makes no changes.

Bubblewrap is an apt-provided utility that exposes `/usr/bin/bwrap` for unprivileged namespace and filesystem sandbox construction. The package alone supplies the required executable; agent-specific sandbox policies are mutable runtime concerns and are not Chezmoi- or Ansible-managed configuration in this change.

The first idempotence-test run revealed that the currently pinned Netavark `v2.1.0` executable requires `GLIBC_2.39`, which is unavailable in the legacy Debian Bookworm container baseline. The role safely rolls back that failed helper replacement, but the test cannot reach the post-provisioning Bubblewrap assertion or its second idempotence pass. The repository now standardizes its Docker developer checks on Debian 13/Trixie, whose runtime satisfies the helper's glibc requirement.

## Goals / Non-Goals

**Goals:**

- Provision the distribution-supported `bubblewrap` package through the shared system package list.
- Assert that `bwrap` is available on `PATH` and responds successfully to `--version` after a first provisioning run.
- Review every managed external-component pin family using authoritative publisher sources and record the disposition of each family.
- Migrate every Docker developer-check task to the Debian 13/Trixie baseline and remove obsolete Bookworm-specific bootstrap behavior.
- Restore the Debian 13/Trixie provisioning-test baseline by configuring a compatible, checksum-verified Podman network-helper pair.
- Preserve the existing idempotence contract.

**Non-Goals:**

- Create a Bubblewrap wrapper, default sandbox profile, or agent integration.
- Change kernel user-namespace policy, permissions, or security controls.
- Pin a Bubblewrap version or download a Bubblewrap artifact outside the distribution package manager.
- Retain Debian Bookworm as a Docker developer-check baseline.
- Extend provisioning support beyond the current Debian/apt baseline.
- Relax helper checksum verification, use floating release references, or alter the Podman rollback behavior.

## Decisions

### Use the shared packages role

Add `bubblewrap` to `packages_managed_packages` in `scripts/ansible/group_vars/all.yml`. The existing role is already responsible for standard system packages and runs with privilege in the system-setup play.

**Alternative considered:** create a dedicated Bubblewrap role. Rejected because the package requires no custom installation, configuration, or lifecycle behavior, so another role would add needless surface area.

### Validate command availability in the existing idempotence test

Add `bwrap` to the first-run command verification loop in `.vscode/test-ansible-idempotence.sh` and invoke it with `--version`. This directly covers the capability agents require: a discoverable, executable `bwrap` command, while the second pass continues to prove idempotence.

**Alternative considered:** test a complete nested Bubblewrap sandbox in the Docker test. Rejected because container runtime capabilities and user-namespace policy can affect nested namespace creation independently of package provisioning. That would make this provisioning test environment-dependent and conflate package availability with agent sandbox-policy validation.

### Retain distribution version ownership

Treat Bubblewrap as an unpinned package-manager input, consistent with the repository's documented APT/YUM version boundary. No version inventory row is required for it.

**Alternative considered:** install a pinned upstream release binary. Rejected because it bypasses the supported package manager and imposes unnecessary artifact-verification and update maintenance.

### Standardize Docker developer checks on Debian 13/Trixie

Replace every Docker developer-check image reference with `debian:trixie` so the dry-run, syntax, full-apply, idempotence, and shell-lint tasks validate one current Debian baseline. Remove the Debian Bookworm-specific PPA bootstrap branch; the existing Trixie branch installs Ansible from the distribution repository.

**Alternative considered:** retain Bookworm alongside Trixie. Rejected because the repository is moving its single baseline rather than claiming compatibility across divergent Debian release runtimes.

### Review all managed external-component pins

Treat the Podman-helper repair as a supply-chain maintenance event that requires a repository-wide review. For every managed pin family, query its authoritative publisher source, evaluate the latest stable candidate against the repository's runtime and platform constraints, independently verify direct-download assets against publisher checksums, and record whether the family is updated, already current, compatibility-held, blocked, or an explicit exception. Do not change an operational pin when its candidate fails any compatibility or integrity gate.

**Alternative considered:** limit review to Netavark and Aardvark-DNS. Rejected because repository policy requires a complete managed-pin review before changing a direct-download pin.

### Restore compatible Podman helper artifacts

Select a Netavark/Aardvark-DNS pair that satisfies the role's Podman compatibility requirements and executes on Debian 13/Trixie's glibc runtime. Discover releases and checksum manifests only from the authoritative upstream publisher, reject artifacts with unavailable or mismatched checksums, and update the role defaults and component-version inventory together. Preserve the existing staged replacement, verification, and rollback flow.

**Alternative considered:** bypass the version command in the Docker test or remove the helper verification. Rejected because it would weaken the existing executable validation and conceal an incompatible artifact.

## Risks / Trade-offs

- [A future host disables unprivileged user namespaces or constrains them through a security policy] → The package and command check can still pass while a particular agent sandbox fails; agent integration must validate its required Bubblewrap invocation on its target host.
- [The distribution changes Bubblewrap behavior or command flags] → The test uses the stable `--version` availability check rather than a policy-specific sandbox invocation; distribution updates remain owned by the supported apt repository.
- [The Docker idempotence image does not include the same package version as a target host] → The change verifies that the package installs and exposes its command on the test image, without asserting an unsupported cross-distribution version equality.
- [A helper release is compatible with Podman but not the Debian 13/Trixie glibc baseline] → Execute the verified staged helper in the Trixie container before configuring it; retain the role's rollback behavior if a later host-specific failure occurs.
- [A reviewed pin lacks an authoritative checksum or a compatible stable candidate] → Preserve its operational pin and record the specific blocked or compatibility-held disposition in the version inventory.
