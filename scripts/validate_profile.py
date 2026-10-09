#!/usr/bin/env python3
"""Validate the structural integrity of a personal multiscale profile."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any


ALLOWED_STATUSES = {"draft", "active", "archived"}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}
ALLOWED_EVIDENCE_TYPES = {
    "self_report",
    "artifact",
    "third_party",
    "observation",
    "public_record",
    "inference",
}
ALLOWED_RELIABILITY = {"high", "medium", "low"}
ALLOWED_CONTRADICTION_STATUSES = {"unresolved", "confirmed", "weakened", "contradicted"}
REQUIRED_SCALES = {"micro", "meso", "macro", "temporal", "contextual"}
PROHIBITED_KEYS = {
    "overall_score",
    "personality_score",
    "potential_score",
    "suitability_score",
    "trait_probability",
    "diagnosis",
}


def is_iso_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def find_prohibited_keys(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in PROHIBITED_KEYS:
                errors.append(f"{path}.{key}: prohibited key")
            errors.extend(find_prohibited_keys(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            errors.extend(find_prohibited_keys(child, f"{path}[{index}]"))
    return errors


def require_mapping(value: Any, path: str, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{path}: expected object")
        return None
    return value


def require_list(value: Any, path: str, errors: list[str]) -> list[Any] | None:
    if not isinstance(value, list):
        errors.append(f"{path}: expected list")
        return None
    return value


def require_string(value: Any, path: str, errors: list[str], *, nonempty: bool = True) -> None:
    if not isinstance(value, str):
        errors.append(f"{path}: expected string")
    elif nonempty and not value.strip():
        errors.append(f"{path}: expected non-empty string")


def validate_profile(profile: Any) -> list[str]:
    errors: list[str] = []
    errors.extend(find_prohibited_keys(profile))
    root = require_mapping(profile, "$", errors)
    if root is None:
        return errors

    required_top_level = {
        "schema_version",
        "profile_id",
        "subject",
        "created_at",
        "updated_at",
        "status",
        "consent",
        "scales",
        "evidence",
        "contradictions",
        "development_targets",
        "revision_history",
    }
    for key in sorted(required_top_level):
        if key not in root:
            errors.append(f"$.{key}: missing required field")

    for key in ("schema_version", "profile_id"):
        if key in root:
            require_string(root[key], f"$.{key}", errors)

    for key in ("created_at", "updated_at"):
        if key in root and not is_iso_date(root[key]):
            errors.append(f"$.{key}: expected YYYY-MM-DD date")

    if root.get("status") not in ALLOWED_STATUSES:
        errors.append(f"$.status: expected one of {sorted(ALLOWED_STATUSES)}")

    subject = require_mapping(root.get("subject"), "$.subject", errors)
    if subject is not None:
        require_string(subject.get("label"), "$.subject.label", errors)
        require_string(subject.get("relationship"), "$.subject.relationship", errors)

    consent = require_mapping(root.get("consent"), "$.consent", errors)
    if consent is not None:
        require_string(consent.get("scope"), "$.consent.scope", errors)
        require_list(consent.get("sources"), "$.consent.sources", errors)
        for key in ("allow_persistent_storage", "allow_external_sharing"):
            if not isinstance(consent.get(key), bool):
                errors.append(f"$.consent.{key}: expected boolean")

    evidence = require_list(root.get("evidence"), "$.evidence", errors)
    evidence_ids: set[str] = set()
    if evidence is not None:
        for index, raw_record in enumerate(evidence):
            path = f"$.evidence[{index}]"
            record = require_mapping(raw_record, path, errors)
            if record is None:
                continue
            required = {"id", "type", "captured_at", "summary", "reliability", "sensitive"}
            for key in sorted(required):
                if key not in record:
                    errors.append(f"{path}.{key}: missing required field")
            record_id = record.get("id")
            require_string(record_id, f"{path}.id", errors)
            if isinstance(record_id, str):
                if record_id in evidence_ids:
                    errors.append(f"{path}.id: duplicate evidence id {record_id}")
                evidence_ids.add(record_id)
            if record.get("type") not in ALLOWED_EVIDENCE_TYPES:
                errors.append(f"{path}.type: unsupported evidence type")
            if not is_iso_date(record.get("captured_at")):
                errors.append(f"{path}.captured_at: expected YYYY-MM-DD date")
            require_string(record.get("summary"), f"{path}.summary", errors)
            if record.get("reliability") not in ALLOWED_RELIABILITY:
                errors.append(f"{path}.reliability: expected high, medium, or low")
            if not isinstance(record.get("sensitive"), bool):
                errors.append(f"{path}.sensitive: expected boolean")

    scales = require_mapping(root.get("scales"), "$.scales", errors)
    if scales is not None:
        if set(scales) != REQUIRED_SCALES:
            errors.append(
                "$.scales: expected exactly "
                + ", ".join(sorted(REQUIRED_SCALES))
            )
        for scale_name in sorted(REQUIRED_SCALES):
            raw_scale = scales.get(scale_name)
            path = f"$.scales.{scale_name}"
            scale = require_mapping(raw_scale, path, errors)
            if scale is None:
                continue
            require_string(scale.get("summary"), f"{path}.summary", errors)
            require_string(scale.get("interpretation"), f"{path}.interpretation", errors)
            if scale.get("confidence") not in ALLOWED_CONFIDENCE:
                errors.append(f"{path}.confidence: expected high, medium, or low")
            refs = require_list(scale.get("evidence_ids"), f"{path}.evidence_ids", errors)
            unknowns = require_list(scale.get("unknowns"), f"{path}.unknowns", errors)
            if refs is not None:
                for ref in refs:
                    if not isinstance(ref, str):
                        errors.append(f"{path}.evidence_ids: expected string ids")
                    elif ref not in evidence_ids:
                        errors.append(f"{path}.evidence_ids: unknown evidence id {ref}")
            if unknowns is not None:
                for ref in unknowns:
                    if not isinstance(ref, str):
                        errors.append(f"{path}.unknowns: expected strings")
                    elif not ref.strip():
                        errors.append(f"{path}.unknowns: expected non-empty strings")

    contradictions = require_list(root.get("contradictions"), "$.contradictions", errors)
    if contradictions is not None:
        for index, raw_item in enumerate(contradictions):
            path = f"$.contradictions[{index}]"
            item = require_mapping(raw_item, path, errors)
            if item is None:
                continue
            require_string(item.get("id"), f"{path}.id", errors)
            require_string(item.get("summary"), f"{path}.summary", errors)
            refs = require_list(item.get("evidence_ids"), f"{path}.evidence_ids", errors)
            if refs is not None:
                for ref in refs:
                    if not isinstance(ref, str):
                        errors.append(f"{path}.evidence_ids: expected string ids")
                    elif ref not in evidence_ids:
                        errors.append(f"{path}.evidence_ids: unknown evidence id {ref}")
            if item.get("status") not in ALLOWED_CONTRADICTION_STATUSES:
                errors.append(f"{path}.status: unsupported status")
            require_string(item.get("next_check"), f"{path}.next_check", errors)

    targets = require_list(root.get("development_targets"), "$.development_targets", errors)
    if targets is not None:
        for index, raw_target in enumerate(targets):
            path = f"$.development_targets[{index}]"
            target = require_mapping(raw_target, path, errors)
            if target is None:
                continue
            for key in ("id", "target", "why", "observable_result", "review_date"):
                require_string(target.get(key), f"{path}.{key}", errors)
            if not is_iso_date(target.get("review_date")):
                errors.append(f"{path}.review_date: expected YYYY-MM-DD date")

    revisions = require_list(root.get("revision_history"), "$.revision_history", errors)
    if revisions is not None:
        for index, raw_revision in enumerate(revisions):
            path = f"$.revision_history[{index}]"
            revision = require_mapping(raw_revision, path, errors)
            if revision is None:
                continue
            if not isinstance(revision.get("revision"), int) or revision.get("revision", 0) < 1:
                errors.append(f"{path}.revision: expected positive integer")
            if not is_iso_date(revision.get("date")):
                errors.append(f"{path}.date: expected YYYY-MM-DD date")
            require_string(revision.get("change"), f"{path}.change", errors)
            if revision.get("status") not in ALLOWED_STATUSES:
                errors.append(f"{path}.status: unsupported status")

    return errors


def load_profile(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"Profile file not found: {path}") from None
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from None


def run_self_test() -> int:
    valid = {
        "schema_version": "0.1.0",
        "profile_id": "self-test-v1",
        "subject": {"label": "Synthetic", "relationship": "self"},
        "created_at": "2026-10-09",
        "updated_at": "2026-10-09",
        "status": "draft",
        "consent": {
            "scope": "Synthetic validation.",
            "sources": ["self_report"],
            "allow_persistent_storage": False,
            "allow_external_sharing": True,
        },
        "scales": {
            name: {
                "summary": "Synthetic summary.",
                "evidence_ids": ["E001"],
                "confidence": "low",
                "unknowns": ["Synthetic unknown."],
                "interpretation": "Synthetic interpretation.",
            }
            for name in REQUIRED_SCALES
        },
        "evidence": [
            {
                "id": "E001",
                "type": "self_report",
                "captured_at": "2026-10-09",
                "summary": "Synthetic evidence.",
                "reliability": "low",
                "sensitive": False,
            }
        ],
        "contradictions": [],
        "development_targets": [],
        "revision_history": [
            {
                "revision": 1,
                "date": "2026-10-09",
                "change": "Created self-test.",
                "status": "draft",
            }
        ],
    }
    invalid = {"overall_score": 99}
    valid_errors = validate_profile(valid)
    invalid_errors = validate_profile(invalid)
    if valid_errors:
        print("Self-test failed: valid fixture returned errors.", file=sys.stderr)
        for error in valid_errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    if not any("prohibited key" in error for error in invalid_errors):
        print("Self-test failed: prohibited score field was not rejected.", file=sys.stderr)
        return 1
    print("Self-test passed.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", nargs="?", type=Path, help="JSON profile to validate")
    parser.add_argument("--self-test", action="store_true", help="Run built-in validation tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()
    if args.profile is None:
        parser.error("provide a profile path or use --self-test")

    errors = validate_profile(load_profile(args.profile))
    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Validation passed: {args.profile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
