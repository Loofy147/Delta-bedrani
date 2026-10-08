"""Validate the machine-readable research claim registry.

The gate is intentionally local and deterministic: it validates schema/provenance
and detects evidence-path drift relative to each claim's verified commit. It does
not attempt to authenticate the external CI run identifiers; those remain
evidence references recorded by the research workflow.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


REQUIRED_PROJECT = ("repository", "branch", "verified_head")
REQUIRED_CLAIM = (
    "claim_id",
    "claim",
    "status",
    "evidence_class",
    "scope",
    "source_path",
    "verification_path",
    "verification_run",
    "verified_commit",
    "disposition",
    "limits",
)
VALID_STATUSES = {
    "ESTABLISHED",
    "EXPERIMENTALLY_SUPPORTED",
    "USER_REPORTED",
    "INFERENCE",
    "HYPOTHESIS",
    "CONTRADICTED",
    "UNKNOWN",
    "OPEN",
}
VALID_DISPOSITIONS = {
    "CONFIRMED",
    "PARTIALLY_CONFIRMED",
    "CONTRADICTED",
    "REFINED",
    "INCONCLUSIVE",
    "INVALID_RESULT",
    "CONTEXT_BOUND",
    "REGRESSION",
    "NOVEL_SIGNAL",
    "OPEN",
}
VALID_EVIDENCE_CLASSES = {
    "THEORETICAL",
    "DIFFERENTIAL",
    "EXHAUSTIVE-FINITE",
    "REGRESSION",
    "BENCHMARK",
    "OPERATING-PROTOCOL",
}


def _git(repo_root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=repo_root, text=True
    ).strip()


def _commit_exists(repo_root: Path, commit: str) -> bool:
    try:
        _git(repo_root, "cat-file", "-e", f"{commit}^{{commit}}")
        return True
    except subprocess.CalledProcessError:
        return False


def _is_ancestor(repo_root: Path, older: str, newer: str) -> bool:
    try:
        subprocess.check_call(
            ["git", "merge-base", "--is-ancestor", older, newer],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def _changed_paths(repo_root: Path, start: str, end: str) -> set[str]:
    if start == end:
        return set()
    out = _git(repo_root, "diff", "--name-only", f"{start}..{end}")
    return {line for line in out.splitlines() if line}


def validate_registry(
    registry_path: str | Path,
    *,
    repo_root: str | Path,
    require_current_tree: bool = True,
) -> list[str]:
    """Return deterministic validation errors; an empty list means valid."""
    registry_path = Path(registry_path)
    repo_root = Path(repo_root)
    errors: list[str] = []

    try:
        data: Any = json.loads(registry_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"registry unreadable: {exc}"]

    if data.get("schema") != "delta-bedrani-claim-registry-v0.1":
        errors.append("unsupported or missing registry schema")

    project = data.get("project")
    if not isinstance(project, dict):
        return errors + ["project must be an object"]

    for field in REQUIRED_PROJECT:
        if not project.get(field):
            errors.append(f"project.{field} is required")

    claims = data.get("claims")
    if not isinstance(claims, list) or not claims:
        return errors + ["claims must be a non-empty array"]

    current_head = _git(repo_root, "rev-parse", "HEAD")
    verified_head = project.get("verified_head")
    if verified_head and not _commit_exists(repo_root, verified_head):
        errors.append(f"project.verified_head is not a local commit: {verified_head}")
    elif verified_head and not _is_ancestor(repo_root, verified_head, current_head):
        errors.append(
            f"project.verified_head is not an ancestor of current HEAD: {verified_head}"
        )

    seen_ids: set[str] = set()
    for claim in claims:
        if not isinstance(claim, dict):
            errors.append("claim entry must be an object")
            continue
        claim_id = claim.get("claim_id", "<missing>")
        if claim_id in seen_ids:
            errors.append(f"duplicate claim_id: {claim_id}")
        seen_ids.add(claim_id)

        for field in REQUIRED_CLAIM:
            if not claim.get(field):
                errors.append(f"claim {claim_id} missing {field}")

        status = claim.get("status")
        if status and status not in VALID_STATUSES:
            errors.append(f"claim {claim_id} has invalid status: {status}")

        disposition = claim.get("disposition")
        if disposition and disposition not in VALID_DISPOSITIONS:
            errors.append(f"claim {claim_id} has invalid disposition: {disposition}")

        evidence_class = claim.get("evidence_class")
        if evidence_class and evidence_class not in VALID_EVIDENCE_CLASSES:
            errors.append(
                f"claim {claim_id} has invalid evidence_class: {evidence_class}"
            )

        verification_path = claim.get("verification_path")
        verified_commit = claim.get("verified_commit")
        source_path = claim.get("source_path")
        if verification_path and not (repo_root / verification_path).is_file():
            errors.append(f"claim {claim_id} verification_path does not exist")
        if source_path and not (repo_root / source_path).is_file():
            errors.append(f"claim {claim_id} source_path does not exist")

        if verified_commit:
            if not _commit_exists(repo_root, verified_commit):
                errors.append(
                    f"claim {claim_id} verified_commit is not a local commit: "
                    f"{verified_commit}"
                )
                continue
            if not _is_ancestor(repo_root, verified_commit, current_head):
                errors.append(
                    f"claim {claim_id} verified_commit is not an ancestor of current HEAD"
                )
                continue

            if require_current_tree:
                changed = _changed_paths(repo_root, verified_commit, current_head)
                paths = {p for p in (source_path, verification_path) if p}
                drift = sorted(changed & paths)
                if drift:
                    errors.append(
                        f"claim {claim_id} evidence paths changed after verified_commit: "
                        + ", ".join(drift)
                    )

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    registry = root / "evidence" / "claims-v0.1.json"
    errors = validate_registry(registry, repo_root=root, require_current_tree=True)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("claim registry: valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
