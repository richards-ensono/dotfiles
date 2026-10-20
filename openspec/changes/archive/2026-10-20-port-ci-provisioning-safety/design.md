# Design

## Ownership and compatibility

Chezmoi owns Pi settings and user dotfiles. Ansible owns installations and system configuration. Existing role variables and version/checksum inputs remain unchanged. Repository-only CI, documentation, specifications, and tests are excluded from Chezmoi deployment.

## Installation transactions

Downloads and build outputs are verified before touching the active installation. Staging directories reside on the destination filesystem where rename is used. Existing recovery paths are never overwritten. Transaction-local flags distinguish preflight failure from partial activation, so rescue cannot remove an untouched installation. Backups remain available if restoration itself fails; the original error is propagated. Temporary staging is cleaned on both success and failure.

.NET replaces its user-local SDK directory. Neovim stages the install prefix and treats its executable and complete runtime tree as one recovery unit. Podman stages its complete install payload, including ancillary upstream helpers, independently of distro-owned network packages and validates both downloaded container configuration files before replacement. Existing rootless/network package provisioning is retained.

## Testing

Offline fixtures exercise checksum rejection, version mismatch, pre-existing recovery paths, successful activation, rollback and no-change repeat runs without touching real user or system paths. Source validators reject mutable configuration references and plugin-lock drift. Podman network integration runs only on an isolated provisioned host/container. CI rendering uses temporary destinations and never applies provisioning to runner homes.

## Pi settings

A Node.js run-after hook embeds a managed JSON fragment. Managed top-level keys override existing keys; subagents merges one level deep. Runtime preferences such as theme and changelog state remain unowned. Invalid JSON or unexpected object shapes fail without writes. An exclusive, mode-0600 temporary file is renamed atomically; unchanged content does not cause a rewrite. The hook targets Chezmoi's explicit destination, not the invoking process's HOME.

## Delivery

New commits use repository-local richards-ensono attribution and the existing signing key. No push or PR is implicit. Archive this change only after all acceptance checks pass; document unavailable full-system integration checks rather than claiming completion.
