#!/usr/bin/env python3
"""Offline tests for validate_bestpractices.py."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_bestpractices.py"
SPEC = importlib.util.spec_from_file_location("validate_bestpractices", SCRIPT)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load validator from {SCRIPT}")
VALIDATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


class ValidatorCliTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)
        self.project = {
            "id": 42,
            "user_id": 7,
            "contribution_status": "?",
            "contribution_justification": "",
            "passwords_status": "?",
            "passwords_justification": "",
            "review_status": "?",
            "review_justification": "",
            "optional_status": "?",
            "optional_justification": "",
        }
        self.rules = {
            "contribution": {
                "strength": "MUST",
                "allow_na": False,
                "na_requires_justification": False,
                "met_requires_url": True,
                "met_requires_justification": False,
            },
            "passwords": {
                "strength": "MUST",
                "allow_na": True,
                "na_requires_justification": True,
                "met_requires_url": False,
                "met_requires_justification": True,
            },
            "review": {
                "strength": "SHOULD",
                "allow_na": False,
                "na_requires_justification": False,
                "met_requires_url": False,
                "met_requires_justification": False,
            },
            "optional": {
                "strength": "SUGGESTED",
                "allow_na": False,
                "na_requires_justification": False,
                "met_requires_url": False,
                "met_requires_justification": False,
            },
        }
        self.project_path = self.write_json("project.json", self.project)
        self.rules_path = self.write_json("rules.json", self.rules)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_json(
        self, name: str, value: dict[str, Any], *, canonical: bool = False
    ) -> Path:
        path = self.directory / name
        if canonical:
            path.write_bytes(VALIDATOR.canonical_bytes(value))
        else:
            path.write_text(
                json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        return path

    def run_validator(self, candidate: Path, *extra: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--candidate",
                str(candidate),
                "--repo-root",
                str(self.directory),
                "--project-json",
                str(self.project_path),
                "--rules",
                str(self.rules_path),
                *extra,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )

    def assert_invalid(self, candidate: dict[str, Any], expected: str) -> None:
        path = self.write_json("candidate.json", candidate, canonical=True)
        result = self.run_validator(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(expected, result.stderr)

    def test_accepts_known_canonical_answers(self) -> None:
        candidate = {
            "contribution_status": "Met",
            "contribution_justification": (
                "Documented at "
                "https://github.com/example/project/blob/"
                "0123456789abcdef0123456789abcdef01234567/CONTRIBUTING.md"
            ),
            "passwords_status": "N/A",
            "passwords_justification": "The project does not operate a password store.",
            "review_status": "Unmet",
            "review_justification": "Reviews are not yet consistently required.",
            "optional_status": "Unmet",
        }
        path = self.write_json("candidate.json", candidate, canonical=True)
        result = self.run_validator(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OK: 4 known criterion status(es)", result.stdout)

    def test_rejects_unknown_and_numeric_statuses(self) -> None:
        self.assert_invalid(
            {"optional_status": "unknown"},
            "status must be exactly Met, Unmet, or N/A",
        )
        self.assert_invalid(
            {"optional_status": 3},
            "status must be exactly Met, Unmet, or N/A",
        )

    def test_rejects_server_managed_and_unknown_fields(self) -> None:
        self.assert_invalid({"id": 42}, "only recognized _status")
        self.assert_invalid(
            {"invented_status": "Met"},
            "field is not present in the frozen project JSON",
        )

    def test_enforces_should_unmet_justification_length(self) -> None:
        self.assert_invalid(
            {"review_status": "Unmet", "review_justification": "four"},
            "require at least 5 characters",
        )

    def test_enforces_met_url_and_public_url_policy(self) -> None:
        self.assert_invalid(
            {
                "contribution_status": "Met",
                "contribution_justification": "See http://example.com/policy",
            },
            "requires a public HTTPS URL",
        )
        self.assert_invalid(
            {
                "contribution_status": "Met",
                "contribution_justification": "See https://localhost/policy",
            },
            "requires a public HTTPS URL",
        )
        self.assert_invalid(
            {
                "contribution_status": "Met",
                "contribution_justification": "See https://token@example.com/policy",
            },
            "requires a public HTTPS URL",
        )
        self.assert_invalid(
            {
                "contribution_status": "Met",
                "contribution_justification": "See https://intranet/policy",
            },
            "requires a public HTTPS URL",
        )
        self.assert_invalid(
            {
                "contribution_status": "Met",
                "contribution_justification": "See https://example.com/policy?token=secret",
            },
            "requires a public HTTPS URL",
        )

    def test_enforces_na_applicability_and_justification(self) -> None:
        self.assert_invalid(
            {"optional_status": "N/A"},
            "N/A is not allowed for this criterion",
        )
        self.assert_invalid(
            {"passwords_status": "N/A"},
            "this N/A criterion requires a justification",
        )

    def test_rejects_justification_without_status(self) -> None:
        self.assert_invalid(
            {"optional_justification": "Not currently implemented."},
            "corresponding optional_status is required",
        )

    def test_rejects_noncanonical_format(self) -> None:
        candidate = {
            "optional_justification": "An explanation.",
            "optional_status": "Met",
        }
        path = self.write_json("candidate.json", candidate, canonical=False)
        result = self.run_validator(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not in canonical format", result.stderr)

    def test_rejects_duplicate_keys(self) -> None:
        path = self.directory / "candidate.json"
        path.write_text(
            '{"optional_status":"Met","optional_status":"Unmet"}\n',
            encoding="utf-8",
        )
        result = self.run_validator(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate JSON key", result.stderr)

    @unittest.skipIf(os.name == "nt", "symlink behavior differs on Windows")
    def test_rejects_candidate_symlink(self) -> None:
        target = self.write_json(
            "target.json", {"optional_status": "Met"}, canonical=True
        )
        link = self.directory / "candidate.json"
        link.symlink_to(target)
        result = self.run_validator(link)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must not contain symbolic links", result.stderr)

    @unittest.skipIf(os.name == "nt", "symlink behavior differs on Windows")
    def test_rejects_symlinked_parent_and_hardlink(self) -> None:
        outside = Path(self.temp_dir.name).parent / f"{self.directory.name}-outside"
        outside.mkdir()
        self.addCleanup(lambda: outside.rmdir() if outside.exists() else None)
        target = outside / "candidate.json"
        target.write_bytes(VALIDATOR.canonical_bytes({"optional_status": "Met"}))
        link_dir = self.directory / "linked"
        link_dir.symlink_to(outside, target_is_directory=True)
        result = self.run_validator(link_dir / "candidate.json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("parent components must be real directories", result.stderr)
        link_dir.unlink()

        original = self.write_json(
            "original.json", {"optional_status": "Met"}, canonical=True
        )
        hardlink = self.directory / "candidate.json"
        os.link(original, hardlink)
        result = self.run_validator(hardlink)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must not be hard-linked", result.stderr)
        hardlink.unlink()
        target.unlink()

    def test_rejects_malformed_rule_strength_type(self) -> None:
        self.rules["optional"]["strength"] = []
        self.rules_path = self.write_json("rules.json", self.rules)
        path = self.write_json(
            "candidate.json", {"optional_status": "Met"}, canonical=True
        )
        result = self.run_validator(path)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("strength must be MUST, SHOULD, or SUGGESTED", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_rejects_empty_candidate(self) -> None:
        self.assert_invalid({}, "must contain at least one known criterion answer")


if __name__ == "__main__":
    unittest.main()
