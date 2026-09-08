## 1. Select and Configure the Release

- [x] 1.1 Query the authoritative npm registry for the current stable pnpm 12 release and record the selected exact version for this change.
- [x] 1.2 Update `scripts/ansible/roles/pnpm/defaults/main.yml` to pin that exact pnpm 12 version while retaining the existing installer URL, `PNPM_HOME`, and executable path.
- [x] 1.3 Update `scripts/ansible/roles/pnpm/README.md` and `docs/COMPONENT_VERSION_INVENTORY.md` so their selected version and documented installer verification exception match the role configuration.

## 2. Validate Provisioning Behavior

- [x] 2.1 Run the narrow Ansible syntax/lint validation applicable to the modified pnpm role and resolve any findings without weakening validation.
- [x] 2.2 Provision pnpm into an isolated `PNPM_HOME` using the role's versioned installer path, then verify `pnpm --version` reports the selected release.
- [x] 2.3 Repeat the relevant provisioning check and verify the matching version does not trigger a reinstall; if configured, confirm global package lifecycle behavior remains intact.

## 3. Run Repository Checks

- [x] 3.1 Run the repository's relevant broader validation and `pre-commit` checks for the changed Ansible and Markdown files; report any environment-limited checks or remaining risks.
