"""Participant-local Streamlit workbench. No simulated cloud success path."""

import re
from pathlib import Path

import streamlit as st
from lab03_payment_agent.confirmation import memory_proposal, review, save
from lab03_payment_agent.domain import Request, digest, investigate
from lab03_payment_agent.live import LiveBackend, Settings, write_receipt, write_report
from lab03_payment_agent.recovery import reviewed_stopped_runs
from lab03_payment_agent.retained_response import recover as recover_retained_response

st.set_page_config(page_title="Agente de investigación de pagos", layout="wide")
st.title("Agente de investigación de pagos")
st.caption(
    "Prototipo del workshop con datos sintéticos. Requiere revisión humana; no está preparado para producción."
)
state = st.session_state


def disconnect():
    backend = state.pop("backend", None)
    if backend:
        backend.close()
    for key in ("result", "request_hash", "case_saved"):
        state.pop(key, None)


with st.sidebar:
    st.header("1. Conexión")
    session_path = st.text_input(
        "Archivo privado de sesión", placeholder="Ruta absoluta fuera del repositorio"
    )
    report_root = st.text_input(
        "Carpeta privada de evidencias",
        value=str(Path.home() / "KhipuPrivate" / "workshop3" / "evidence"),
    )
    with st.form("connect", clear_on_submit=True):
        db_password = st.text_input("Contraseña de la base de datos", type="password")
        wallet_password = st.text_input("Contraseña del wallet", type="password")
        st.caption(
            "Son distintas de tu contraseña OCI. Usa los valores decodificados de los secretos, no Base64."
        )
        connect = st.form_submit_button("Conectar y verificar preparación")
    if connect:
        candidate = None
        try:
            disconnect()
            settings = Settings.load(Path(session_path))
            candidate = LiveBackend(settings, db_password, wallet_password)
            candidate.readiness(reviewed_stopped_runs=reviewed_stopped_runs(settings))
            state.backend = candidate
            st.success("Identidad individual de base de datos verificada")
        except Exception as error:
            if candidate:
                candidate.close()
            detail = error.args[0] if error.args else None
            code = getattr(detail, "code", None)
            driver_codes = sorted(set(re.findall(r"\b(?:DPY|DPI|ORA|TNS)-\d{3,5}\b", str(error))))
            safe_code = ",".join(driver_codes) or (
                str(code) if isinstance(code, int) and code else "no disponible"
            )
            readiness_reasons = {
                "A native team run is still RUNNING; inspect server state before retry": (
                    "Conexión bloqueada: una ejecución anterior del agente sigue "
                    "marcada como RUNNING. El facilitador debe revisar la actividad antes de recuperarla. "
                    "No cambies las contraseñas ni repitas la investigación."
                ),
                "A previous investigation is active; verify server execution before recovery": (
                    "Conexión bloqueada: permanece el bloqueo de una investigación anterior. "
                    "Solicita al facilitador verificar la ejecución; no elimines el bloqueo."
                ),
                "Tool compilation errors": (
                    "Conexión bloqueada: una herramienta del workshop tiene errores de compilación. "
                    "Corrige y verifica tu ejercicio antes de investigar."
                ),
                "Agent team missing": (
                    "Conexión bloqueada: falta el equipo de agentes de tu asignación. "
                    "Solicita al facilitador revisar la preparación de tu asignación."
                ),
            }
            readiness_reason = (
                readiness_reasons.get(str(error)) if isinstance(error, ValueError) else None
            )
            if readiness_reason:
                st.warning(readiness_reason)
            st.error(
                "La conexión falló. Diagnóstico seguro: "
                + type(error).__name__
                + "; código de base de datos="
                + safe_code
                + ". Revisa la asignación privada y la preparación con el facilitador."
            )
        finally:
            db_password = wallet_password = None
    if st.button("Desconectar / iniciar una sesión nueva"):
        disconnect()
        st.rerun()

backend = state.get("backend")
if not backend:
    st.info(
        "Conecta con tu asignación individual. Verificar la preparación no realiza llamadas pagadas."
    )
    st.stop()

st.header("2. Memoria y evidencia")
if st.button("Recuperar memorias aprobadas (sin inferencia)"):
    try:
        records = backend.memories("payment idempotency")
        st.json([m.__dict__ for m in records])
        for memory in records:
            if memory.identifier == "payment-idempotency-approved":
                write_receipt(
                    Path(report_root),
                    backend.identity,
                    memory.source_run,
                    "memory_recovery",
                    {"recovered_after_connection": True, **memory.__dict__},
                )
        st.caption(
            "Después de guardar una memoria, reconecta y comprueba aquí su identificador y ejecución de origen (source_run)."
        )
    except Exception:
        st.error("No se pudieron recuperar las memorias. Contacta al facilitador.")

st.header("3. Investigación")
question_input = st.text_area(
    "Pregunta sobre el caso sintético",
    value="Investiga la idempotencia del pago y prepara una recomendación.",
)
question = (
    "Investigate payment idempotency and prepare a recommendation."
    if question_input == "Investiga la idempotencia del pago y prepara una recomendación."
    else question_input
)
with st.expander("Ver la pregunta que se envía al agente"):
    st.code(question, language=None)
    st.caption(
        "El ejemplo conserva la solicitud original en inglés para mantener la calibración y la trazabilidad."
    )
payment_id = st.selectbox("Pago sintético", ["PAY-104", "PAY-105", "PAY-106", "PAY-999"])
version = st.selectbox(
    "Versión del contrato",
    ["v2", "v1", "unspecified"],
    format_func=lambda value: "Sin especificar" if value == "unspecified" else value,
)
request = Request(question, payment_id, version)
request_hash = digest(request.__dict__)
with st.expander("Recuperar una respuesta completada sin otra ejecución pagada"):
    retained_run = st.text_input("Identificador de la ejecución completada")
    st.caption(
        "Úsalo después del diagnóstico del facilitador. Requiere el informe original y una "
        "tarea nativa exitosa para la misma pregunta, pago y versión seleccionados."
    )
    if st.button("Recuperar respuesta completada (sin inferencia)"):
        try:
            recovered = recover_retained_response(backend, request, Path(report_root), retained_run)
            state.result = recovered
            state.request_hash = request_hash
            state.pop("case_saved", None)
            st.rerun()
        except Exception:
            st.error(
                "No se pudo verificar la respuesta guardada. Conserva la evidencia y contacta al facilitador."
            )
paid = st.checkbox(
    "Autorizo el consumo de embeddings e inferencia del agente para esta ejecución.",
    key="paid-" + str(state.get("paid_generation", 0)),
)
if st.button("Ejecutar investigación", disabled=not paid):
    state.pop("case_saved", None)
    with st.spinner("Recuperando contexto y ejecutando el agente en ADB…"):
        state.result = investigate(backend, request)
        state.request_hash = request_hash
    try:
        write_report(state.result, Path(report_root), backend.identity)
    except Exception:
        st.warning(
            "La ejecución terminó, pero falló la exportación de evidencias. Descarga el resultado a continuación."
        )
    state.paid_generation = state.get("paid_generation", 0) + 1
    st.rerun()

result = state.get("result")
if result:
    st.header("4. Respuesta y trazabilidad")
    status_labels = {
        "answered": "Respondido",
        "requires_clarification": "Requiere aclaración",
        "insufficient_evidence": "Evidencia insuficiente",
        "conflict": "Conflicto",
        "error": "Error",
    }
    mode_labels = {
        "live": "Servicios OCI reales",
        "stored_oci_revalidation": "Respuesta OCI guardada y revalidada",
    }
    st.write("Estado:", status_labels.get(result.status, result.status))
    st.caption(
        "Modo de ejecución: " + mode_labels.get(result.execution_mode, result.execution_mode)
    )
    st.caption("Códigos técnicos: " + result.status + " · " + result.execution_mode)
    answer_messages = {
        "Synthetic payment not found. No case was proposed.": "No se encontró el pago sintético. No se propuso registrar un caso.",
        "Requests and payment events are required.": "Se necesitan solicitudes y eventos del pago como evidencia.",
        "Provide a question, a synthetic payment identifier and v1 or v2.": "Indica una pregunta, un identificador de pago sintético y la versión v1 o v2.",
        "The synthetic payment corpus does not support this topic.": "El corpus de pagos sintéticos no contiene evidencia sobre este tema.",
        "No contractual evidence passed retrieval validation.": "Ninguna evidencia contractual superó la validación de recuperación.",
        "An approved procedure and contractual evidence are required.": "Se requieren un procedimiento aprobado y evidencia contractual.",
        "Review the memory against the approved v2 procedure.": "Revisa la memoria frente al procedimiento aprobado para v2.",
        "The approved memory applies to v2, not this contract.": "La memoria aprobada corresponde a v2 y no a este contrato.",
        "Execution failed. Check readiness and retry explicitly; no automatic write occurred.": "La ejecución falló. Revisa la preparación con el facilitador antes de reintentar. No se guardaron registros automáticamente.",
    }
    if result.status == "answered":
        if result.answer.startswith("ESCALATE"):
            st.info("Recomendación: escalar el conflicto para investigación.")
        elif result.answer.startswith("NO_DUPLICATE_EVIDENCE"):
            st.info("No se encontró evidencia de duplicación en los hechos consultados.")
        st.caption(
            "La respuesta y las citas se conservan en su idioma original para mantener la evidencia exacta."
        )
    st.code(answer_messages.get(result.answer, result.answer), language=None)
    sources, memories, tools, metrics = st.tabs(
        ["Citas del contrato", "Procedimientos", "Resultados de herramientas", "Métricas"]
    )
    sources.json(result.citations)
    memories.json(result.memories)
    tools.json(result.tools)
    metrics.json(result.telemetry)
    import json

    st.download_button(
        "Descargar evidencia JSON", json.dumps(result.as_dict(), indent=2), "evidence.json"
    )
    current = state.get("request_hash") == request_hash
    if not current:
        st.warning(
            "Cambiaste los datos de entrada. No confirmes la propuesta anterior; revisa el alcance autorizado antes de otra ejecución."
        )
    if result.proposal and current:
        st.header("5. Revisión humana")
        st.json(result.proposal)
        case_hash = digest(result.proposal)
        approved_case = st.checkbox(
            "He revisado y apruebo este caso exacto.", key="case-" + case_hash
        )
        if st.button("Registrar caso", disabled=not approved_case):
            try:
                receipt = save(
                    backend,
                    backend.identity,
                    "case",
                    result.proposal,
                    review(backend.identity, "case", result.proposal),
                )
                state.case_saved = result.run_id
                if receipt.get("status") == "saved":
                    st.success("Caso registrado correctamente.")
                elif receipt.get("status") == "already_saved":
                    st.success("El caso ya estaba registrado. No se creó un duplicado.")
                st.json(receipt)
                write_receipt(
                    Path(report_root), backend.identity, result.run_id, "case_confirmation", receipt
                )
            except Exception:
                st.error(
                    "No se pudo confirmar el resultado del guardado. Solicita revisar el registro de escrituras antes de reintentar el mismo contenido."
                )
        if state.get("case_saved") == result.run_id:
            st.header("6. Aprobar una memoria de procedimiento reutilizable")
            proposal = memory_proposal(result)
            st.json(proposal)
            approved_memory = st.checkbox(
                "Apruebo este procedimiento y su procedencia.", key="memory-" + digest(proposal)
            )
            if st.button("Guardar memoria aprobada", disabled=not approved_memory):
                try:
                    receipt = save(
                        backend,
                        backend.identity,
                        "memory",
                        proposal,
                        review(backend.identity, "memory", proposal),
                    )
                    if receipt.get("status") == "saved":
                        st.success("Memoria aprobada guardada correctamente.")
                    elif receipt.get("status") == "already_saved":
                        st.success("La memoria ya estaba guardada. No se creó un duplicado.")
                    st.json(receipt)
                    write_receipt(
                        Path(report_root),
                        backend.identity,
                        result.run_id,
                        "memory_confirmation",
                        receipt,
                    )
                    st.success("Reconecta y recupera esta memoria desde una sesión nueva.")
                except Exception:
                    st.error(
                        "No se pudo confirmar el resultado del guardado. Solicita revisar el registro de escrituras; no cambies el contenido propuesto."
                    )

st.header("7. Evaluación")
st.markdown(
    "- Verifica la versión del contrato y las afirmaciones citadas.\n- Compara los identificadores, las claves de idempotencia y los hashes de las solicitudes.\n- Prueba PAY-105 y PAY-999 solo con autorización de consumo.\n- Usa v1 y una versión sin especificar para evaluar conflicto y aclaración, dentro del alcance autorizado.\n- Reconecta y recupera la memoria aprobada."
)
