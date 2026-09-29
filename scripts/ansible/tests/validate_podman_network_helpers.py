#!/usr/bin/env python3
"""Focused static checks for Podman network-helper provisioning safeguards."""
from pathlib import Path
import unittest

ROLE = Path(__file__).resolve().parents[1] / "roles" / "podman"
DEFAULTS = (ROLE / "defaults" / "main.yml").read_text(encoding="utf-8")
TASKS = (ROLE / "tasks" / "main.yml").read_text(encoding="utf-8")


class PodmanNetworkHelperProvisioningTests(unittest.TestCase):
    def test_successful_compatible_helper_provisioning(self) -> None:
        self.assertIn('netavark:\n      version: "2.1.0"', DEFAULTS)
        self.assertIn('aardvark-dns:\n      version: "2.1.0"', DEFAULTS)
        self.assertIn('dest: "{{ podman_network_helper_stage.path }}/{{ item.key }}.gz"', TASKS)
        self.assertIn('- "{{ podman_network_helper_directory }}/{{ item.key }}"', TASKS)
        self.assertIn("Download verified Podman network helper artifacts", TASKS)
        self.assertIn("Decompress verified Podman network helper artifacts", TASKS)
        self.assertIn("Verify installed Podman network helper versions", TASKS)

    def test_podman_compose_provider_is_installed(self) -> None:
        self.assertIn('podman_compose_package: "podman-compose"', DEFAULTS)
        self.assertIn('- "{{ podman_compose_package }}"', TASKS)

    def test_rootless_storage_uses_user_owned_locations(self) -> None:
        storage = TASKS.index("Configure rootless Podman storage")
        runtime_check = TASKS.index("Inspect active rootless Netavark helper")
        self.assertLess(storage, runtime_check)
        self.assertIn('dest: "{{ podman_user_home }}/.config/containers/storage.conf"', TASKS)
        self.assertIn('runroot = "/run/user/{{ podman_user_uid }}/containers"', TASKS)
        self.assertIn('graphroot = "{{ podman_user_home }}/.local/share/containers/storage"', TASKS)
        self.assertIn('mount_program = "/usr/bin/fuse-overlayfs"', TASKS)

    def test_rootless_lifecycle_skips_root_run_containers(self) -> None:
        lifecycle = TASKS.index("Validate rootless Podman network-helper lifecycle")
        environment = TASKS.index('XDG_RUNTIME_DIR: "/run/user/{{ podman_user_uid }}"')
        self.assertLess(lifecycle, environment)
        self.assertIn("when: podman_user_uid | int != 0", TASKS)

    def test_matching_components_skip_replacement_staging(self) -> None:
        self.assertIn(
            "Determine whether reviewed container-image configuration needs replacement", TASKS
        )
        self.assertIn("when: podman_container_image_configuration_needs_update", TASKS)
        self.assertIn(
            "Determine whether verified Podman network helpers need replacement", TASKS
        )
        self.assertIn("when: podman_network_helpers_need_update", TASKS)

    def test_existing_matching_helpers_are_preserved_until_validation(self) -> None:
        preserve = TASKS.index("Preserve existing managed Podman network helpers")
        stage = TASKS.index("Stage validated Podman network helper replacements")
        install = TASKS.index("Atomically install validated Podman network helper replacements")
        self.assertLess(preserve, stage)
        self.assertLess(stage, install)
        self.assertIn(".previous", TASKS)
        self.assertIn("Restore previously managed Podman network helpers", TASKS)

    def test_unsupported_architecture_fails_before_download(self) -> None:
        reject = TASKS.index("Reject unsupported Podman helper architecture")
        download = TASKS.index("Download verified Podman network helper artifacts")
        self.assertLess(reject, download)
        self.assertIn("refusing {{ ansible_architecture }} before download or replacement", TASKS)

    def test_artifact_checksum_mismatch_is_rejected(self) -> None:
        self.assertIn('checksum: "{{ item.value.checksum }}"', TASKS)
        self.assertIn("39fb540daf7578a793510b27b592b10f17b5d9aa3b07bc5c3f40881f12d590bd", DEFAULTS)
        self.assertIn("a7bc5252ee0e083f3f46d5bb9dc5f0abdbaa31a70a5a19012412dc8055ac2976", DEFAULTS)

    def test_failure_cleanup_removes_staging_and_keeps_existing_helpers(self) -> None:
        self.assertIn("always:\n    - name: Remove Podman network-helper staging directory", TASKS)
        self.assertIn("Existing managed helpers\n          were preserved or restored", TASKS)
        self.assertIn("Debian helper packages were not removed", TASKS)


if __name__ == "__main__":
    unittest.main()
