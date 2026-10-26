"""Tests for the participant-facing, side-effect-free runner interface."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIRECTORY = REPOSITORY_ROOT / "labs" / "lab01_agent_memory" / "scripts"
CONFIG_DIRECTORY = REPOSITORY_ROOT / "labs" / "lab01_agent_memory" / "config"
RUNNER_PATH = SCRIPTS_DIRECTORY / "run_participant_sdk_lab.py"
LAUNCHER_PATH = SCRIPTS_DIRECTORY / "run_participant_live.ps1"


def _load_runner_module():
    spec = importlib.util.spec_from_file_location("participant_runner", RUNNER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_preflight_arguments_do_not_require_an_evidence_path(monkeypatch) -> None:
    runner = _load_runner_module()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_participant_sdk_lab.py",
            "--bundle",
            "bundle.json",
            "--team-code",
            "T01",
            "--participant-code",
            "P01",
            "--preflight",
        ],
    )

    args = runner.parse_args()

    assert args.preflight is True
    assert args.output_path is None


def test_memory_exercise_arguments_select_a_safe_procedure(monkeypatch) -> None:
    runner = _load_runner_module()
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "run_participant_sdk_lab.py",
            "--bundle",
            "bundle.json",
            "--team-code",
            "T01",
            "--participant-code",
            "P01",
            "--memory-exercise",
            "payment-idempotency",
            "--output-path",
            "memory-evidence.json",
        ],
    )

    args = runner.parse_args()

    assert args.memory_exercise == "payment-idempotency"
    assert args.confirm_live_inference is False


def test_custom_procedure_arguments_do_not_acknowledge_live_inference(monkeypatch) -> None:
    runner = _load_runner_module()
    monkeypatch.setattr(sys, "argv", [
        "run_participant_sdk_lab.py", "--bundle", "bundle.json", "--team-code", "T01",
        "--participant-code", "P01", "--custom-procedure", "procedure.json",
        "--output-path", "custom-evidence.json",
    ])
    args = runner.parse_args()
    assert args.custom_procedure.name == "procedure.json"
    assert args.confirm_live_inference is False


def test_progress_marker_is_clear_for_participants(capsys) -> None:
    runner = _load_runner_module()

    runner.print_step(4, "COMPARE", "making exactly two OCI Generative AI calls")

    assert capsys.readouterr().out == (
        "LAB01_STEP 4/4 COMPARE: making exactly two OCI Generative AI calls\n"
    )


def test_preflight_checks_model_access_before_reporting_success(monkeypatch, capsys) -> None:
    runner = _load_runner_module()
    events: list[str] = []

    class FakeMemory:
        def list_memories(self, *, user_id: str, limit: int) -> list[object]:
            events.append(f"memory:{user_id}:{limit}")
            return []

    class FakePool:
        def close(self) -> None:
            events.append("pool:closed")

    monkeypatch.setattr(runner, "create_runtime_memory", lambda: (FakeMemory(), FakePool()))
    monkeypatch.setattr(
        runner, "validate_tenancy_binding", lambda: events.append("tenancy:checked")
    )
    monkeypatch.setattr(runner, "validate_model_access", lambda: events.append("model:checked"))

    runner.run_preflight(team_code="T01", participant_code="P01")

    assert events == ["tenancy:checked", "memory:t01:p01:1", "pool:closed", "model:checked"]
    output = capsys.readouterr().out
    assert "LAB01_OCI_TENANCY_MATCH True" not in output
    assert "LAB01_PREFLIGHT_MODEL_ACCESS True" in output
    assert "LAB01_PREFLIGHT_COMPLETE" in output


def test_participant_launcher_uses_private_environment_and_preflight() -> None:
    launcher = LAUNCHER_PATH.read_text(encoding="utf-8")

    assert "Require-EnvironmentValue" in launcher
    assert "LAB01_PREFLIGHT_NO_INFERENCE" in launcher
    assert "--confirm-live-inference" in launcher
    assert "-MemoryExercise" in launcher
    assert "-CustomProcedure" in launcher
    assert "$Preflight.IsPresent" in launcher
    assert "$ContextExperiment.IsPresent" in launcher
    assert "zero OCI Generative AI requests" in launcher
    memory_branch = launcher.index("if ($MemoryExercise)")
    profile_ready = launcher.index("LAB01_OCI_PROFILE_READY True")
    assert memory_branch < profile_ready
    assert "session validate" not in launcher
    assert "iam region list" not in launcher
    assert "exactly two on-demand OCI Generative AI requests" in launcher
    assert "OAM_T01_P01" not in launcher
    assert "KHIPU_LAB01_MEM" not in launcher


def test_private_session_template_exposes_only_configuration_references() -> None:
    template = (CONFIG_DIRECTORY / "participant-session.ps1.example").read_text(
        encoding="utf-8"
    )

    for variable in (
        "OCI_CONFIG_FILE",
        "OCI_CONFIG_PROFILE",
        "LAB01_TENANCY_NAME",
        "LAB01_TENANCY_ID",
        "OCI_COMPARTMENT_ID",
        "LAB01_CHAT_MODEL_ID",
        "LAB01_WALLET_DIR",
        "LAB01_DB_USER",
        "LAB01_DB_DSN",
        "LAB01_MEMORY_SCHEMA_OWNER",
        "LAB01_MEMORY_STORE_ID",
    ):
        assert variable in template

    assert "DB_PASSWORD" not in template
    assert "WALLET_PASSWORD" not in template
