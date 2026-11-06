"""Local participant dashboard; all workshop operations use actual OCI services."""

import os
import traceback
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from lab02_contract_rag.corpus import LAB_ROOT
from lab02_contract_rag.dashboard import (
    candidate_selection,
    expected_comparison,
    list_own_reports,
    load_own_report,
    workshop_cases,
)
from lab02_contract_rag.execution import execute_live
from lab02_contract_rag.live_validation import settings_from_environment
from lab02_contract_rag.local_pool import LocalParticipantPool
from lab02_contract_rag.participant import participant_id


def render_result(result):
    candidates, candidate_by_chunk = candidate_selection(result)
    is_ingestion = result["status"] == "ingested"
    if is_ingestion:
        st.subheader("Preparación del corpus sintético")
        st.caption(f"Ejecución: {result['run_id']} | Participante: {result['participant_id']}")
        st.success(
            "El corpus quedó preparado para consultas OCI. Esta actividad no formula una "
            "pregunta contractual ni solicita una respuesta de chat."
        )
        for limitation in result["limitations"]:
            st.write(limitation)
    else:
        st.subheader("Referencia del ejercicio vs. respuesta obtenida")
        st.caption(f"Pregunta: {result['question']}")
        st.caption(f"Ejecución: {result['run_id']} | Participante: {result['participant_id']}")
        comparison = expected_comparison(result)
        left, right = st.columns(2)
        with left:
            st.markdown("**Respuesta de referencia del ejercicio**")
            st.caption("Definida en la matriz antes de ejecutar OCI.")
            if comparison:
                case = comparison["case"]
                st.write(case["expected_answer"])
                st.caption(f"Estado esperado: {case['expected_status']}")
                st.write("Secciones requeridas: " + (", ".join(case["sections"]) or "No aplica"))
                st.write(
                    "Hechos requeridos: "
                    + (", ".join(case["required_terms"]) or "No inventar hechos")
                )
            else:
                st.info(
                    "No hay una respuesta de referencia para esta consulta personalizada. "
                    "Se requiere revisión humana."
                )
        with right:
            st.markdown("**Respuesta obtenida de OCI**")
            st.caption("Publicada por esta ejecución, después de validar sus citas.")
            st.write(result["status"])
            if result["answer"]:
                st.text(result["answer"])
            else:
                st.info("No hay una respuesta publicada del modelo para este resultado.")
            for limitation in result["limitations"]:
                st.write(limitation)
        st.divider()
        if comparison:
            assessment = comparison["assessment"]
            if assessment["passed"]:
                st.success(
                    "Las comprobaciones automáticas del contrato fueron aprobadas. "
                    "Revisa el texto y la evidencia reales a continuación."
                )
            else:
                st.error(
                    "No se cumple el contrato esperado. Inspecciona el resultado y las fuentes reales."
                )
            st.dataframe(
                [
                    {"Comprobación": key, "Observado": str(value)}
                    for key, value in assessment.items()
                    if key not in {"id", "expected_status"}
                ],
                hide_index=True,
            )
        st.warning(
            "Revisión humana pendiente: las comprobaciones automáticas y las citas son necesarias, "
            "pero debes confirmar que el extracto realmente sustenta la respuesta."
        )
    st.subheader("Ejecución de servicios")
    if result.get("execution_origin") == "application_control":
        st.info("Decisión de la aplicación: no se necesitó inferencia OCI. No es una respuesta del modelo.")
    elif result.get("cloud_executed"):
        st.caption(
            "Flujo OCI real: inspecciona operaciones de servicio, fallas y generación omitida."
        )
    else:
        st.error(
            "La ejecución OCI no se completó. Este reporte no es una validación cloud exitosa."
        )
    trace = result.get("service_trace", [])
    if trace:
        st.dataframe(trace, hide_index=True)
    telemetry = result.get("telemetry", {})
    a, b, c = st.columns(3)
    a.metric("Llamadas de embedding de consulta", telemetry.get("query_embedding_calls", 0))
    b.metric("Llamadas de chat", telemetry.get("chat_calls", 0))
    c.metric("Milisegundos totales", result.get("timings_ms", {}).get("total", 0))
    st.caption("Los conteos representan intentos. Que no haya uso de tokens reportado no significa consumo cero.")
    if telemetry.get("tokens"):
        st.write(telemetry["tokens"])
    st.subheader("Afirmaciones y evidencia verificable")
    for claim in result["claims"]:
        st.text(claim["text"])
        st.caption("Evidencia: " + ", ".join(claim["evidence_ids"]))
    for source in result["citations"]:
        with st.expander(source["label"]):
            st.code(source["excerpt"], language="markdown")
            st.caption(f"Fuente: {source['source_uri']}")
            st.caption(f"Fragmento: {source['chunk_id']} | Hash de contenido: {source['content_hash']}")
            candidate = candidate_by_chunk.get(source["chunk_id"])
            if candidate:
                st.caption(
                    "Métrica de recuperación de esta evidencia seleccionada: "
                    f"{candidate['score_type']} = {candidate['rank_value']:.4f}."
                )
    with st.expander("Candidatos recuperados y evidencia seleccionada"):
        st.caption(
            "Una menor cosine_distance indica un candidato vectorial más cercano. Una "
            "cobertura estructural de sección completa un aspecto solicitado ausente en los "
            "candidatos vectoriales; ninguna señal sustituye el respaldo semántico."
        )
        st.dataframe(
            [
                {
                    "Versión": e["contract_version"],
                    "Sección": e["section"],
                    "Posición": e["rank_value"],
                    "Método": e["method"],
                    "Métrica": e["score_type"],
                    "Seleccionada como evidencia": "Sí"
                    if e["selected_as_evidence"]
                    else "No",
                }
                for e in candidates
            ],
            hide_index=True,
        )


def close_local_pool() -> None:
    """Close only the current browser session's local participant pool."""
    holder = st.session_state.pop("local_participant_pool", None)
    if holder is not None:
        holder.close()


def local_pool(settings):
    """Return a pool that can only match the current participant target."""
    holder = st.session_state.get("local_participant_pool")
    if holder is not None and not holder.matches(settings):
        holder.close()
        holder = None
    if holder is None:
        holder = LocalParticipantPool(settings)
        st.session_state["local_participant_pool"] = holder
    return holder


def main():
    st.set_page_config(page_title="Khipu · Evidencia contractual", page_icon="📑", layout="wide")
    load_dotenv()
    st.title("Estudio de evidencia contractual")
    st.caption("Workshop 2 · ejecución OCI real · espacio de trabajo individual")
    try:
        assigned = participant_id(os.environ["LAB02_PARTICIPANT_ID"])
        root = Path(os.getenv("LAB02_REPORT_ROOT", str(LAB_ROOT.parents[1] / "artifacts/lab02")))
        reports = list_own_reports(root, assigned)
    except Exception:
        st.error(
            "Primero carga tu sesión privada asignada. La selección de participantes y las "
            "cuentas compartidas no están disponibles."
        )
        st.stop()
    # A rerun after an environment change cannot keep another participant's in-memory result.
    if st.session_state.get("bound_participant") != assigned:
        st.session_state.pop("last_result", None)
        close_local_pool()
    st.session_state["bound_participant"] = assigned
    st.sidebar.header("Mi espacio de trabajo")
    st.sidebar.write(f"Participante: {assigned}")
    st.sidebar.write(f"Región: {os.getenv('OCI_REGION', 'us-chicago-1')}")
    st.sidebar.success("Solo servicios OCI")
    st.sidebar.caption(
        "Sin fallback automático, respuestas de ejemplo ni simulador. Un proceso local por participante."
    )
    query_tab, history_tab = st.tabs(["Ejecutar e inspeccionar", "Mi historial de ejecuciones"])
    with query_tab:
        cases = workshop_cases()
        selection = st.selectbox(
            "Pregunta del workshop",
            [c["id"] for c in cases] + ["Personalizada"],
            format_func=lambda key: next(
                (f"{c['id']} · {c['question']}" for c in cases if c["id"] == key), key
            ),
        )
        if selection == "Personalizada":
            question = st.text_area("Pregunta sobre contrato sintético", max_chars=4000)
            target = st.selectbox("Versión objetivo", ["Desde la pregunta", "v1", "v2"])
            version = None if target == "Desde la pregunta" else target
        else:
            question = next(c["question"] for c in cases if c["id"] == selection)
            version = None
        st.caption(
            "Usa únicamente preguntas sintéticas. Nunca ingreses credenciales, contratos de "
            "clientes ni datos personales."
        )
        with st.form("live_request", clear_on_submit=True):
            action = st.radio("Acción", ["Preguntar usando OCI", "Preparar mi corpus sintético"])
            db_password = st.text_input("Mi contraseña de base de datos", type="password")
            wallet_password = st.text_input("Contraseña del wallet", type="password")
            approve = st.checkbox("Confirmo la inferencia OCI con costo aprobada para esta solicitud.")
            load = st.checkbox("Autorizo insertar fragmentos sintéticos faltantes en mi propio schema.")
            submitted = st.form_submit_button("Ejecutar flujo OCI real", type="primary")
        if submitted:
            st.session_state.pop("last_result", None)
            if not approve:
                st.error("Confirma la inferencia OCI con costo antes de ejecutar. No se envió ninguna solicitud.")
            else:
                ui_stage = "configuración local"
                try:
                    ingest = action == "Preparar mi corpus sintético"
                    settings = settings_from_environment(require_calibration=not ingest)
                    if settings.participant_id != assigned:
                        raise ValueError("La identidad de sesión cambió")
                    ui_stage = "sesión local ADB"
                    pool = local_pool(settings)
                    if not pool.ready and (not db_password or not wallet_password):
                        raise ValueError(
                            "Ingresa las contraseñas privadas para abrir la sesión ADB local inicial."
                        )
                    if ingest and not load:
                        raise ValueError("Se requiere autorización explícita de carga sintética.")
                    ui_stage = "flujo OCI"
                    with st.spinner("Ejecutando contra los servicios OCI asignados..."):
                        result = execute_live(
                            settings,
                            question or "Prepare the synthetic corpus",
                            confirm_inference=True,
                            confirm_load=load,
                            ingest_only=ingest,
                            version=version,
                            database_password=db_password,
                            wallet_password=wallet_password,
                            output_root=root,
                            connection_factory=lambda: pool.acquire(
                                database_password=db_password or None,
                                wallet_password=wallet_password or None,
                            ),
                        )
                    ui_stage = "registro del resultado"
                    st.session_state["last_result"] = result
                except ValueError as exc:
                    st.error(str(exc))
                except Exception as exc:
                    # Keep the dashboard safe for participant use: expose only the local
                    # exception class, never a provider response, connection string or secret.
                    workspace_frames = [
                        frame
                        for frame in traceback.extract_tb(exc.__traceback__)
                        if "lab02_contract_rag" in frame.filename.replace("\\", "/")
                    ]
                    location = "not_available"
                    if workspace_frames:
                        frame = workspace_frames[-1]
                        location = f"{Path(frame.filename).name}:{frame.lineno}"
                    st.error(
                        "La ejecución falló antes de completar el flujo OCI. "
                        f"Código técnico seguro: {type(exc).__name__}. "
                        f"Etapa: {ui_stage}. "
                        f"Ubicación local: {location}. "
                        "Revisa configuración, calibración, aprobaciones y acceso al servicio. "
                        "No se usó fallback."
                    )
            # The clear-on-submit form resets credential widgets; never cache connections/passwords.
            db_password = wallet_password = ""
        holder = st.session_state.get("local_participant_pool")
        if holder is not None and holder.ready:
            st.caption("Sesión ADB local reutilizable activa para este participante. Cierra el dashboard para liberarla.")
        if "last_result" in st.session_state:
            render_result(st.session_state["last_result"])
    with history_tab:
        if st.button("Actualizar mi historial"):
            st.rerun()
        if not reports:
            st.info(
                "Aún no hay reportes de flujos reales. Se excluyen ejemplos de desarrollo y "
                "fixtures simulados."
            )
        else:
            chosen = st.selectbox("Mi ejecución guardada", reports, format_func=lambda p: p.parent.name)
            try:
                render_result(load_own_report(root, assigned, chosen))
            except Exception:
                st.error("El reporte no pudo verificarse para este participante.")


if __name__ == "__main__":
    main()
