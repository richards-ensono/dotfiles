## Why

Pi mutates its global agent directory with package installations, mission/session state, permissions, and changelog metadata. Managing the whole directory through chezmoi causes every apply to overwrite Pi-owned state and leaves recurring drift, even though only the preferred models and extensions need to be synchronized.

## What Changes

- Manage Pi model selection and extension package declarations as a dedicated, stable chezmoi-managed configuration.
- Preserve Pi-owned runtime state, including installed package files, session and mission data, authentication/trust data, permissions, and changelog bookkeeping.
- Ensure repeated `chezmoi apply` operations converge without resetting Pi-owned state or producing expected configuration drift.

## Capabilities

### New Capabilities
- `pi-configuration-sync`: Synchronize only declarative Pi model and extension configuration through chezmoi while leaving Pi runtime state unmanaged.

### Modified Capabilities

- None.

## Impact

- Affects the Pi files currently managed under `dot_pi/agent/`, the chezmoi source layout, and apply behavior.
- Does not change Pi's provider authentication, installed runtime artifacts, skills, sessions, missions, or package installation behavior.
- May add a chezmoi apply script or template to merge the managed configuration with Pi's existing settings safely.
