import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _write_registry(payload):
    path = ROOT / "evidence" / "claims-v0.1.test.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_claim_registry_validator_accepts_current_registry():
    from tools.verify_claim_registry import validate_registry

    result = validate_registry(
        ROOT / "evidence" / "claims-v0.1.json",
        repo_root=ROOT,
        require_current_tree=False,
    )
    assert result == []


def test_claim_registry_validator_rejects_missing_provenance_fields(tmp_path):
    from tools.verify_claim_registry import validate_registry

    payload = {
        "schema": "delta-bedrani-claim-registry-v0.1",
        "project": {"repository": "Loofy147/Delta-bedrani"},
        "claims": [{"claim_id": "X", "claim": "x"}],
    }
    registry = tmp_path / "claims.json"
    registry.write_text(json.dumps(payload), encoding="utf-8")

    errors = validate_registry(registry, repo_root=ROOT, require_current_tree=False)
    assert any("project.branch" in error for error in errors)
    assert any("project.verified_head" in error for error in errors)
    assert any("claim X missing verification_path" in error for error in errors)


def test_claim_registry_validator_detects_stale_evidence_paths(tmp_path):
    from tools.verify_claim_registry import validate_registry

    verified = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    payload = {
        "schema": "delta-bedrani-claim-registry-v0.1",
        "project": {
            "repository": "Loofy147/Delta-bedrani",
            "branch": "feature/exchange-engine-v0",
            "verified_head": verified,
        },
        "claims": [
            {
                "claim_id": "X",
                "claim": "x",
                "status": "EXPERIMENTALLY_SUPPORTED",
                "evidence_class": "EXHAUSTIVE-FINITE",
                "scope": "test",
                "source_path": "tests/test_dmlib_oracle.py",
                "verification_path": "tests/test_dmlib_oracle.py",
                "verification_run": "github-actions:test",
                "verified_commit": verified,
                "disposition": "CONFIRMED",
                "limits": "finite",
            }
        ],
    }
    registry = tmp_path / "claims.json"
    registry.write_text(json.dumps(payload), encoding="utf-8")

    errors = validate_registry(registry, repo_root=ROOT, require_current_tree=True)
    assert errors == []
