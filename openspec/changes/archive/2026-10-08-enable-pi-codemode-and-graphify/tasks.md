## 1. Update managed Pi declarations

- [x] 1.1 Confirm current Pi additive tool-selection support and verify `graphify-pi` package identity and runtime compatibility against the authoritative npm registry before any dependency installation or upgrade; preserve the existing unpinned Pi package declaration convention.
- [x] 1.2 Add top-level `"defaultTools": ["+codemode"]` to `.chezmoitemplates/pi/settings.json` without changing model preferences or CodeMode presentation mode.
- [x] 1.3 Add `"npm:graphify-pi"` exactly once to the managed `packages` array, preserving all pre-existing package entries and their order.
- [x] 1.4 Parse the managed fragment as JSON and verify that only `defaultTools` and the intended package-list addition differ from the pre-change fragment.

## 2. Verify settings synchronization in isolation

- [x] 2.1 Add focused regression coverage using the rendered `run_after_merge-pi-settings.js.tmpl` with an isolated temporary home; cover missing settings, absent or differing `defaultTools`, and both absent and already-present Graphify declarations.
- [x] 2.2 Verify preservation of model preferences, all existing managed packages, theme, changelog metadata, unknown top-level settings, unknown subagent settings, runtime artifact sentinels, and existing agent-directory permissions.
- [x] 2.3 Verify repeated synchronization is idempotent and malformed existing JSON causes a failure without modifying the original settings file.
- [x] 2.4 Run focused checks in the repository's required sandbox, followed by applicable JSON/style and pre-commit checks; report actual outcomes without changing the operator's live settings or unrelated files.

## 3. Verify rollout readiness and runtime boundaries

- [x] 3.1 Preview the targeted Pi settings synchronization and document expected replacement of machine-local `defaultTools`, along with the explicit live-key restoration needed for rollback.
- [x] 3.2 Confirm CodeMode activation and Graphify package loading in a safe test session if available; if live settings synchronization is needed, obtain operator approval and apply only the Pi settings mechanism.
- [x] 3.3 Using a clean, non-sensitive browser session if available, verify CodeMode can discover `chrome_devtools_*`, inspect a tool schema, and perform a read-only page-list call; otherwise explicitly document the unverified runtime boundary and reason without claiming integration success.
- [x] 3.4 Validate the OpenSpec change and review the final diff to confirm that settings declarations and focused coverage are the only implementation changes.

## Verification notes

- Registry verification: `https://registry.npmjs.org/graphify-pi` reports latest stable `0.3.0`, Node `>=20`, and a Pi extension/skill manifest. Installed Node is `26.4.0`; Pi `1.1.0` documents additive default tool selection and maps the legacy Pi peer import name. No dependencies were installed or upgraded.
- Six focused Python regression tests passed using the actual chezmoi-rendered merge script inside Bubblewrap, with networking disabled, read-only staged public files and Node toolchain, synthetic temporary homes, and no credential or socket mounts. JSON, JavaScript, and Python syntax checks passed. Scoped pre-commit checks passed; the hook is already installed.
- Targeted preview passed: `chezmoi apply --dry-run --verbose --refresh-externals=never --include=scripts --source-path run_after_merge-pi-settings.js.tmpl`. Only the settings merge script was previewed; no live synchronization was performed.
- Offline runtime smoke passed in Bubblewrap: Pi's SDK activated `codemode` while retaining `read`, `bash`, `edit`, and `write`; an isolated copy of installed Graphify `0.3.0` resolved through `npm:graphify-pi` and registered `/graphify` without extension-load errors. No model request, installation, live settings modification, or browser connection occurred. Other configured packages were deliberately excluded from this safe smoke session.
- `openspec validate enable-pi-codemode-and-graphify --strict` and `git diff --check` passed. Final scope review confirms implementation changes are limited to the managed settings fragment and `scripts/tests/test_pi_settings_sync.py`; the merge script is unchanged. The pre-existing Neovim modification was not edited.
- Browser integration remains **unverified**: this session exposes no `chrome_devtools_*` tools, and no clean, non-sensitive browser profile/endpoint was established for testing. No existing browser was contacted. CodeMode discovery of browser capabilities, browser-tool schema inspection, and a read-only page-list call were not run; activation and Graphify loading do not prove browser connectivity. Repeat these checks in a fresh session connected to a clean test browser after an approved targeted synchronization.
- Ownership/rollback: synchronization replaces machine-local `defaultTools` with `["+codemode"]`. Revert the Graphify addition and managed `defaultTools` declaration to roll back, then explicitly restore the previous live `defaultTools` value or remove the live key if previously absent. Removing the managed key alone leaves it in live settings because the merge preserves unowned keys. Runtime files need not be deleted.
