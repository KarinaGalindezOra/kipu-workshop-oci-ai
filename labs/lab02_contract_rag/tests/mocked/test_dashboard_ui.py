"""Streamlit UI contract tests; never claimed as real OCI validation."""

from types import SimpleNamespace

import pytest
from lab02_contract_rag import execution, live_validation
from lab02_contract_rag.corpus import LAB_ROOT

streamlit_testing = pytest.importorskip("streamlit.testing.v1")


def test_dashboard_requires_assigned_identity(monkeypatch):
    monkeypatch.delenv("LAB02_PARTICIPANT_ID", raising=False)
    # Do not read a developer's populated environment file in this isolated UI test.
    monkeypatch.setattr("dotenv.load_dotenv", lambda *a, **kw: None)
    app = streamlit_testing.AppTest.from_file(str(LAB_ROOT / "ui/app.py")).run()
    assert not app.exception
    assert any("sesión privada asignada" in e.value for e in app.error)
    assert not app.selectbox


def test_dashboard_opens_without_network_and_has_no_simulator(monkeypatch, tmp_path):
    monkeypatch.setenv("LAB02_PARTICIPANT_ID", "p001")
    monkeypatch.setenv("LAB02_REPORT_ROOT", str(tmp_path))
    monkeypatch.setattr(
        execution, "execute_live", lambda *a, **kw: pytest.fail("No click, no calls")
    )
    app = streamlit_testing.AppTest.from_file(str(LAB_ROOT / "ui/app.py")).run()
    assert not app.exception
    assert [tab.label for tab in app.tabs] == ["Ejecutar e inspeccionar", "Mi historial de ejecuciones"]
    assert len(app.text_input) == 2 and all(w.proto.type == 1 for w in app.text_input)
    options = app.selectbox[0].options
    assert not any("T16" in option or "T17" in option for option in options)
    assert not any(w.label == "Participant" for w in app.selectbox)


def test_dashboard_no_consent_never_calls_services(monkeypatch, tmp_path):
    monkeypatch.setenv("LAB02_PARTICIPANT_ID", "p001")
    monkeypatch.setenv("LAB02_REPORT_ROOT", str(tmp_path))
    monkeypatch.setattr(execution, "execute_live", lambda *a, **kw: pytest.fail("No consent"))
    app = streamlit_testing.AppTest.from_file(str(LAB_ROOT / "ui/app.py")).run()
    app.button[0].click().run()
    assert not app.exception
    assert any("Confirma la inferencia OCI con costo" in e.value for e in app.error)


def test_dashboard_renders_expected_observed_and_application_provenance(monkeypatch, tmp_path):
    monkeypatch.setenv("LAB02_PARTICIPANT_ID", "p001")
    monkeypatch.setenv("LAB02_REPORT_ROOT", str(tmp_path))
    monkeypatch.setattr(
        live_validation,
        "settings_from_environment",
        lambda **kw: SimpleNamespace(participant_id="p001"),
    )
    received = []

    def ui_double(settings, question, **kwargs):
        received.append(kwargs)
        return execution.control_result("How do I update the status?", "p001")

    monkeypatch.setattr(execution, "execute_live", ui_double)
    app = streamlit_testing.AppTest.from_file(str(LAB_ROOT / "ui/app.py")).run()
    app.text_input[0].set_value("private-test-password")
    app.text_input[1].set_value("private-test-wallet")
    app.checkbox[0].check()
    app.button[0].click().run()
    assert not app.exception
    assert received and received[0]["confirm_inference"] is True
    assert any("Referencia del ejercicio vs. respuesta obtenida" == e.value for e in app.subheader)
    assert any("Decisión de la aplicación" in e.value for e in app.info)
    assert "private-test-password" not in str(app.session_state["last_result"])
