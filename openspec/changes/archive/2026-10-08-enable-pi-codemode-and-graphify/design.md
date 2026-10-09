## Context

`.chezmoitemplates/pi/settings.json` declares repository-owned model preferences and ten extension packages. `run_after_merge-pi-settings.js.tmpl` overlays its top-level keys onto existing Pi settings and merges the owned subagent preferences separately. Installed extensions, credentials, sessions, caches, and other runtime state remain outside chezmoi ownership.

The Chrome DevTools extension is already declared. Its installed documentation recommends `defaultTools: ["+codemode"]`, and its browser capabilities are registered with CodeMode exposure and inactive direct tools. Neither the managed fragment nor the inspected live settings currently declares `defaultTools`. The inspected live settings additionally declare `npm:graphify-pi`, which the managed package list does not contain.

The existing `pi-configuration-sync` spec describes ownership only of model and extension keys. Adding `defaultTools` therefore requires an explicit ownership update, not a new synchronization mechanism.

## Goals / Non-Goals

**Goals:**
- Enable Pi's built-in CodeMode alongside its normal default tools.
- Include `npm:graphify-pi` in the repository-managed extension package list exactly once.
- Preserve existing model settings, extension declarations, unowned settings, and runtime artifacts.
- Verify synchronization against isolated settings fixtures, including idempotence and malformed input.

**Non-Goals:**
- Change CodeMode to `only` mode, expose browser tools directly, or add `tool_search`.
- Change model defaults, browser endpoints, tool availability permissions, or extension exposure.
- Upgrade Pi or install, update, pin, or synchronize extension runtime files.
- Apply unrelated dotfiles or change the settings merge architecture.

## Decisions

### Use additive default tool selection

Declare exactly `defaultTools: ["+codemode"]` in the managed fragment. Pi interprets this as an addition to its inherited defaults, retaining `read`, `bash`, `edit`, and `write`. A plain `["codemode"]` allowlist would replace defaults and is rejected. Enabling `codemode.mode: "only"` is rejected because it changes how all tools are presented and is unnecessary for the requested integration.

`defaultTools` becomes repository-owned: the merge script replaces a machine-local value with the managed declaration rather than merging arrays. This matches the existing top-level ownership model. Trusted project settings and explicit CLI selections can still override Pi's resolved tool selection; the proposal does not override those controls.

### Manage Graphify using the existing package declaration format

Add `npm:graphify-pi` to `packages` without removing or reordering existing entries. This preserves the already locally configured extension declaration during future merges. Editing only the live settings is rejected because the managed package array would overwrite it again. No dependency resolution or installation occurs during artifact creation; any later dependency addition or upgrade must follow the repository's registry and compatibility verification policy.

### Reuse the merge script without behavioral changes

The existing top-level overlay already handles `defaultTools` and `packages`, and its temporary-file replacement preserves valid JSON updates. No merge-script edit is needed. Add focused regression coverage using the rendered script with a temporary `HOME` or equivalent isolated fixtures; do not run the script against the operator's actual settings during tests. Retain negative coverage for malformed existing JSON.

## Risks / Trade-offs

- [Machine-local `defaultTools` is replaced] → Document repository ownership and verify replacement with an isolated fixture; do not promise preservation of that now-owned key.
- [Explicit CLI or project selections omit CodeMode] → Verify ordinary default startup separately and retain Pi's explicit override behavior.
- [Enabling CodeMode is mistaken for confirmed browser connectivity] → Treat tool activation, browser capability discovery, and a read-only page-list call as distinct verification steps; report an unavailable browser as an unverified integration, not a passing check.
- [Browser results contain private page data] → Use a clean, non-sensitive test page/profile and report capability names and success status rather than page contents.
- [The managed package array removes unrelated local-only entries] → Preserve all existing managed packages and explicitly include Graphify; do not change the established replace-array policy.
- [Graphify is declared but not installed or loaded] → Distinguish settings verification from package installation and runtime loading; do not claim runtime success from a JSON comparison alone.

## Migration Plan

1. Update the managed fragment with the two declarations and run focused isolated merge verification.
2. Preview the targeted settings synchronization without applying unrelated dotfiles.
3. With operator approval, synchronize Pi settings through the existing mechanism, then reload Pi or start a fresh normal session.
4. Confirm live declarations and, where a safe browser session is available, verify CodeMode discovery and a read-only Chrome DevTools call.
5. To roll back, revert the package-list addition and remove the managed `defaultTools` declaration. Because the merge preserves unowned keys, removing it from the fragment alone does not delete it from live settings: explicitly restore the pre-change live `defaultTools` value or remove that key if it was previously absent. Runtime files need not be deleted.

## Open Questions

None blocking proposal creation. Runtime browser availability and package loading must be established during implementation verification rather than inferred from configuration.
