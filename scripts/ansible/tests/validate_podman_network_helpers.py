#!/usr/bin/env python3
"""Focused static checks for Podman network-helper provisioning safeguards."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[3]


class PodmanNetworkHelperProvisioningTests(unittest.TestCase):
    root = ROOT

    def setUp(self):
        role = self.root / "scripts/ansible/roles/podman"
        self.defaults = (role / "defaults/main.yml").read_text(encoding="utf-8")
        self.tasks = "\n".join(
            file.read_text(encoding="utf-8") for file in sorted((role / "tasks").glob("*.yml"))
        )
        self.variables = (role / "vars/main.yml").read_text(encoding="utf-8")

    def test_rootless_handler_package_mapping_is_preserved(self):
        self.assertIn("podman_package_map[podman_network_handler]", self.tasks)
        self.assertIn('pasta: "passt"', self.variables)
        self.assertIn('slirp4netns: "slirp4netns"', self.variables)
    def test_successful_compatible_helper_provisioning(self) -> None:
        self.assertIn('netavark:\n      version: "2.1.0"', self.defaults)
        self.assertIn('aardvark-dns:\n      version: "2.1.0"', self.defaults)
        self.assertIn('dest: "{{ podman_network_helper_stage.path }}/{{ item.key }}.gz"', self.tasks)
        self.assertIn('- "{{ podman_network_helper_directory }}/{{ item.key }}"', self.tasks)
        self.assertIn("Download verified Podman network helper artifacts", self.tasks)
        self.assertIn("Decompress verified Podman network helper artifacts", self.tasks)
        self.assertIn("Verify installed Podman network helper versions", self.tasks)

    def test_podman_compose_provider_is_installed(self) -> None:
        self.assertIn('podman_compose_package: "podman-compose"', self.defaults)
        self.assertIn('- "{{ podman_compose_package }}"', self.tasks)

    def test_rootless_storage_uses_user_owned_locations(self) -> None:
        storage = self.tasks.index("Configure rootless Podman storage")
        runtime_check = self.tasks.index("Inspect active rootless Netavark helper")
        self.assertLess(storage, runtime_check)
        self.assertIn('dest: "{{ podman_user_home }}/.config/containers/storage.conf"', self.tasks)
        self.assertIn('runroot = "/run/user/{{ podman_user_uid }}/containers"', self.tasks)
        self.assertIn('graphroot = "{{ podman_user_home }}/.local/share/containers/storage"', self.tasks)
        self.assertIn('mount_program = "/usr/bin/fuse-overlayfs"', self.tasks)

    def test_rootless_lifecycle_skips_root_run_containers(self) -> None:
        lifecycle = self.tasks.index("Validate rootless Podman network-helper lifecycle")
        environment = self.tasks.index('XDG_RUNTIME_DIR: "/run/user/{{ podman_user_uid }}"')
        self.assertLess(lifecycle, environment)
        self.assertIn("when: podman_user_uid | int != 0", self.tasks)

    def test_matching_components_skip_replacement_staging(self) -> None:
        self.assertIn(
            "Determine whether reviewed container-image configuration needs replacement", self.tasks
        )
        self.assertIn("when: podman_container_image_configuration_needs_update", self.tasks)
        self.assertIn(
            "Determine whether verified Podman network helpers need replacement", self.tasks
        )
        self.assertIn("when: podman_network_helpers_need_update", self.tasks)

    def test_existing_matching_helpers_are_preserved_until_validation(self) -> None:
        preserve = self.tasks.index("Preserve existing managed Podman network helpers")
        stage = self.tasks.index("Stage validated Podman network helper replacements")
        install = self.tasks.index("Atomically install validated Podman network helper replacements")
        self.assertLess(preserve, stage)
        self.assertLess(stage, install)
        self.assertIn(".previous", self.tasks)
        self.assertIn("Restore previously managed Podman network helpers", self.tasks)

    def test_unsupported_architecture_fails_before_download(self) -> None:
        reject = self.tasks.index("Reject unsupported Podman helper architecture")
        download = self.tasks.index("Download verified Podman network helper artifacts")
        self.assertLess(reject, download)
        self.assertIn("refusing {{ ansible_architecture }} before download or replacement", self.tasks)

    def test_artifact_checksum_mismatch_is_rejected(self) -> None:
        self.assertIn('checksum: "{{ item.value.checksum }}"', self.tasks)
        self.assertIn("39fb540daf7578a793510b27b592b10f17b5d9aa3b07bc5c3f40881f12d590bd", self.defaults)
        self.assertIn("a7bc5252ee0e083f3f46d5bb9dc5f0abdbaa31a70a5a19012412dc8055ac2976", self.defaults)

    def test_failure_cleanup_removes_staging_and_keeps_existing_helpers(self) -> None:
        self.assertIn("always:\n    - name: Remove Podman network-helper staging directory", self.tasks)
        self.assertIn("Existing managed helpers\n          were preserved or restored", self.tasks)
        self.assertIn("Debian helper packages were not removed", self.tasks)


def validate(root):
    class RepositoryTests(PodmanNetworkHelperProvisioningTests):
        pass

    RepositoryTests.root = root
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(RepositoryTests)
    result = unittest.TestResult()
    suite.run(result)
    return [f"{test.id()}: {detail.splitlines()[-1]}"
            for test, detail in result.failures + result.errors]


if __name__ == "__main__":
    unittest.main()
