"""Participant-local Streamlit workbench. No simulated cloud success path."""

import re
from dataclasses import replace
from pathlib import Path

import streamlit as st
from lab03_payment_agent.agent_builder import TEAM, AgentBlueprint, register
from lab03_payment_agent.confirmation import memory_proposal, review, save
from lab03_payment_agent.domain import Request, digest, investigate
from lab03_payment_agent.live import LiveBackend, Settings, write_receipt, write_report
from lab03_payment_agent.recovery import ensure_paid_execution_allowed, reviewed_stopped_runs
from lab03_payment_agent.retained_response import recover as recover_retained_response
from lab03_payment_agent.ui_panels import render_answer, render_metrics, render_rag, render_tools
from lab03_payment_agent.workbench import contract_library, load_local_report, questions

st.set_page_config(
    page_title="Workshop 3 · Construye tu agente", layout="wide", initial_sidebar_state="collapsed"
)
st.title("Workshop 3 · Construye tu agente de pagos")
st.markdown(
    "**Objetivo:** construir un agente, consultarlo en lenguaje natural y verificar sus contratos, herramientas y memoria."
)
st.caption(
    "Prototipo del workshop con datos sintéticos. Requiere revisión humana; no está preparado para producción."
)
state = st.session_state
if "pending_original_question" in state:
    state.query_text = state.pop("pending_original_question")


def disconnect():
    backend = state.pop("backend", None)
    if backend:
        backend.close()
    for key in ("result", "request_hash", "case_saved", "current_memories", "registered_team"):
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
            preparation = candidate.readiness(
                reviewed_stopped_runs=reviewed_stopped_runs(settings), require_team=False
            )
            state.agent_ready = preparation["agent_ready"]
            state.corpus_inventory = candidate.corpus_inventory()
            state.corpus_ready = sum(
                item["indexed_chunks"] for item in state.corpus_inventory
            ) == len(contract_library(settings.manifest_name))
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
        "Puedes explorar el constructor y el corpus sin conectarte. Las consultas reales y el registro del agente requieren tu asignación individual."
    )

builder_tab, query_tab, rag_tab, memory_tab, evaluation_tab = st.tabs(
    ["1. Construir mi agente", "2. Consultar", "3. Evidencia RAG", "4. Memoria", "5. Evaluar"]
)


def operation_allowed():
    if not backend:
        return False
    try:
        ensure_paid_execution_allowed(backend.settings)
        return True
    except Exception:
        return False


def source_result():
    return state.get("result") or state.get("inspection_result")


def use_question():
    selected = next((item for item in questions() if item["id"] == state.question_example), None)
    if selected:
        state.query_text = selected["question"]
        state.payment_choice = selected["payment_id"]
        state.version_choice = selected["version"]


with builder_tab:
    st.header("Define qué agente vas a construir")
    st.write(
        "Un agente combina un objetivo, instrucciones, herramientas y una tarea. En este laboratorio lo registrarás con Select AI Agent en tu esquema ADB."
    )
    st.markdown(
        "**Tu diseño → herramientas registradas → agente y tarea → equipo ejecutable en ADB.**"
    )
    with st.form("blueprint_form"):
        goal = st.text_area(
            "Objetivo de mi agente",
            value="Investigar reintentos de pagos sintéticos y proponer una recomendación respaldada por hechos y contrato.",
            max_chars=1500,
        )
        role = st.text_area(
            "Instrucciones que debe respetar",
            value="Soy un investigador de pagos. Consulto hechos observables, contrasto el contrato vigente y explicito cuándo falta evidencia. Uso solo los datos del participante asignado.",
            max_chars=1500,
        )
        selected_tools = st.multiselect(
            "Herramientas disponibles",
            ["get_payment", "get_payment_events", "find_related_requests"],
            default=["get_payment", "get_payment_events", "find_related_requests"],
        )
        if st.form_submit_button("Generar definición revisable"):
            try:
                blueprint = AgentBlueprint(goal, role, tuple(selected_tools))
                blueprint.validate()
                state.blueprint = blueprint
            except ValueError:
                st.error(
                    "Completa el objetivo y las instrucciones; esta investigación requiere las tres herramientas de consulta."
                )
    blueprint = state.get("blueprint")
    if blueprint:
        st.dataframe(
            [{"Objeto": kind, "Nombre en ADB": name} for kind, name, _ in blueprint.objects()],
            hide_index=True,
            width="stretch",
        )
        st.caption(
            "Se crearán seis objetos de tu esquema: tres herramientas, un agente, una tarea y un equipo. Se reutiliza el perfil preparado; no se conceden permisos ni se ejecuta el modelo."
        )
        with st.expander("Inspeccionar instrucciones y SQL que construyen el agente"):
            st.json(
                {"goal": blueprint.goal, "role": blueprint.role, "tools": list(blueprint.tools)}
            )
            st.code(blueprint.sql(), language="sql")
        st.download_button(
            "Descargar definición SQL", blueprint.sql(), "my_payment_agent.sql", mime="text/plain"
        )
        approved_blueprint = st.checkbox(
            "He revisado y autorizo crear estos seis objetos en mi esquema.",
            key="build-" + blueprint.fingerprint,
        )
        if st.button(
            "Registrar mi agente en ADB", disabled=not (operation_allowed() and approved_blueprint)
        ):
            try:
                receipt = register(backend, blueprint, blueprint.fingerprint)
                backend.settings = replace(backend.settings, agent_team=TEAM)
                state.registered_team = TEAM
                state.agent_ready = True
                state.builder_receipt = receipt
                st.success(
                    "Tu agente, su tarea, sus herramientas y su equipo quedaron registrados y verificados en ADB."
                )
            except Exception as error:
                st.error(
                    "El registro no terminó. Conserva la definición y solicita revisar los objetos antes de repetir; no se eliminará nada automáticamente."
                )
                st.caption("Clase segura: " + type(error).__name__)
        if state.get("builder_receipt"):
            st.json(state.builder_receipt)
    if backend and st.button("Inspeccionar equipos registrados (sin inferencia)"):
        try:
            state.agent_inventory = backend.agent_inventory()
        except Exception:
            st.error("No se pudo consultar el inventario de tu esquema.")
    if state.get("agent_inventory"):
        st.dataframe(state.agent_inventory, hide_index=True, width="stretch")
    st.caption(
        "La definición local no acredita un registro en ADB. El botón de registro solo se habilita con conexión y autorización; la nueva edición requiere un piloto de compatibilidad."
    )

with query_tab:
    st.header("Haz una consulta en lenguaje natural")
    st.write(
        "Pregunta sobre el pago seleccionado, sus reintentos y las cláusulas del contrato. La identidad proviene de tu conexión."
    )
    examples = {item["id"]: item for item in questions()}
    st.selectbox(
        "Ejemplos de preguntas",
        ["custom", *examples],
        format_func=lambda key: (
            "Escribe tu propia consulta" if key == "custom" else examples[key]["question"]
        ),
        key="question_example",
        on_change=use_question,
    )
    question = st.text_area(
        "Tu consulta",
        value="¿Por qué PAY-104 debe escalarse y qué evidencia lo demuestra?",
        key="query_text",
    )
    left, right = st.columns(2)
    payment_id = left.selectbox(
        "Pago sintético", ["PAY-104", "PAY-105", "PAY-106", "PAY-999"], key="payment_choice"
    )
    version = right.selectbox(
        "Versión del contrato",
        ["v2", "v1", "unspecified"],
        key="version_choice",
        format_func=lambda value: "Sin especificar" if value == "unspecified" else value,
    )
    request = Request(question, payment_id, version)
    request_hash = digest(request.__dict__)
    settings = getattr(backend, "settings", None)
    research_ready = bool(
        settings
        and settings.manifest_name == "research_contracts.json"
        and settings.agent_team == TEAM
        and state.get("agent_ready", False)
        and state.get("corpus_ready", False)
    )
    if settings:
        st.caption(
            "Equipo configurado: " + settings.agent_team + " · Corpus: " + settings.corpus_id
        )
    if not research_ready:
        st.info(
            "Para ejecutar esta edición, el facilitador debe preparar y calibrar el corpus ampliado y tú debes registrar tu agente. Los informes anteriores siguen disponibles en Evaluar."
        )
    paid = st.checkbox(
        "Autorizo el consumo de embeddings e inferencia del agente para esta ejecución.",
        key="paid-" + str(state.get("paid_generation", 0)),
    )
    if st.button(
        "Enviar consulta al agente", disabled=not (research_ready and operation_allowed() and paid)
    ):
        state.pop("case_saved", None)
        with st.status("Preparando la investigación…", expanded=True) as progress:

            def show_stage(stage):
                labels = {
                    "memory": "1/4 · Recuperando memoria aprobada",
                    "retrieval": "2/4 · Buscando cláusulas con RAG",
                    "agent": "3/4 · Ejecutando agente y herramientas",
                    "validation": "4/4 · Verificando hechos y citas",
                }
                progress.update(label=labels[stage])
                st.write(labels[stage])

            state.result = investigate(backend, request, observer=show_stage)
            state.request_hash = request_hash
            state.last_request = request.__dict__.copy()
            progress.update(
                label="Investigación terminada",
                state="complete" if state.result.status == "answered" else "error",
            )
        try:
            write_report(state.result, Path(report_root), backend.identity)
        except Exception:
            st.warning("No se pudo exportar el informe. Descarga la evidencia antes de cerrar.")
        state.paid_generation = state.get("paid_generation", 0) + 1
        st.rerun()
    result = source_result()
    verified = state.get("result") is not None
    if result:
        original = result.telemetry.get("original_execution", result.telemetry)
        question_record = original.get("request", state.get("last_request", {}))
        with st.chat_message("user"):
            st.write(
                question_record.get(
                    "question", "Pregunta original no incluida en este informe anterior."
                )
            )
        with st.chat_message("assistant"):
            render_answer(result, verified)
        render_tools(result)
        current = state.get("request_hash") == request_hash
        if verified and not current:
            st.warning(
                "Cambiaste los datos de entrada. No confirmes la propuesta anterior; recupera su pregunta exacta o solicita una nueva ejecución autorizada."
            )
        if verified and backend and result.proposal and current:
            st.subheader("Revisión humana del caso")
            st.json(result.proposal)
            approved_case = st.checkbox(
                "He revisado y apruebo este caso exacto.", key="case-" + digest(result.proposal)
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
                    st.success(
                        "Caso registrado correctamente."
                        if receipt["status"] == "saved"
                        else "El caso ya estaba registrado. No se creó un duplicado."
                    )
                    st.json(receipt)
                    write_receipt(
                        Path(report_root),
                        backend.identity,
                        result.run_id,
                        "case_confirmation",
                        receipt,
                    )
                except Exception:
                    st.error(
                        "No se pudo confirmar el guardado. Conserva el contenido y solicita auditar su clave antes de reintentar."
                    )

with rag_tab:
    st.header("Inspecciona el RAG")
    st.write("Aquí distingues el contrato de los hechos del pago y de las memorias aprendidas.")
    library_choice = st.radio(
        "Biblioteca documental",
        ["research_contracts.json", "contracts.json"],
        format_func=lambda name: (
            "Corpus ampliado propuesto · 12 cláusulas"
            if name == "research_contracts.json"
            else "Corpus anterior · 2 cláusulas"
        ),
        horizontal=True,
    )
    library = contract_library(library_choice)
    st.caption(
        "Esta biblioteca es contenido local del repositorio. Su presencia no significa que ya esté indexada en tu ADB."
    )
    filter_text = st.text_input("Explorar cláusulas por texto (búsqueda local, sin embeddings)")
    for item in library:
        if (
            filter_text
            and filter_text.casefold() not in (item["text"] + item.get("section", "")).casefold()
        ):
            continue
        with st.expander(
            item["version"] + " · " + item.get("section", "Idempotency") + " · " + item["id"]
        ):
            st.write(item["text"])
            if item.get("source_file"):
                st.caption(
                    f"Documento: {item['source_file']} · líneas {item['line_start']}–{item['line_end']}"
                )
    if backend and st.button("Comprobar fragmentos indexados en mi corpus (sin inferencia)"):
        try:
            state.corpus_inventory = backend.corpus_inventory()
        except Exception:
            st.error("No se pudo verificar el corpus en ADB.")
    if state.get("corpus_inventory") is not None:
        st.dataframe(state.corpus_inventory, hide_index=True, width="stretch")
    result = source_result()
    if result:
        render_rag(result)

with memory_tab:
    st.header("Qué recuerda el agente entre sesiones")
    st.write(
        "La memoria conserva procedimientos aprobados. El contrato determina la regla vigente; las herramientas aportan hechos actuales."
    )
    if st.button("Recuperar memorias aprobadas (sin inferencia)", disabled=backend is None):
        try:
            state.current_memories = [
                item.__dict__ for item in backend.memories("payment idempotency")
            ]
            for item in state.current_memories:
                if item["identifier"] == "payment-idempotency-approved":
                    write_receipt(
                        Path(report_root),
                        backend.identity,
                        item["source_run"],
                        "memory_recovery",
                        {"recovered_after_connection": True, **item},
                    )
        except Exception:
            st.error("No se pudo recuperar la memoria. Solicita revisar tu asignación.")
    result = source_result()
    memories = state.get("current_memories", result.memories if result else [])
    for item in memories:
        with st.container(border=True):
            st.markdown("**" + item["identifier"] + "** · " + item["version"])
            st.write(item["content"])
            st.caption(
                "Procedencia: "
                + item["source_run"]
                + " · Aprobada: "
                + ("Sí" if item["approved"] else "No")
            )
    if result:
        if result.memory_references:
            st.write("Memorias citadas explícitamente por el agente:", result.memory_references)
        else:
            st.caption(
                "Este informe no registra referencias explícitas del agente a memorias. Recuperar una memoria demuestra disponibilidad, no una mejora causal de la respuesta."
            )
    if (
        result
        and backend
        and state.get("result") is not None
        and state.get("case_saved") == result.run_id
        and state.get("request_hash") == request_hash
    ):
        st.subheader("Aprueba una lección reutilizable")
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
                st.success(
                    "Memoria aprobada guardada correctamente."
                    if receipt["status"] == "saved"
                    else "La memoria ya estaba guardada. No se creó un duplicado."
                )
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
                    "No se pudo confirmar el guardado. Solicita revisar el registro antes de reintentar."
                )
    st.caption(
        "Para demostrar persistencia: desconecta, reconecta y busca el identificador y la ejecución de origen de la lección aprobada."
    )

with evaluation_tab:
    st.header("Mide y contrasta el resultado")
    with st.expander(
        "Abrir un informe privado guardado (sin conexión ni inferencia)", expanded=not backend
    ):
        report_path = st.text_input("Ruta absoluta del informe JSON")
        if st.button("Abrir informe local"):
            try:
                state.inspection_result = load_local_report(Path(report_path))
                state.pop("result", None)
                state.pop("case_saved", None)
                st.rerun()
            except Exception:
                st.error(
                    "No se pudo abrir un informe válido fuera del repositorio. No compartas archivos de sesión o credenciales."
                )
    result = source_result()
    if result:
        render_metrics(result, state.get("result") is not None)
        import json

        st.download_button(
            "Descargar evidencia JSON", json.dumps(result.as_dict(), indent=2), "evidence.json"
        )
    else:
        st.info(
            "Las métricas aparecerán después de una ejecución real o al abrir un informe guardado. No se muestran números simulados."
        )
    st.dataframe(
        [
            {
                "Escenario": item["purpose"],
                "Pago": item["payment_id"],
                "Versión": item["version"],
                "Estado esperado": item["expected"],
            }
            for item in questions()
        ],
        hide_index=True,
        width="stretch",
    )
    st.caption(
        "Cada escenario real requiere autorización de consumo. La tabla describe expectativas; no acredita pruebas ejecutadas."
    )
    with st.expander("Recuperar una respuesta completada sin otra ejecución pagada"):
        retained_run = st.text_input("Identificador de la ejecución completada")
        original_question = st.text_input(
            "Pregunta exacta de la ejecución original",
            value="Investigate payment idempotency and prepare a recommendation.",
        )
        if st.button("Recuperar respuesta completada (sin inferencia)", disabled=backend is None):
            try:
                original_request = Request(original_question, payment_id, version)
                recovered = recover_retained_response(
                    backend, original_request, Path(report_root), retained_run
                )
                state.result = recovered
                state.request_hash = digest(original_request.__dict__)
                state.last_request = original_request.__dict__.copy()
                state.pending_original_question = original_question
                state.pop("case_saved", None)
                st.rerun()
            except Exception:
                st.error(
                    "No se pudo revalidar la respuesta contra la tarea, herramientas y fuentes de ADB. Conserva los informes."
                )
