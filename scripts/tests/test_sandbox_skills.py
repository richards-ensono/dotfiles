#!/usr/bin/env python3
"""Focused regression tests for the author-owned Pi sandbox skills."""
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / ".chezmoitemplates/pi/skills"
BWRAP = SKILLS / "bubblewrap-sandbox/executable_bwrap-run.sh"
PODMAN = SKILLS / "podman-containers/executable_podman-run.sh"
DIGEST = "example.invalid/test@sha256:" + "a" * 64


class SandboxSkillsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sandbox-skills-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.home = self.root / "home"
        self.home.mkdir()
        self.project = self.root / "project"
        self.project.mkdir()
        self.output = self.project / "output"
        self.output.mkdir()
        self.dist = self.output / "dist"
        self.dist.mkdir()
        self.bin = self.root / "bin"
        self.bin.mkdir()
        mock = self.bin / "podman"
        mock.write_text(
            "#!/bin/sh\n"
            "if [ \"$1\" = info ]; then\n"
            "  case \"$3\" in *Rootless*) echo true;; *) echo false;; esac\n"
            "else printf '%s\\n' \"$@\"; fi\n",
            encoding="utf-8",
        )
        mock.chmod(0o755)
        self.env = {**os.environ, "HOME": str(self.home), "PATH": f"{self.bin}:{os.environ['PATH']}"}

    def run_wrapper(self, script, *args, cwd=None):
        return subprocess.run(
            ["bash", str(script), *args], cwd=cwd or self.project, env=self.env,
            capture_output=True, text=True, timeout=15,
        )

    def test_rejects_sensitive_read_only_mounts_and_sensitive_workdir(self):
        private = self.home / ".ssh"
        for directory in (private, self.home / ".config", self.home / ".local"):
            directory.mkdir()
        for script, trailer in ((BWRAP, ("true",)), (PODMAN, (DIGEST,))):
            for path in (private, self.home / ".config", self.home / ".local", self.home, self.root):
                with self.subTest(script=script.name, path=path):
                    result = self.run_wrapper(script, "--dry-run", "--ro", str(path), "--", *trailer)
                    self.assertNotEqual(result.returncode, 0)
            result = self.run_wrapper(script, "--dry-run", "--", *trailer, cwd=self.home)
            self.assertNotEqual(result.returncode, 0)

    def test_rejects_sockets_even_when_read_only(self):
        sock_path = self.root / "podman.sock"
        with socket.socket(socket.AF_UNIX) as sock:
            sock.bind(str(sock_path))
            for script, trailer in ((BWRAP, ("true",)), (PODMAN, (DIGEST,))):
                for path in (sock_path, self.root):
                    with self.subTest(script=script.name, path=path):
                        result = self.run_wrapper(script, "--dry-run", "--ro", str(path), "--", *trailer)
                        self.assertNotEqual(result.returncode, 0)

    @unittest.skipUnless(shutil.which("bwrap"), "bubblewrap is not installed")
    def test_bwrap_ro_default_and_writable_child_with_ro_override(self):
        result = self.run_wrapper(BWRAP, "--timeout", "5", "--", "sh", "-c", "touch blocked")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.project / "blocked").exists())
        result = self.run_wrapper(
            BWRAP, "--rw", str(self.dist), "--timeout", "5", "--",
            "sh", "-c", "touch output/dist/allowed",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.dist / "allowed").exists())
        result = self.run_wrapper(
            BWRAP, "--rw", str(self.output), "--ro", str(self.dist), "--timeout", "5", "--",
            "sh", "-c", "touch output/dist/blocked",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.dist / "blocked").exists())

    def test_podman_mount_order_and_image_boundary(self):
        result = self.run_wrapper(PODMAN, "--rw", str(self.dist), "--", DIGEST, "true")
        self.assertEqual(result.returncode, 0, result.stderr)
        args = result.stdout.splitlines()
        self.assertLess(args.index(f"{self.project}:/workspace:ro"), args.index(f"{self.dist}:/workspace/output/dist:rw"))
        self.assertEqual(args[args.index("--") + 1], DIGEST)
        result = self.run_wrapper(PODMAN, "--rw", str(self.output), "--ro", str(self.dist), "--", DIGEST)
        self.assertEqual(result.returncode, 0, result.stderr)
        args = result.stdout.splitlines()
        self.assertLess(args.index(f"{self.output}:/workspace/output:rw"), args.index(f"{self.dist}:/workspace/output/dist:ro"))
        for script, trailer in ((BWRAP, ("true",)), (PODMAN, (DIGEST,))):
            with self.subTest(script=script.name):
                duplicate = self.run_wrapper(script, "--dry-run", "--rw", str(self.project), "--", *trailer)
                self.assertNotEqual(duplicate.returncode, 0)
        for image in ("--privileged", "image@sha256:not-a-digest", "-v"):
            with self.subTest(image=image):
                result = self.run_wrapper(PODMAN, "--allow-tag", "--", image, "ignored")
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(result.stdout)

    def test_resource_caps_cannot_be_disabled(self):
        for script, trailer in ((BWRAP, ("true",)), (PODMAN, (DIGEST,))):
            with self.subTest(script=script.name):
                result = self.run_wrapper(script, "--dry-run", "--timeout", "0", "--", *trailer)
                self.assertNotEqual(result.returncode, 0)
        for flag in ("--memory", "--pids-limit"):
            with self.subTest(flag=flag):
                result = self.run_wrapper(PODMAN, "--dry-run", flag, "0", "--", DIGEST)
                self.assertNotEqual(result.returncode, 0)

    def test_environment_validation_and_redacted_dry_run(self):
        marker = "SYNTHETIC-TEST-VALUE"
        for script, trailer in ((BWRAP, ("true",)), (PODMAN, (DIGEST,))):
            for name in ("api_token", "AWS_ACCESS_KEY_ID", "bad-name"):
                with self.subTest(script=script.name, name=name):
                    result = self.run_wrapper(script, "--dry-run", "--env", f"{name}={marker}", "--", *trailer)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertNotIn(marker, result.stderr)
            result = self.run_wrapper(script, "--dry-run", "--env", f"PUBLIC_VALUE={marker}", "--", *trailer, marker)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn(marker, result.stderr + result.stdout)

    @unittest.skipUnless(shutil.which("chezmoi") and shutil.which("node"), "chezmoi/node unavailable")
    def test_skill_sync_preserves_agent_permissions_and_state(self):
        agent = self.home / ".pi/agent"
        agent.mkdir(parents=True)
        agent.chmod(0o750)
        (agent / "settings.json").write_text("untouched", encoding="utf-8")
        template = (ROOT / "run_after_sync-pi-skills.js.tmpl").read_text(encoding="utf-8")
        rendered = subprocess.run(
            ["chezmoi", "execute-template", "--source", str(ROOT)], input=template,
            capture_output=True, text=True, check=True,
        ).stdout
        script = self.root / "sync.js"
        script.write_text(rendered, encoding="utf-8")
        for _ in range(2):
            result = subprocess.run(["node", str(script)], env=self.env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(agent.stat().st_mode & 0o777, 0o750)
            self.assertEqual((agent / "settings.json").read_text(encoding="utf-8"), "untouched")
        runner = agent / "skills/bubblewrap-sandbox/bwrap-run.sh"
        self.assertEqual(runner.stat().st_mode & 0o777, 0o755)
        github = agent / "skills/github/SKILL.md"
        self.assertEqual(github.stat().st_mode & 0o777, 0o644)
        self.assertEqual(github.read_bytes(), (SKILLS / "github/SKILL.md").read_bytes())
        previous = runner.stat().st_mtime_ns
        github_previous = github.stat().st_mtime_ns
        subprocess.run(["node", str(script)], env=self.env, check=True)
        self.assertEqual(runner.stat().st_mtime_ns, previous)
        self.assertEqual(github.stat().st_mtime_ns, github_previous)
        runner.unlink()
        runner.symlink_to(agent / "settings.json")
        result = subprocess.run(["node", str(script)], env=self.env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((agent / "settings.json").read_text(encoding="utf-8"), "untouched")


if __name__ == "__main__":
    unittest.main()
