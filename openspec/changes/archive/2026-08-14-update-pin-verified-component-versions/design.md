## Context

The Ansible provisioner manages release binaries, installation scripts, source builds, Go modules, Ansible Galaxy content, OS packages, and Neovim plugins. The version audit found stale explicit pins and several non-deterministic sources: default Git branches, unversioned installer URLs, `latest` channels, and unpinned Galaxy collections. Some release downloads already carry SHA-256 checksums, but the policy is incomplete.

The change must preserve the current platform support and idempotence behavior. It must not invent checksums or treat a checksum from an unauthenticated third party as authoritative.

## Goals / Non-Goals

**Goals:**

- Move repository-managed components to their latest stable versions identified during the audit.
- Make version selection explicit for externally sourced components wherever their upstream mechanism supports it.
- Require authoritative SHA-256 verification for directly downloaded binaries, archives, and scripts when available.
- Make any unavoidable floating or unverified source visible, justified, and regression-tested.
- Maintain idempotent Ansible behavior and existing OS package-manager ownership boundaries.

**Non-Goals:**

- Pinning every package supplied by APT/YUM or replacing the operating system package repositories.
- Mirroring upstream artifacts or introducing a new artifact repository.
- Changing the set of developer tools or the user-facing configuration except where an immutable version reference is necessary.
- Guaranteeing an installed-host inventory without running the playbook on that host.

## Decisions

### Maintain a single declarative version-and-integrity inventory in role variables

Each role that downloads or builds a managed component will hold its stable version and, where applicable, its release asset URL and SHA-256 value in defaults or vars. Tasks will interpolate only these values, avoiding a duplicate version embedded in shell commands.

This keeps upgrades reviewable in the files that own each tool and retains the repository's existing role architecture. A central generated manifest was considered, but would introduce cross-role indirection without replacing the role-specific asset and architecture logic.

### Prefer immutable upstream release assets over default-branch source clones

fzf and Neovim will use a stable tag or release archive rather than a shallow clone of the upstream default branch. Source builds remain acceptable when the tool has no suitable verified binary for the supported platform, provided the Git tag/commit is explicit.

A floating clone was rejected because `depth: 1` does not identify a reproducible source revision and can change without a repository edit.

### Verify direct downloads before execution or installation

`get_url` tasks that retrieve an executable, archive, or installer will set a SHA-256 checksum from the corresponding upstream release/checksum publication. The task will verify the fetched file before it is extracted, copied, or executed. Architecture-specific assets require architecture-specific hash mapping.

Using TLS alone was rejected: it protects transport but does not pin the artifact content reviewed by this repository. Checksums will not be added where an authoritative upstream hash cannot be obtained; those paths must be explicitly documented as exceptions.

### Pin package-manager and Git sources at supported immutable version references

Ansible Galaxy roles and collections, Go module installs, pnpm global packages, uv tools, and Neovim plugins will use explicit versions, tags, commits, or immutable package specifications supported by their manager. Installer scripts will be versioned and hashed if their upstream exposes a versioned script release; otherwise the installer will be replaced with a verified release asset where practical.

This balances reproducibility against upstream tooling constraints. A lockfile for every ecosystem was considered, but Ansible Galaxy, Go tools, uv tools, and Lazy.nvim have distinct lock semantics and a universal lockfile would not be authoritative for their installers.

### Document target-distribution exceptions

APT/YUM packages remain intentionally unpinned because the repository supports distribution package managers and the effective version is part of the selected OS repository. The documentation will state this boundary and identify any other justified exception, including the reason, source, and verification limitations.

## Risks / Trade-offs

- [A new release asset has a different name or architecture matrix] → Verify URLs and checksums against the official release publication and add architecture mappings before changing tasks.
- [Pinned source-build versions need newer build dependencies] → Run the role's narrow provisioning validation before the complete idempotence test.
- [Upstream does not publish a checksum or a versioned installer] → Prefer a signed/hashed release asset; otherwise document the bounded exception rather than fabricating integrity data.
- [Version updates introduce incompatible behavior] → Preserve current role interfaces and make each tool upgrade independently reviewable; roll back by restoring the prior version and checksum pair.
- [Floating plugin updates are required by the plugin manager] → Pin supported tags/commits and validate Neovim headless synchronization after updating references.

## Migration Plan

1. Obtain current stable releases and authoritative checksums from each upstream publisher.
2. Update role variables, requirements, plugin references, and bootstrap documentation in small component groups.
3. Run syntax, lint, and focused role validation after each group, followed by the repository idempotence test.
4. On failure, restore the immediately previous version/checksum pair for the affected component; no persistent data migration is required.

## Open Questions

- Which exact upstream distribution should replace the currently unversioned Copilot CLI installer if it cannot expose a versioned script plus authoritative checksum?
- Which Neovim plugin revisions are compatible with the selected Neovim release and LazyVim configuration?
- Does the project want to pin APT repository snapshots in a future, OS-image-focused change?
