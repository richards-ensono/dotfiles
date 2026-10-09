"""Failure cases for the validators; do not edit the real source tree."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

import validate_nvim_lock
import validate_podman_sources
import validate_podman_network_helpers

ROOT = Path(__file__).resolve().parents[3]


class SourceValidators(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for relative in [".chezmoitemplates/nvim", "scripts/ansible/roles/podman"]:
            shutil.copytree(ROOT / relative, self.root / relative)

    def test_valid_repository(self):
        for validator in [validate_nvim_lock, validate_podman_sources, validate_podman_network_helpers]:
            self.assertEqual(validator.validate(self.root), [])

    def test_plugin_drift(self):
        file = self.root / ".chezmoitemplates/nvim/lazy-lock.json"
        lock = json.loads(file.read_text())
        lock["copilot.vim"]["commit"] = "0" * 40
        file.write_text(json.dumps(lock))
        self.assertTrue(validate_nvim_lock.validate(self.root))

    def test_bootstrap_drift(self):
        file = self.root / ".chezmoitemplates/nvim/lazy-lock.json"
        lock = json.loads(file.read_text())
        lock["lazy.nvim"]["commit"] = "0" * 40
        file.write_text(json.dumps(lock))
        self.assertTrue(validate_nvim_lock.validate(self.root))

    def test_lock_is_not_object(self):
        file = self.root / ".chezmoitemplates/nvim/lazy-lock.json"
        file.write_text("[]")
        self.assertTrue(validate_nvim_lock.validate(self.root))

    def test_mutable_configuration_url(self):
        file = self.root / "scripts/ansible/roles/podman/defaults/main.yml"
        file.write_text(file.read_text().replace("{{ podman_containers_image_ref }}", "main"))
        self.assertTrue(validate_podman_sources.validate(self.root))

    def test_mutable_source_commit(self):
        file = self.root / "scripts/ansible/roles/podman/vars/main.yml"
        file.write_text(file.read_text().replace('podman_source_commit: "cade97a52ebdf9dbf9e81de8009015776837a074"', 'podman_source_commit: "main"'))
        self.assertTrue(validate_podman_sources.validate(self.root))

    def test_network_helper_removed(self):
        file = self.root / "scripts/ansible/roles/podman/tasks/main.yml"
        file.write_text(file.read_text().replace("      - netavark\n", ""))
        self.assertTrue(validate_podman_network_helpers.validate(self.root))


if __name__ == "__main__":
    unittest.main()
