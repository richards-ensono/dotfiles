## 1. Establish authoritative release metadata

- [x] 1.1 Recheck each managed component's latest stable release against its authoritative registry or publisher and record the selected version, asset URL, and source.
- [x] 1.2 Obtain and verify authoritative SHA-256 checksums for every direct-download binary, archive, and installer asset to be changed; do not use third-party checksum sources.
- [x] 1.3 Identify components whose publishers cannot provide a versioned, hash-verifiable installation path and document their bounded exception, rationale, and mitigation.
- [x] 1.4 Confirm selected source-build tags and Neovim plugin revisions are compatible with the supported host platforms and current configuration.

## 2. Pin managed provisioning inputs

- [x] 2.1 Update the managed versions for release-binary and source-build roles, including uv, Oh My Posh, nvm, pnpm, .NET, GitHub CLI, Podman, PowerShell, tmux, fzf, and Neovim.
- [x] 2.2 Replace default-branch, `latest`, and unversioned installer behavior with explicit supported versions, tags, commits, or package specifications for Git, package-manager, uv, and plugin sources.
- [x] 2.3 Update Ansible Galaxy role and collection constraints to explicit compatible versions.
- [x] 2.4 Update the four developer analysis-tool Go module versions to their selected stable releases while preserving ownership-marker idempotence.
- [x] 2.5 Update the explicitly tagged Telescope plugin and pin the remaining managed Neovim plugin references using supported immutable revisions.

## 3. Apply integrity verification

- [x] 3.1 Add version-coupled SHA-256 metadata and `get_url` verification for all direct release-asset downloads that have authoritative upstream hashes.
- [x] 3.2 Ensure architecture-specific URLs and checksums resolve to the same selected release asset and fail before execution, extraction, or installation on mismatch.
- [x] 3.3 Replace or explicitly document any installer path that cannot be both versioned and integrity verified.

## 4. Document version ownership and exceptions

- [x] 4.1 Add a maintained component version/integrity inventory or equivalent documentation that identifies each externally sourced component, its pinned source, and any exception.
- [x] 4.2 Update bootstrap and provisioning documentation to distinguish pinned externally sourced tools from intentionally distribution-managed APT/YUM packages.
- [x] 4.3 Document the Copilot CLI, SpecKit, and any other upstream-specific limitations with their source, rationale, and mitigation.

## 5. Validate provisioning behavior

- [x] 5.1 Run Ansible syntax and lint checks for the updated roles and requirements.
- [x] 5.2 Run focused validation for changed download, source-build, Go-tool, and plugin configuration paths, including checksum failure behavior where practical.
- [x] 5.3 Run the repository's Ansible idempotence validation and confirm a second unchanged run does not update managed components.
- [x] 5.4 Verify the final configuration contains no unintended floating external source, unqualified `latest` channel, or unverified direct download outside documented exceptions.
