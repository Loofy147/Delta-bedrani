import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_claim_registry_validator_accepts_current_registry():
    from tools.verify_claim_registry import validate_registry

    errors = validate_registry(
        ROOT / "evidence" / "claims-v0.1.json",
        repo_root=ROOT,
        require_current_tree=False,
    )
    assert errors == []


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


def test_claim_registry_validator_detects_changed_evidence_path(tmp_path):
    from tools.verify_claim_registry import validate_registry

    git = lambda *args: subprocess.check_output(
        ["git", *args], cwd=tmp_path, text=True
    ).strip()

    subprocess.run(["git", "init"], cwd=tmp_path, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "evidence.txt").write_text("v1\n", encoding="utf-8")
    subprocess.run(["git", "add", "evidence.txt"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "v1"], cwd=tmp_path, check=True, stdout=subprocess.DEVNULL)
    verified = git("rev-parse", "HEAD")

    (tmp_path / "evidence.txt").write_text("v2\n", encoding="utf-8")
    subprocess.run(["git", "add", "evidence.txt"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "v2"], cwd=tmp_path, check=True, stdout=subprocess.DEVNULL)

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
                "source_path": "evidence.txt",
                "verification_path": "evidence.txt",
                "verification_run": "github-actions:test",
                "verified_commit": verified,
                "disposition": "CONFIRMED",
                "limits": "finite",
            }
        ],
    }
    registry = tmp_path / "claims.json"
    registry.write_text(json.dumps(payload), encoding="utf-8")

    errors = validate_registry(registry, repo_root=tmp_path, require_current_tree=True)
    assert any("claim X evidence paths changed" in error for error in errors)


def test_claim_registry_cli_passes():
    completed = subprocess.run(
        [sys.executable, "tools/verify_claim_registry.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
