"""Offline tests run actual Ansible task fragments against disposable fixtures.

No system build, package installation, network download, or real home is used.
Build integration remains the scheduled/manual full-provisioning check.
"""
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ANSIBLE = shutil.which("ansible-playbook")


@unittest.skipUnless(ANSIBLE, "ansible-playbook is required")
class StagedInstallers(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="staged-install-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def executable(self, path, body):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/bin/sh\n" + body + "\n")
        path.chmod(0o755)

    def run_role(self, name, variables, tasks_from="main", success=True, environment=None):
        play = [{"name": "Offline staged installation fixture", "hosts": "localhost",
                 "gather_facts": False, "tasks": [
                     {"name": "Exercise actual role fragment", "ansible.builtin.include_role":
                      {"name": name, "tasks_from": tasks_from}}]}]
        if environment:
            play[0]["environment"] = environment
        play_file = self.root / "fixture.json"
        play_file.write_text(json.dumps(play))
        vars_file = self.root / "variables.json"
        # Fixture binaries report a synthetic version independent of production pins.
        fixture_versions = {"neovim_version": "v0.12.4"} if name == "neovim" else {}
        vars_file.write_text(json.dumps({"ansible_become": False, **fixture_versions, **variables}))
        env = {**os.environ, "ANSIBLE_ROLES_PATH": str(ROOT / "scripts/ansible/roles"),
               "ANSIBLE_LOCAL_TEMP": str(self.root / "ansible-local"),
               "ANSIBLE_REMOTE_TEMP": str(self.root / "ansible-remote"),
               "ANSIBLE_NOCOLOR": "1"}
        result = subprocess.run([ANSIBLE, "-i", "localhost,", "-c", "local", str(play_file),
                                 "--extra-vars", "@" + str(vars_file)],
                                cwd=self.root, env=env, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode == 0, success, result.stdout[-6000:] + result.stderr[-2000:])
        return result.stdout

    def dotnet_fixture(self, body="echo fixture-sdk", installed=True):
        install = self.root / "dotnet"
        if installed:
            self.executable(install / "dotnet", "echo previous-sdk")
            (install / "previous.txt").write_text("preserve me")
        payload = self.root / "payload"
        self.executable(payload / "dotnet", body)
        archive = self.root / "sdk.tar.gz"
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(payload / "dotnet", arcname="dotnet")
        return install, {"ansible_architecture": "x86_64", "dotnet_sdk_version": "fixture-sdk",
                         "dotnet_install_dir": str(install), "dotnet_download_url": archive.as_uri(),
                         "dotnet_checksum": "sha256:" + hashlib.sha256(archive.read_bytes()).hexdigest()}

    def assert_dotnet_preserved(self, install):
        self.assertEqual((install / "previous.txt").read_text(), "preserve me")
        self.assertIn("previous-sdk", (install / "dotnet").read_text())
        self.assertFalse(list(self.root.glob(".dotnet-stage-*")))

    def test_dotnet_success_and_no_change_second_run(self):
        install, variables = self.dotnet_fixture()
        install.chmod(0o700)
        self.run_role("dotnet", variables)
        self.assertEqual(install.stat().st_mode & 0o777, 0o700)
        self.assertEqual((install / "previous.txt").read_text(), "preserve me")
        self.assertIn("fixture-sdk", (install / "dotnet").read_text())
        self.assertFalse(Path(str(install) + ".ansible-backup").exists())
        self.assertRegex(self.run_role("dotnet", variables), r"changed=0\s")

    def test_dotnet_unsupported_architecture(self):
        install, variables = self.dotnet_fixture()
        variables["ansible_architecture"] = "unsupported-fixture"
        self.run_role("dotnet", variables, success=False)
        self.assert_dotnet_preserved(install)

    def test_dotnet_checksum_rejection(self):
        install, variables = self.dotnet_fixture()
        variables["dotnet_checksum"] = "sha256:" + "0" * 64
        self.run_role("dotnet", variables, success=False)
        self.assert_dotnet_preserved(install)

    def test_dotnet_staged_version_rejection(self):
        install, variables = self.dotnet_fixture("echo unexpected-sdk")
        self.run_role("dotnet", variables, success=False)
        self.assert_dotnet_preserved(install)

    def test_dotnet_active_verification_rollback(self):
        install, variables = self.dotnet_fixture('case "$0" in */payload/dotnet) echo fixture-sdk ;; *) echo unexpected-sdk ;; esac')
        self.run_role("dotnet", variables, success=False)
        self.assert_dotnet_preserved(install)
        self.assertFalse(Path(str(install) + ".ansible-backup").exists())

    def test_dotnet_failure_without_previous_installation(self):
        install, variables = self.dotnet_fixture('case "$0" in */payload/dotnet) echo fixture-sdk ;; *) exit 1 ;; esac', installed=False)
        self.run_role("dotnet", variables, success=False)
        self.assertFalse(install.exists())
        self.assertFalse(list(self.root.glob(".dotnet-stage-*")))

    def test_dotnet_partial_failed_activation_without_previous_state(self):
        install, variables = self.dotnet_fixture(installed=False)
        fakebin = self.root / "fakebin"
        self.executable(fakebin / "mv", 'case "$2" in */payload) mkdir -p "$3"; echo partial > "$3/partial.txt"; exit 1 ;; *) exec /bin/mv "$@" ;; esac')
        self.run_role("dotnet", variables, success=False,
                      environment={"PATH": str(fakebin) + ":" + os.environ["PATH"]})
        self.assertFalse(install.exists())
        self.assertFalse(list(self.root.glob(".dotnet-stage-*")))

    def test_dotnet_recovery_collision(self):
        install, variables = self.dotnet_fixture()
        recovery = Path(str(install) + ".ansible-backup")
        recovery.mkdir()
        (recovery / "pending.txt").write_text("do not overwrite")
        self.run_role("dotnet", variables, success=False)
        self.assert_dotnet_preserved(install)
        self.assertEqual((recovery / "pending.txt").read_text(), "do not overwrite")

    def test_dotnet_invalid_archive(self):
        install, variables = self.dotnet_fixture()
        archive = self.root / "sdk.tar.gz"
        archive.write_bytes(b"not an archive")
        variables["dotnet_checksum"] = "sha256:" + hashlib.sha256(archive.read_bytes()).hexdigest()
        self.run_role("dotnet", variables, success=False)
        self.assert_dotnet_preserved(install)

    def neovim_fixture(self, broken=False, missing_runtime=False):
        install = self.root / "nvim-prefix"
        stage = self.root / "nvim-stage"
        staged_prefix = stage / str(install).lstrip("/")
        self.executable(install / "bin/nvim", "echo previous-nvim")
        (install / "share/nvim/runtime").mkdir(parents=True)
        (install / "share/nvim/runtime/previous.txt").write_text("old runtime")
        self.executable(staged_prefix / "bin/nvim", 'if [ "$1" = --version ]; then echo "NVIM v0.12.4"; else ' + ("exit 1" if broken else "exit 0") + '; fi')
        if not missing_runtime:
            (staged_prefix / "share/nvim/runtime").mkdir(parents=True)
            (staged_prefix / "share/nvim/runtime/new.txt").write_text("new runtime")
        for prefix, text in [(install, "old manual"), (staged_prefix, "new manual")]:
            (prefix / "share/man/man1").mkdir(parents=True)
            (prefix / "share/man/man1/nvim.1").write_text(text)
        return install, {"neovim_install_dir": str(install), "neovim_stage": {"path": str(stage)}}

    def assert_neovim_preserved(self, install):
        self.assertIn("previous-nvim", (install / "bin/nvim").read_text())
        self.assertEqual((install / "share/nvim/runtime/previous.txt").read_text(), "old runtime")
        self.assertFalse((install / "bin/nvim.ansible-backup").exists())
        self.assertFalse((install / "share/nvim.ansible-backup").exists())
        self.assertEqual((install / "share/man/man1/nvim.1").read_text(), "old manual")

    def test_neovim_binary_and_runtime_success(self):
        install, variables = self.neovim_fixture()
        self.run_role("neovim", variables, "activate-staged")
        self.assertTrue((install / "share/nvim/runtime/new.txt").exists())
        self.assertFalse((install / "share/nvim/runtime/previous.txt").exists())
        self.assertEqual((install / "share/man/man1/nvim.1").read_text(), "new manual")
        self.assertFalse((install / "bin/nvim.ansible-backup").exists())

    def test_neovim_clean_startup_rollback(self):
        install, variables = self.neovim_fixture(broken=True)
        self.run_role("neovim", variables, "activate-staged", success=False)
        self.assert_neovim_preserved(install)

    def test_neovim_partial_activation_rollback(self):
        install, variables = self.neovim_fixture(missing_runtime=True)
        self.run_role("neovim", variables, "activate-staged", success=False)
        self.assert_neovim_preserved(install)

    def test_neovim_recovery_collision(self):
        install, variables = self.neovim_fixture()
        recovery = install / "share/nvim.ansible-backup"
        recovery.mkdir()
        (recovery / "pending.txt").write_text("pending")
        self.run_role("neovim", variables, "activate-staged", success=False)
        self.assertIn("previous-nvim", (install / "bin/nvim").read_text())
        self.assertEqual((recovery / "pending.txt").read_text(), "pending")

    def test_neovim_staging_uses_destdir_and_staged_runtime(self):
        install, variables = self.neovim_fixture()
        build = self.root / "nvim-build"
        build.mkdir()
        staged_prefix = Path(variables["neovim_stage"]["path"]) / str(install).lstrip("/")
        shutil.copytree(staged_prefix, build / "payload")
        self.executable(build / "payload/bin/nvim",
                        'if [ "$1" = --version ]; then echo "NVIM v0.12.4"; else '
                        f'test -f "${{VIMRUNTIME:-{install}/share/nvim/runtime}}/new.txt"; fi')
        (build / "Makefile").write_text(f'PREFIX={install}\ninstall:\n\tmkdir -p "$(DESTDIR)$(PREFIX)"\n\tcp -a payload/. "$(DESTDIR)$(PREFIX)/"\n')
        self.run_role("neovim", {"neovim_install_dir": str(install), "neovim_dest": str(build)}, "install-staged")
        self.assertTrue((install / "share/nvim/runtime/new.txt").exists())
        self.assertEqual((install / "share/man/man1/nvim.1").read_text(), "new manual")
        self.assertFalse(list(install.glob(".nvim-stage-*")))

    def test_neovim_build_install_failure_preserves_existing_payload(self):
        install, _ = self.neovim_fixture()
        build = self.root / "nvim-build"
        build.mkdir()
        (build / "Makefile").write_text('install:\n\tfalse\n')
        self.run_role("neovim", {"neovim_install_dir": str(install), "neovim_dest": str(build)}, "install-staged", success=False)
        self.assert_neovim_preserved(install)
        self.assertFalse(list(install.glob(".nvim-stage-*")))

    def podman_fixture(self, broken=False):
        install = self.root / "podman-prefix"
        stage = self.root / "podman-stage"
        self.executable(install / "bin/podman", "echo previous-podman")
        self.executable(stage / str(install).lstrip("/") / "bin/podman",
                        "echo " + ("unexpected" if broken else "podman version 6.1.0"))
        staged_prefix = stage / str(install).lstrip("/")
        self.executable(install / "libexec/podman/rootlessport", "echo old-helper")
        self.executable(staged_prefix / "libexec/podman/rootlessport", "echo new-helper")
        (install / "bin/podmansh").symlink_to("podman")
        (staged_prefix / "bin/podmansh").symlink_to("podman")
        return install, {"podman_install_dir": str(install), "podman_stage": {"path": str(stage)},
                         "podman_expected_version": "6.1.0"}

    def test_podman_binary_success(self):
        install, variables = self.podman_fixture()
        self.run_role("podman", variables, "activate-staged")
        self.assertIn("podman version 6.1.0", (install / "bin/podman").read_text())
        self.assertIn("new-helper", (install / "libexec/podman/rootlessport").read_text())
        self.assertTrue((install / "bin/podmansh").is_symlink())
        self.assertFalse((install / "bin/podman.ansible-backup").exists())

    def test_podman_binary_rollback(self):
        install, variables = self.podman_fixture(broken=True)
        self.run_role("podman", variables, "activate-staged", success=False)
        self.assertIn("previous-podman", (install / "bin/podman").read_text())
        self.assertIn("old-helper", (install / "libexec/podman/rootlessport").read_text())
        self.assertTrue((install / "bin/podmansh").is_symlink())
        self.assertFalse((install / "bin/podman.ansible-backup").exists())

    def test_podman_build_staging_retains_ancillary_helpers(self):
        install, variables = self.podman_fixture()
        staged_prefix = Path(variables["podman_stage"]["path"]) / str(install).lstrip("/")
        build = self.root / "podman-build"
        build.mkdir()
        shutil.copytree(staged_prefix, build / "payload", symlinks=True)
        (build / "Makefile").write_text('all:\n\ttrue\ninstall:\n\tmkdir -p "$(DESTDIR)$(PREFIX)"\n\tcp -a payload/. "$(DESTDIR)$(PREFIX)/"\n')
        self.run_role("podman", {"podman_install_dir": str(install), "podman_build_dir": str(build),
                                 "podman_expected_version": "6.1.0", "ansible_env": {"PATH": os.environ["PATH"]}}, "install-staged")
        self.assertIn("new-helper", (install / "libexec/podman/rootlessport").read_text())
        self.assertTrue((install / "bin/podmansh").is_symlink())
        self.assertFalse(list(install.glob(".podman-stage-*")))

    def test_podman_failed_build_preserves_existing_payload(self):
        install, _ = self.podman_fixture()
        build = self.root / "podman-build"
        build.mkdir()
        (build / "Makefile").write_text('all:\n\tfalse\n')
        self.run_role("podman", {"podman_install_dir": str(install), "podman_build_dir": str(build),
                                 "podman_expected_version": "6.1.0", "ansible_env": {"PATH": os.environ["PATH"]}}, "install-staged", success=False)
        self.assertIn("previous-podman", (install / "bin/podman").read_text())
        self.assertIn("old-helper", (install / "libexec/podman/rootlessport").read_text())
        self.assertFalse(list(install.glob(".podman-stage-*")))

    def configuration_fixture(self, invalid=False):
        destination = self.root / "containers"
        destination.mkdir()
        (destination / "policy.json").write_text('{"default":[{"type":"reject"}]}')
        (destination / "registries.conf").write_text('unqualified-search-registries = ["previous"]\n')
        sources = self.root / "config-sources"
        sources.mkdir()
        (sources / "policy.json").write_text("invalid-json" if invalid else '{"default":[{"type":"insecureAcceptAnything"}]}')
        (sources / "registries.conf").write_text('unqualified-search-registries = ["fixture"]\n')
        variables = {"podman_config_dir": str(destination),
                     "podman_policy_source_url": (sources / "policy.json").as_uri(),
                     "podman_registries_source_url": (sources / "registries.conf").as_uri()}
        return destination, sources, variables

    def test_podman_configuration_success_and_idempotence(self):
        destination, sources, variables = self.configuration_fixture()
        self.run_role("podman", variables, "install-configuration")
        self.assertEqual((destination / "policy.json").read_bytes(), (sources / "policy.json").read_bytes())
        self.assertRegex(self.run_role("podman", variables, "install-configuration"), r"changed=0\s")

    def test_podman_invalid_json_preserves_configuration(self):
        destination, _, variables = self.configuration_fixture(invalid=True)
        original = (destination / "policy.json").read_bytes()
        self.run_role("podman", variables, "install-configuration", success=False)
        self.assertEqual((destination / "policy.json").read_bytes(), original)
        self.assertFalse(list(destination.glob(".podman-config-*")))

    def test_podman_invalid_toml_preserves_configuration(self):
        destination, sources, variables = self.configuration_fixture()
        original = (destination / "policy.json").read_bytes()
        (sources / "registries.conf").write_text("invalid [ toml")
        self.run_role("podman", variables, "install-configuration", success=False)
        self.assertEqual((destination / "policy.json").read_bytes(), original)

    def test_podman_configuration_activation_rollback(self):
        destination, sources, variables = self.configuration_fixture(invalid=True)
        original_policy = (destination / "policy.json").read_bytes()
        original_registries = (destination / "registries.conf").read_bytes()
        variables["podman_configuration_stage"] = {"path": str(sources)}
        self.run_role("podman", variables, "activate-configuration", success=False)
        self.assertEqual((destination / "policy.json").read_bytes(), original_policy)
        self.assertEqual((destination / "registries.conf").read_bytes(), original_registries)
        self.assertFalse(list(destination.glob("*.ansible-backup")))

    def test_symlink_destination_rejected_without_mutation(self):
        install, variables = self.podman_fixture()
        target = install / "bin/podman"
        target.rename(self.root / "outside")
        target.symlink_to(self.root / "outside")
        self.run_role("podman", variables, "activate-staged", success=False)
        self.assertTrue(target.is_symlink())
        self.assertIn("previous-podman", (self.root / "outside").read_text())


if __name__ == "__main__":
    unittest.main()
