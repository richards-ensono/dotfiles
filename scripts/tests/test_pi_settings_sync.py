#!/usr/bin/env python3
"""Regression coverage for the rendered Pi settings merge script.

For sandboxed execution, render the template on the host first and set
PI_SETTINGS_SYNC_SCRIPT to that file's path. Otherwise chezmoi renders it here.
Every merge runs with a synthetic temporary HOME, never the operator's home.
"""
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
FRAGMENT = ROOT / ".chezmoitemplates/pi/settings.json"
TEMPLATE = ROOT / "run_after_merge-pi-settings.js.tmpl"
GRAPHIFY = "npm:graphify-pi"


class PiSettingsSyncTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.managed = json.loads(FRAGMENT.read_text(encoding="utf-8"))
        cls.node = shutil.which("node")
        if cls.node is None:
            raise RuntimeError("node is required for Pi settings synchronization tests")
        supplied_script = os.environ.get("PI_SETTINGS_SYNC_SCRIPT")
        if supplied_script:
            cls.rendered = Path(supplied_script).read_text(encoding="utf-8")
        else:
            cls.rendered = subprocess.run(
                ["chezmoi", "execute-template", "--config", "/dev/null",
                 "--config-format", "toml", "--source", str(ROOT)],
                input=TEMPLATE.read_text(encoding="utf-8"), capture_output=True,
                text=True, check=True, timeout=30,
            ).stdout

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="pi-settings-sync-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.agent = self.home / ".pi/agent"
        self.settings = self.agent / "settings.json"
        self.script = self.root / "merge.js"
        # The hook follows Chezmoi's explicit destination, not the process HOME.
        rendered = re.sub(r"^const destination = .*;$",
                          lambda _: f"const destination = {json.dumps(str(self.home))};",
                          self.rendered, count=1, flags=re.MULTILINE)
        self.script.write_text(rendered, encoding="utf-8")
        self.env = {"HOME": str(self.home), "PATH": os.environ.get("PATH", "")}

    def write_settings(self, value):
        self.agent.mkdir(parents=True, exist_ok=True)
        self.settings.write_text(json.dumps(value) + "\n", encoding="utf-8")

    def run_merge(self):
        return subprocess.run(
            [self.node, str(self.script)], cwd=self.home, env=self.env,
            capture_output=True, text=True, timeout=15,
        )

    def assert_merge_succeeds(self):
        result = self.run_merge()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(list(self.agent.glob(".settings.json.chezmoi-*")))
        return json.loads(self.settings.read_text(encoding="utf-8"))

    def test_managed_declarations(self):
        self.assertEqual(self.managed["defaultTools"], ["+codemode"])
        self.assertNotIn("codemode", self.managed)
        self.assertEqual(self.managed["packages"].count(GRAPHIFY), 1)
        self.assertEqual(self.managed["packages"][:-1], [
            "git:github.com/richards-ensono/pi-openspec-status",
            "npm:@juicesharp/rpiv-ask-user-question",
            "npm:@juicesharp/rpiv-todo",
            "npm:@narumitw/pi-usage",
            "npm:@narumitw/pi-chrome-devtools",
            "npm:@tmustier/pi-usage-extension",
            "npm:context-mode",
            "npm:pi-simplify",
            "npm:pi-subagents",
            "npm:pi-web-access",
        ])

    def test_missing_settings_are_created(self):
        self.assertFalse(self.settings.exists())
        self.assertEqual(self.assert_merge_succeeds(), self.managed)
        self.assertEqual(self.agent.stat().st_mode & 0o777, 0o700)

    def test_existing_default_tools_and_graphify_are_replaced(self):
        for default_tools in (None, ["read"], ["+codemode"]):
            for has_graphify in (False, True):
                with self.subTest(default_tools=default_tools, has_graphify=has_graphify):
                    existing = {"packages": ["npm:local-only-fixture"]}
                    if has_graphify:
                        existing["packages"].append(GRAPHIFY)
                    if default_tools is not None:
                        existing["defaultTools"] = default_tools
                    self.write_settings(existing)
                    merged = self.assert_merge_succeeds()
                    self.assertEqual(merged, self.managed)
                    self.assertEqual(merged["packages"].count(GRAPHIFY), 1)

    def test_unowned_settings_runtime_files_and_permissions_are_preserved(self):
        existing = {
            "defaultProvider": "fixture-provider",
            "defaultModel": "fixture-model",
            "defaultThinkingLevel": "off",
            "enabledModels": ["fixture-provider/fixture-model"],
            "defaultTools": ["read"],
            "packages": [GRAPHIFY, "npm:local-only-fixture"],
            "theme": "fixture-theme",
            "lastChangelogVersion": "fixture-version",
            "unknownSetting": {"nested": [False, "fixture-value"]},
            "codemode": {"mode": "on", "inlineBudget": 123},
            "subagents": {"defaultModel": "fixture-model", "unknownPreference": [1, 2]},
        }
        self.write_settings(existing)
        self.agent.chmod(0o750)
        sentinels = {}
        for relative in (
            "sessions/fixture.jsonl", "missions/fixture.json", "trust.json",
            "npm/node_modules/fixture/index.js", "cache/fixture.bin", "auth.json",
        ):
            target = self.agent / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"synthetic-runtime-sentinel\x00\n")
            target.chmod(0o640)
            sentinels[target] = (target.read_bytes(), target.stat())
        expected = {
            **existing, **self.managed,
            "subagents": {**existing["subagents"], **self.managed["subagents"]},
        }
        for _ in range(2):
            self.assertEqual(self.assert_merge_succeeds(), expected)
            self.assertEqual(self.agent.stat().st_mode & 0o777, 0o750)
            for target, (content, stat) in sentinels.items():
                self.assertEqual(target.read_bytes(), content)
                current = target.stat()
                self.assertEqual(current.st_mode, stat.st_mode)
                self.assertEqual(current.st_mtime_ns, stat.st_mtime_ns)
                self.assertEqual(current.st_ino, stat.st_ino)

    def test_repeated_sync_is_byte_idempotent(self):
        self.write_settings({"theme": "fixture-theme", "subagents": {"unknown": True}})
        expected = self.assert_merge_succeeds()
        original = self.settings.read_bytes()
        for _ in range(2):
            self.assertEqual(self.assert_merge_succeeds(), expected)
            self.assertEqual(self.settings.read_bytes(), original)

    def test_invalid_existing_json_fails_without_modification(self):
        self.agent.mkdir(parents=True)
        self.agent.chmod(0o750)
        for invalid in (b"{broken json\n", b"[]\n", b"null\n", b'"not an object"\n'):
            with self.subTest(invalid=invalid):
                self.settings.write_bytes(invalid)
                self.settings.chmod(0o600)
                before = self.settings.stat()
                result = self.run_merge()
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Pi settings synchronization failed", result.stderr)
                self.assertEqual(self.settings.read_bytes(), invalid)
                after = self.settings.stat()
                self.assertEqual(after.st_mode, before.st_mode)
                self.assertEqual(after.st_mtime_ns, before.st_mtime_ns)
                self.assertEqual(after.st_ino, before.st_ino)
                self.assertEqual(self.agent.stat().st_mode & 0o777, 0o750)
                self.assertFalse(list(self.agent.glob(".settings.json.chezmoi-*")))


if __name__ == "__main__":
    unittest.main()
