## 1. Define the managed Pi configuration

- [x] 1.1 Inspect existing chezmoi conventions and select a portable JSON merge mechanism available on supported targets.
- [x] 1.2 Replace the direct Pi `settings.json` mapping with a dedicated source fragment containing only the owned model and `packages` keys.
- [x] 1.3 Document the owned settings boundary so future changes do not add Pi runtime metadata to the fragment.

## 2. Implement safe synchronization

- [x] 2.1 Add an idempotent chezmoi apply mechanism that creates or field-merges `~/.pi/agent/settings.json` from the owned fragment.
- [x] 2.2 Validate the existing target JSON before replacement and use an atomic write so invalid input leaves the original settings file intact.
- [x] 2.3 Remove the managed directory mapping for `~/.pi/agent` while preserving deployment of the owned configuration fragment and merge mechanism.

## 3. Verify behavior

- [x] 3.1 Test applying to an existing settings file with Pi-owned metadata and confirm the metadata remains unchanged while owned model and extension keys converge.
- [x] 3.2 Test applying when Pi settings are absent and confirm valid settings are created.
- [x] 3.3 Test invalid existing JSON and confirm apply fails without changing the target file.
- [x] 3.4 Run `chezmoi apply` twice and verify the second apply leaves Pi runtime files, directory permissions, and settings unchanged.
