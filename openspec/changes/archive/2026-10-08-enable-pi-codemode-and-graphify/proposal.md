## Why

The managed Pi configuration includes Chrome DevTools but does not enable the built-in CodeMode entry point its default browser capabilities require. The live configuration also includes `npm:graphify-pi` outside the managed package list, so a subsequent settings synchronization would remove that declaration.

## What Changes

- Declare `defaultTools: ["+codemode"]` in the managed Pi settings fragment to enable CodeMode without replacing Pi's normal default tools.
- Add `npm:graphify-pi` to the managed extension package list alongside all existing packages.
- Extend the configuration ownership contract to include the declared default tool selection while preserving unrelated Pi-owned settings and runtime artifacts.
- Reuse the existing settings merge mechanism; leave model preferences and Chrome DevTools exposure unchanged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `pi-configuration-sync`: Synchronize an additive CodeMode default tool declaration, retain Graphify in the managed extension catalog, and preserve settings outside the expanded owned key set.

## Impact

- Implementation is limited to `.chezmoitemplates/pi/settings.json` and focused regression coverage or verification using `run_after_merge-pi-settings.js.tmpl`.
- `~/.pi/agent/settings.json` receives the declarations on settings synchronization. `defaultTools` becomes repository-owned, and any host-specific value for that key is replaced by the managed declaration.
- Adds management of an already locally configured extension; no Pi upgrade, package version pin, or extension runtime synchronization is proposed.
- Chrome DevTools browser connectivity remains a separate runtime prerequisite, not a guarantee of enabling CodeMode.
