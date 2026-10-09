## Context

The repository currently manages `~/.pi/agent` as a normal chezmoi directory, including one complete `settings.json`. Pi also owns that directory at runtime: it installs extension artifacts below `npm/` and `git/`, records mission/session-related state, restricts directory permissions, and updates `lastChangelogVersion`. Applying the complete managed directory restores stale metadata and conflicts with Pi's runtime ownership.

The desired synchronized surface is limited to the model preferences and extension declarations. This change must preserve every other Pi setting and runtime artifact already present on the host.

## Goals / Non-Goals

**Goals:**
- Declare the Pi model-related settings and extension package list in chezmoi source.
- Merge only those declared settings into `~/.pi/agent/settings.json` during `chezmoi apply`.
- Preserve unowned top-level settings, Pi-generated metadata, and all runtime files and directory modes.
- Make repeated apply operations idempotent.

**Non-Goals:**
- Version-pin, install, remove, or synchronize extension runtime files.
- Synchronize Pi authentication, trust records, sessions, missions, package caches, or changelog state.
- Change Pi provider behavior beyond the currently declared model preferences.
- Rework unrelated chezmoi-managed configuration.

## Decisions

### Model and extension declarations are a managed settings fragment
Store only the stable settings that this repository owns in a separate source fragment: the default provider/model/thinking level, enabled models, subagent model configuration, and `packages` extension declarations. Do not use the fragment as Pi's target `settings.json`.

This provides an explicit ownership boundary and prevents the configuration source from accidentally expanding to include state Pi later writes.

**Alternatives considered:**
- Continue managing the full `settings.json`: rejected because Pi-generated fields are repeatedly reset.
- Ignore all of `~/.pi/agent`: rejected because it would stop synchronizing the requested models and extensions.

### Apply configuration through a field-level JSON merge
Use a chezmoi apply script or equivalent templated mechanism to read the existing target JSON, overlay only the owned fragment keys, and write valid JSON atomically. The merge must create an empty object when the target file does not yet exist.

This preserves unowned keys such as `lastChangelogVersion` and future Pi metadata while ensuring declared keys converge to repository configuration.

**Alternatives considered:**
- Delete `lastChangelogVersion` from the full managed file: rejected because a full-file apply would still delete or overwrite other runtime-owned settings.
- Template the target file from its current contents: rejected because source rendering should not depend on mutable target state and it would not clearly define ownership.

### Leave the Pi agent directory unmanaged
Remove the regular chezmoi mapping for the `~/.pi/agent` directory and retain only the new declarative fragment and merge mechanism. Pi remains responsible for directory mode and runtime descendants.

This avoids directory permission drift and prevents apply from treating installed package and state trees as dotfile contents.

## Risks / Trade-offs

- [Malformed existing JSON prevents a merge] → Validate JSON before replacing the file, fail with an actionable error, and retain the original file.
- [A future required setting is omitted from the owned fragment] → Document the owned key set and add deliberate keys rather than broadening to full-file synchronization.
- [A merge tool is absent on a target host] → Use an already-provisioned, portable runtime/tool or explicitly provision the required tool as part of the implementation.
- [Pi changes the shape of an owned key] → Preserve unknown keys and cover the owned key overlay with an idempotence test or verification command.

## Migration Plan

1. Move the stable model and extension declarations out of the direct `~/.pi/agent/settings.json` mapping into an owned fragment.
2. Remove the managed agent-directory mapping without deleting the existing target directory or Pi runtime state.
3. Add the idempotent merge step and run `chezmoi apply` to overlay owned values.
4. Verify a second apply produces no Pi-related status or content changes, while retained Pi-generated metadata remains intact.
5. Roll back by restoring the previous source mapping; no runtime data deletion is required.

## Open Questions

- None. The implementation will select the repository's established portable JSON tooling after inspecting existing provisioning support.
