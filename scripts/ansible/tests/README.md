# Provisioning regression tests

Adapted from RichardSlater/dotfiles at `38b2df53dba253eeeb4cce38ddb039ef7febc051`, retaining the work repository's role APIs and provisioned versions.

## Offline checks

From the repository root, with Python 3.13, Ansible, Node.js and Chezmoi available:

```sh
python3 -m unittest discover -s scripts/ansible/tests -p 'test_source*.py' -v
python3 scripts/ansible/tests/validate_nvim_lock.py
python3 scripts/ansible/tests/validate_podman_sources.py
python3 scripts/ansible/tests/validate_podman_network_helpers.py
bash scripts/ansible/tests/test-staged-installers.sh
node --test scripts/ansible/tests/pi-settings.test.cjs
node scripts/ansible/tests/test-render.cjs
```

The installer suite invokes actual Ansible task fragments against temporary local payloads. It covers checksum/architecture rejection, bad archives, staged and activated version failures, existing recovery paths, partial activation, rollback, symlink refusal, ancillary payload retention, and build/install failures. .NET and Podman configuration also have no-change second-run assertions. Neovim/Podman build integration fixtures use tiny Makefiles to check DESTDIR behavior; they do not replace the real upstream source-build integration check.

Pi tests exercise preservation, managed-key precedence, restrictive writes, malformed input, repeat-run stability, write failures and detected concurrent updates. Symlink tests run on Linux; Windows skips them because creating symlinks requires host-specific privileges. The rendering test copies the source and config to temporary locations, performs no full apply, and executes only the Pi hook from a minimal isolated source. No real home or authentication file is touched. POSIX mode checks apply on Linux; Windows access protection inherits the destination directory's ACL, which these tests do not audit. Keep that directory private to the intended user.

CI installs current stable validation tools and immutable action references recorded in `docs/COMPONENT_VERSION_INVENTORY.md`. Linux and Windows rendering use verified Chezmoi release artifacts. To run the same Python tooling locally, install the versions listed in the workflow into a disposable virtual environment, not into the provisioned system environment.

## Broader integration

The existing `.vscode/test-ansible-idempotence.sh` provisions a disposable Debian container twice and preserves its security-tool availability checks. Run it through Docker, or Podman when Docker is unavailable:

```sh
podman run --rm -v "$PWD:/dotfiles:ro" docker.io/library/debian:bookworm \
  bash /dotfiles/.vscode/test-ansible-idempotence.sh
```

The GitHub workflow schedules this expensive check and exposes it through workflow_dispatch. Static/fixture success alone does not prove full source-build or full-playbook idempotence.

For a disposable provisioned Linux host with usable Podman namespaces:

```sh
DOTFILES_ISOLATED_TEST=1 bash scripts/ansible/tests/test-podman-network.sh
```

This creates, inspects and removes a uniquely named diagnostic network. It never prunes other resources. The repo does not provision a Compose provider, so the upstream Compose test is adapted to native Podman rather than introducing another tool. Restricted nested containers may lack the kernel/capability support to run this integration check; do not disable host security controls to force it through.

## Port validation record

Local validation of this port:

- 31 Python source/installer regressions passed with ansible-core 2.21.5.
- Pi unit tests: 14 passed on Linux; 13 passed and one symlink test skipped on Windows.
- Real Chezmoi rendering/interpreter/hook integration passed on both platforms, with isolated home, cache and persistent state.
- Full pre-commit, strict YAML lint, ShellCheck, actionlint, production Ansible lint and syntax checks passed. Linux static checks used an LF checkout-equivalent snapshot of the Windows source; `.gitattributes` preserves these line endings for future checkouts.
- A disposable Debian/Podman two-pass run completed with a recorded container exit code of 0. Second recap: `changed=0 unreachable=0 failed=0`. Existing security-tool execution checks passed. The full run began before final failure-path hardening; those later changes were rechecked by the final offline suite.
- The existing best-effort LazyVim sync was ignored on the container's first run, where the user editor config was not applied. Full plugin-download validation is not claimed.
- Native live Podman network integration was not run on a separate disposable provisioned host. Its opt-in script and static helper/source checks are provided; restricted nested environments are not treated as proof of rootless network compatibility.
- Hosted GitHub Actions have not run locally; the workflow is statically validated and will execute once pushed to an eligible branch/PR.

## PR merge validation

After merging `origin/main` at `99d4c7d`, the newer production pins, verified Podman network helpers/Compose provider, and Pi skills/model declarations were retained alongside the staged-install safeguards. Neovim fixtures explicitly use their synthetic version rather than depend on the production pin.

- 7 source-validator tests, 24 offline installer tests, and 10 Podman networking safeguard tests passed on Debian WSL.
- All 13 Pi settings/sandbox tests imported from main passed on Debian WSL.
- Pi unit tests passed: 14 on Linux; 13 on Windows with one symlink test skipped.
- Isolated Chezmoi rendering and hook execution passed on Linux and Windows.
- Full pre-commit, actionlint, production Ansible lint, and playbook syntax checks passed. The local linted sources were normalized to checkout-equivalent LF before running Linux checks.
- Full-system two-pass provisioning and live rootless network integration were not rerun for this merge.
- The existing `pi update --all` operation reports changes conservatively because its output is not a stable no-change API; full-playbook no-change claims do not apply to hosts with Pi installed.

## Recovery

Do not overwrite or automatically delete pre-existing `.ansible-backup` paths. If an installation fails during restoration, preserve the backup and inspect the failed task before manually recovering. Binary/runtime activation is recoverable but not a multi-file atomic swap; avoid concurrent provisioning.
