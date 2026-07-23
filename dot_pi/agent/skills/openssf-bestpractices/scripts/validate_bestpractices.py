#!/usr/bin/env python3
"""Validate and canonicalize an OpenSSF Best Practices repository answer file."""

from __future__ import annotations

import argparse
import errno
import ipaddress
import json
import os
import re
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NoReturn
from urllib.parse import urlsplit

MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_JUSTIFICATION_LENGTH = 8192
KNOWN_STATUSES = frozenset({"Met", "Unmet", "N/A"})
KNOWN_STRENGTHS = frozenset({"MUST", "SHOULD", "SUGGESTED"})
FIELD_RE = re.compile(r"^(?P<criterion>[a-zA-Z0-9_]+)_(?P<kind>status|justification)$")
HTTPS_URL_RE = re.compile(r"https://[^\s<>\[\]{}\"']+")


class ValidationError(Exception):
    """A deterministic validation failure suitable for user-facing output."""


class DuplicateKeyError(ValueError):
    """Raised when a JSON object contains the same key more than once."""


@dataclass(frozen=True)
class CriterionRule:
    strength: str
    allow_na: bool
    na_requires_justification: bool
    met_requires_url: bool
    met_requires_justification: bool


def duplicate_safe_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json_object(raw: bytes, path: Path, label: str) -> dict[str, Any]:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValidationError(f"{label} is not valid UTF-8: {path}") from error
    try:
        value = json.loads(text, object_pairs_hook=duplicate_safe_object)
    except (json.JSONDecodeError, DuplicateKeyError, RecursionError) as error:
        raise ValidationError(f"invalid {label} JSON in {path}: {error}") from error
    if not isinstance(value, dict):
        raise ValidationError(f"{label} must have a JSON object root: {path}")
    return value


def read_candidate_safely(path: Path, repo_root: Path) -> tuple[dict[str, Any], bytes]:
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    directory = getattr(os, "O_DIRECTORY", 0)
    nonblock = getattr(os, "O_NONBLOCK", 0)
    if not nofollow or not directory:
        raise ValidationError("this platform cannot provide no-follow candidate validation")

    try:
        root = repo_root.resolve(strict=True)
    except OSError as error:
        raise ValidationError(f"cannot resolve repository root {repo_root}: {error}") from error
    if not root.is_dir():
        raise ValidationError(f"repository root is not a directory: {root}")

    candidate = Path(os.path.abspath(path))
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise ValidationError(f"candidate is outside repository root {root}: {candidate}") from error
    if not relative.parts:
        raise ValidationError("candidate path must name a file below the repository root")

    descriptors: list[int] = []
    try:
        current_fd = os.open(root, os.O_RDONLY | directory)
        descriptors.append(current_fd)
        for component in relative.parts[:-1]:
            current_fd = os.open(
                component,
                os.O_RDONLY | directory | nofollow,
                dir_fd=current_fd,
            )
            descriptors.append(current_fd)
        candidate_fd = os.open(
            relative.parts[-1],
            os.O_RDONLY | nofollow | nonblock,
            dir_fd=current_fd,
        )
        descriptors.append(candidate_fd)
        metadata = os.fstat(candidate_fd)
        if not stat.S_ISREG(metadata.st_mode):
            raise ValidationError(f"candidate must be a regular file: {candidate}")
        if metadata.st_nlink != 1:
            raise ValidationError(f"candidate must not be hard-linked: {candidate}")
        if metadata.st_size > MAX_FILE_BYTES:
            raise ValidationError(
                f"candidate exceeds the {MAX_FILE_BYTES}-byte validation limit: {candidate}"
            )
        chunks: list[bytes] = []
        remaining = MAX_FILE_BYTES + 1
        while remaining:
            chunk = os.read(candidate_fd, min(65536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
        if len(raw) > MAX_FILE_BYTES:
            raise ValidationError(
                f"candidate exceeds the {MAX_FILE_BYTES}-byte validation limit: {candidate}"
            )
    except ValidationError:
        raise
    except OSError as error:
        if error.errno == errno.ELOOP:
            raise ValidationError(
                f"candidate path must not contain symbolic links: {candidate}"
            ) from error
        if error.errno == errno.ENOTDIR:
            raise ValidationError(
                f"candidate parent components must be real directories: {candidate}"
            ) from error
        raise ValidationError(f"cannot safely read candidate {candidate}: {error}") from error
    finally:
        for descriptor in reversed(descriptors):
            try:
                os.close(descriptor)
            except OSError:
                pass

    return parse_json_object(raw, candidate, "candidate"), raw


def load_json_object(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    try:
        metadata = path.stat()
    except OSError as error:
        raise ValidationError(f"cannot stat {label} {path}: {error}") from error
    if not stat.S_ISREG(metadata.st_mode):
        raise ValidationError(f"{label} must be a regular file: {path}")
    if metadata.st_size > MAX_FILE_BYTES:
        raise ValidationError(
            f"{label} exceeds the {MAX_FILE_BYTES}-byte validation limit: {path}"
        )
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise ValidationError(f"cannot read {label} {path}: {error}") from error
    return parse_json_object(raw, path, label), raw


def require_bool(rule_name: str, field: str, value: Any) -> bool:
    if not isinstance(value, bool):
        raise ValidationError(f"rules.{rule_name}.{field} must be a boolean")
    return value


def load_rules(path: Path) -> dict[str, CriterionRule]:
    raw_rules, _ = load_json_object(path, "rules")
    rules: dict[str, CriterionRule] = {}
    expected_fields = {
        "strength",
        "allow_na",
        "na_requires_justification",
        "met_requires_url",
        "met_requires_justification",
    }
    for criterion, raw_rule in raw_rules.items():
        if not isinstance(criterion, str) or not re.fullmatch(r"[a-zA-Z0-9_]+", criterion):
            raise ValidationError(f"invalid criterion name in rules: {criterion!r}")
        if not isinstance(raw_rule, dict):
            raise ValidationError(f"rules.{criterion} must be an object")
        unknown = sorted(set(raw_rule) - expected_fields)
        missing = sorted(expected_fields - set(raw_rule))
        if unknown:
            raise ValidationError(
                f"rules.{criterion} has unknown fields: {', '.join(unknown)}"
            )
        if missing:
            raise ValidationError(
                f"rules.{criterion} is missing fields: {', '.join(missing)}"
            )
        strength = raw_rule["strength"]
        if not isinstance(strength, str) or strength not in KNOWN_STRENGTHS:
            raise ValidationError(
                f"rules.{criterion}.strength must be MUST, SHOULD, or SUGGESTED"
            )
        rules[criterion] = CriterionRule(
            strength=strength,
            allow_na=require_bool(criterion, "allow_na", raw_rule["allow_na"]),
            na_requires_justification=require_bool(
                criterion,
                "na_requires_justification",
                raw_rule["na_requires_justification"],
            ),
            met_requires_url=require_bool(
                criterion, "met_requires_url", raw_rule["met_requires_url"]
            ),
            met_requires_justification=require_bool(
                criterion,
                "met_requires_justification",
                raw_rule["met_requires_justification"],
            ),
        )
    return rules


def public_https_urls(text: str) -> list[str]:
    urls: list[str] = []
    for raw_url in HTTPS_URL_RE.findall(text):
        url = raw_url.rstrip(".,;:!?)")
        try:
            parsed = urlsplit(url)
            host = parsed.hostname
            port = parsed.port
        except ValueError:
            continue
        if parsed.scheme != "https" or not host or parsed.username or parsed.password:
            continue
        if parsed.query or parsed.fragment or port not in (None, 443):
            continue
        normalized_host = host.rstrip(".").lower()
        if normalized_host == "localhost" or normalized_host.endswith(".localhost"):
            continue
        if normalized_host.endswith(".local") or normalized_host.endswith(".internal"):
            continue
        try:
            address = ipaddress.ip_address(normalized_host)
        except ValueError:
            if "." not in normalized_host:
                continue
            labels = normalized_host.split(".")
            if any(not label or len(label) > 63 for label in labels):
                continue
            if any(label.startswith("-") or label.endswith("-") for label in labels):
                continue
            if any(not re.fullmatch(r"[a-z0-9-]+", label) for label in labels):
                continue
        else:
            if not address.is_global:
                continue
        urls.append(url)
    return urls


def canonical_field_key(field: str) -> tuple[str, int]:
    match = FIELD_RE.fullmatch(field)
    if not match:
        return (field, 2)
    return (match.group("criterion"), 0 if match.group("kind") == "status" else 1)


def canonical_bytes(candidate: dict[str, Any]) -> bytes:
    ordered = {key: candidate[key] for key in sorted(candidate, key=canonical_field_key)}
    return (json.dumps(ordered, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def validate(
    candidate: dict[str, Any],
    project: dict[str, Any],
    rules: dict[str, CriterionRule],
) -> list[str]:
    errors: list[str] = []
    status_fields: dict[str, str] = {}
    justification_fields: dict[str, str] = {}

    if not candidate:
        errors.append("candidate must contain at least one known criterion answer")

    for field, value in candidate.items():
        match = FIELD_RE.fullmatch(field)
        if not match:
            errors.append(
                f"{field}: only recognized _status and _justification criterion fields are allowed"
            )
            continue
        if field not in project:
            errors.append(f"{field}: field is not present in the frozen project JSON")
            continue
        criterion = match.group("criterion")
        kind = match.group("kind")
        if criterion not in rules:
            errors.append(f"{field}: criterion has no frozen rules metadata")
            continue
        if kind == "status":
            if not isinstance(value, str) or value not in KNOWN_STATUSES:
                errors.append(f"{field}: status must be exactly Met, Unmet, or N/A")
                continue
            status_fields[criterion] = value
        else:
            if not isinstance(value, str):
                errors.append(f"{field}: justification must be a string")
                continue
            stripped = value.strip()
            if not stripped:
                errors.append(f"{field}: justification must not be blank")
                continue
            if len(stripped) > MAX_JUSTIFICATION_LENGTH:
                errors.append(
                    f"{field}: justification exceeds {MAX_JUSTIFICATION_LENGTH} characters"
                )
                continue
            if stripped != value:
                errors.append(f"{field}: justification must not have surrounding whitespace")
            justification_fields[criterion] = value

    for criterion in sorted(justification_fields):
        if criterion not in status_fields:
            errors.append(
                f"{criterion}_justification: corresponding {criterion}_status is required"
            )

    for criterion, status in sorted(status_fields.items()):
        rule = rules[criterion]
        justification = justification_fields.get(criterion)
        if status == "N/A" and not rule.allow_na:
            errors.append(f"{criterion}_status: N/A is not allowed for this criterion")
        if status == "N/A" and rule.na_requires_justification and justification is None:
            errors.append(
                f"{criterion}_justification: this N/A criterion requires a justification"
            )
        if status == "Unmet" and rule.strength == "SHOULD":
            if justification is None or len(justification) < 5:
                errors.append(
                    f"{criterion}_justification: SHOULD criteria marked Unmet require at least 5 characters"
                )
        if status == "Met" and rule.met_requires_justification and justification is None:
            errors.append(
                f"{criterion}_justification: this Met criterion requires a justification"
            )
        if status == "Met" and rule.met_requires_url:
            if justification is None or not public_https_urls(justification):
                errors.append(
                    f"{criterion}_justification: this Met criterion requires a public HTTPS URL"
                )

    return sorted(set(errors))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a criterion-only .bestpractices.json against a frozen "
            "bestpractices.dev project response and frozen criteria rules."
        )
    )
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--project-json", required=True, type=Path)
    parser.add_argument("--rules", required=True, type=Path)
    return parser.parse_args()


def fail(message: str) -> NoReturn:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    args = parse_args()
    try:
        candidate, current = read_candidate_safely(args.candidate, args.repo_root)
        project, _ = load_json_object(args.project_json, "project snapshot")
        rules = load_rules(args.rules)
        errors = validate(candidate, project, rules)
    except ValidationError as error:
        fail(str(error))

    if errors:
        print(f"FAIL: {len(errors)} validation error(s)", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    rendered = canonical_bytes(candidate)
    if current != rendered:
        print(
            "FAIL: candidate is valid but not in canonical format",
            file=sys.stderr,
        )
        return 1

    status_count = sum(key.endswith("_status") for key in candidate)
    justification_count = sum(key.endswith("_justification") for key in candidate)
    print(
        "OK: "
        f"{status_count} known criterion status(es), "
        f"{justification_count} justification(s); canonical format verified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
