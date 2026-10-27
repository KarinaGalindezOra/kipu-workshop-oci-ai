"""Visual participant experience for Lab 1 Decision Memory and Context Isolation."""

# ruff: noqa: E501

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st
from lab01_agent_memory.custom_procedure_evidence import load_custom_procedure_evidence
from lab01_agent_memory.demo import build_report
from lab01_agent_memory.experiment_evidence import load_context_experiment_evidence
from lab01_agent_memory.live_evidence import load_live_evidence
from lab01_agent_memory.participant_evidence import load_participant_evidence
from lab01_agent_memory.scenario import GUIDELINES

APP_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
EXAMPLE_EVIDENCE_PATH = APP_ROOT / "data" / "lab01-live-evidence.example.json"
LIVE_EVIDENCE_PATH = REPOSITORY_ROOT / "artifacts" / "lab01" / "facilitator" / "oci-isolation-evidence.json"
PARTICIPANT_EVIDENCE_DIRECTORY = REPOSITORY_ROOT / "artifacts" / "lab01"

TEAM_LABELS = {
    "team-01": "Team 01 - Payments API",
    "team-02": "Team 02 - Integration Delivery",
}

LAB_STEPS = (
    ("01", "Recuperar", "Selecciona el equipo y trae solo la decisión pertinente."),
    ("02", "Aislar", "Comprueba que el otro equipo no aporta contexto."),
    ("03", "Medir", "Compara tokens reportados por OCI para ambos diseños de contexto."),
)

QUESTION_OPTIONS = (
    "¿Cómo procesamos una solicitud de pago repetida para el contrato de API v2?",
    "¿Qué verificamos antes de proponer un cambio de compatibilidad de la API?",
    "¿Qué evidencia debe conservar una decisión de integración para una auditoría?",
)

GUIDELINE_DISPLAY_CONTENT = {
    "payment-idempotency": (
        "Para operaciones de pago, exige una clave de idempotencia, conserva el identificador "
        "original de la solicitud y rechaza una repetición con una carga distinta."
    ),
    "contract-versioning": (
        "Cuando una solicitud referencia varias versiones de contrato, utiliza la versión aprobada "
        "más alta y devuelve la versión fuente usada como evidencia."
    ),
    "audit-traceability": (
        "Toda decisión de integración debe conservar un identificador de correlación, el sistema "
        "origen y una marca de tiempo para auditoría."
    ),
}

MEMORY_STORE_TABLES = (
    ("<STORE>_ACTOR_PROFILE", "Perfil técnico del actor o usuario al que se asocia una memoria."),
    ("<STORE>_DOCUMENT", "Documento lógico que agrupa contenido y metadatos persistidos."),
    ("<STORE>_MEMORY", "Registro principal de cada memoria, incluida su clase procedural guideline."),
    ("<STORE>_MEMORY_LINK", "Relaciones entre memorias, actores y documentos cuando el SDK las necesita."),
    ("<STORE>_MESSAGE", "Mensajes asociados a una memoria conversacional cuando ese patrón se utiliza."),
    ("<STORE>_RECORD_CHUNKS", "Fragmentos recuperables de los registros de memoria."),
    ("<STORE>_THREAD", "Hilo o contexto conversacional, disponible aunque este laboratorio no lo use como foco."),
    ("<STORE>_THREAD_SUMMARY", "Resumen de un hilo, disponible para los patrones conversacionales del SDK."),
)

SDK_READING_STEPS = (
    ("Abrir, no crear", "El participante abre el memory store existente con `SchemaPolicy.REQUIRE_EXISTING`; no aprovisiona tablas ni modifica la configuración del owner."),
    ("Persistir una regla", "El SDK guarda una guía sintética con tipo `guideline` dentro del alcance individual `t01:p01`."),
    ("Recuperar por palabra clave", "La consulta `idempotency` filtra el mismo alcance y devuelve solo la regla procedural pertinente."),
    ("Comprobar frontera", "La misma búsqueda contra el alcance de control no devuelve resultados visibles al participante."),
    ("Comparar dos prompts", "Solo la corrida final llama dos veces a OCI Generative AI: baseline completo y prompt compacto con la regla recuperada."),
)


def apply_styles() -> None:
    """Apply a compact workshop-oriented visual treatment."""

    st.markdown(
        """
        <style>
        .block-container {max-width: 1200px; padding-top: 2rem; padding-bottom: 3rem;}
        .hero {padding: 1.35rem 1.5rem; border-radius: 16px; background: linear-gradient(110deg, #14213D, #1D4ED8); color: #FFFFFF; margin-bottom: 1.25rem;}
        .hero h1 {font-size: 2.1rem; margin: 0 0 0.35rem 0; color: #FFFFFF;}
        .hero p {font-size: 1rem; margin: 0; color: #DBEAFE;}
        .journey-card {border: 1px solid #D1D5DB; background: #FFFFFF; border-radius: 12px; padding: 0.9rem 1rem; min-height: 122px;}
        .journey-card-active {border: 2px solid #2563EB; background: #EFF6FF;}
        .journey-number {font-size: 0.82rem; font-weight: 800; color: #1D4ED8; letter-spacing: 0.08em; margin: 0 0 0.35rem 0;}
        .journey-card h4 {margin: 0 0 0.35rem 0; color: #111827;}
        .journey-card p {margin: 0; color: #4B5563; font-size: 0.92rem;}
        .memory-card {border: 1px solid #BFDBFE; background: #EFF6FF; border-radius: 12px; padding: 0.9rem 1rem; margin-bottom: 0.7rem;}
        .memory-card h4 {margin: 0 0 0.35rem 0; color: #1E3A8A;}
        .memory-card p {margin: 0; color: #1F2937;}
        .scope-chip {display: inline-block; border-radius: 999px; background: #DBEAFE; color: #1E3A8A; font-weight: 700; padding: 0.25rem 0.65rem; margin-right: 0.4rem;}
        .boundary-card {border-left: 5px solid #16A34A; background: #F0FDF4; border-radius: 8px; padding: 0.85rem 1rem; margin: 0.5rem 0 1rem 0;}
        .warning-card {border-left: 5px solid #D97706; background: #FFFBEB; border-radius: 8px; padding: 0.85rem 1rem; margin: 0.5rem 0 1rem 0;}
        .scope-map {display: grid; grid-template-columns: 1fr 1.15fr 1fr; gap: 0.75rem; align-items: stretch; margin: 0.75rem 0 1rem 0;}
        .scope-node {border-radius: 12px; padding: 0.85rem; background: #F9FAFB; border: 1px solid #D1D5DB; color: #111827;}
        .scope-node-active {background: #EFF6FF; border: 2px solid #2563EB;}
        .scope-node-blocked {background: #FEF2F2; border: 1px solid #FCA5A5;}
        .scope-node strong {display: block; margin-bottom: 0.25rem;}
        .scope-middle {display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.45rem; text-align: center; color: #1F2937;}
        .scope-arrow {font-size: 1.4rem; line-height: 1; color: #2563EB;}
        .scope-blocked {font-weight: 700; color: #B91C1C;}
        @media (max-width: 760px) {.scope-map {grid-template-columns: 1fr;}.scope-middle {order: -1;}}
        .small-note {font-size: 0.85rem; color: #4B5563;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_journey(retrieval_completed: bool, isolation_checked: bool) -> None:
    """Render the workshop journey and its currently completed steps."""

    active_step = 1
    if retrieval_completed:
        active_step = 2
    if isolation_checked:
        active_step = 3

    st.subheader("Recorrido de la demostración")
    columns = st.columns(3)
    for index, (number, title, description) in enumerate(LAB_STEPS, start=1):
        state_class = " journey-card-active" if index == active_step else ""
        state = "En curso" if index == active_step else "Preparado"
        if index < active_step:
            state = "Completado"
        columns[index - 1].markdown(
            (
                f'<div class="journey-card{state_class}">'
                f'<p class="journey-number">{number} · {state}</p>'
                f"<h4>{title}</h4>"
                f"<p>{description}</p>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )


def render_memory_cards(retrieved_identifiers: list[str]) -> None:
    """Render retrieved procedural guidance as readable cards."""

    by_identifier = {guideline.identifier: guideline for guideline in GUIDELINES}
    for identifier in retrieved_identifiers:
        guideline = by_identifier[identifier]
        st.markdown(
            (
                '<div class="memory-card">'
                f"<h4>{guideline.identifier}</h4>"
                f"<p>{GUIDELINE_DISPLAY_CONTENT.get(identifier, guideline.content)}</p>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )


def render_scope_map(team_id: str) -> None:
    """Make the active and blocked context boundary explicit."""

    selected_team = TEAM_LABELS[team_id]
    other_team = TEAM_LABELS["team-02" if team_id == "team-01" else "team-01"]
    st.markdown(
        f"""
        <div class="scope-map" aria-label="Context isolation visualization">
          <div class="scope-node scope-node-active">
            <strong>{selected_team}</strong>
            Alcance activo: recupera su memoria procedural.
          </div>
          <div class="scope-middle">
            <span class="scope-arrow">→</span>
            <strong>Memoria con alcance de equipo</strong>
            <span class="small-note">La consulta lleva el identificador del equipo.</span>
            <span class="scope-arrow">←</span>
          </div>
          <div class="scope-node scope-node-blocked">
            <strong>{other_team}</strong>
            <span class="scope-blocked">0 guías expuestas al equipo activo.</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_offline_token_preview(comparison: dict[str, int]) -> None:
    """Show the local preview without presenting it as OCI token evidence."""

    baseline = comparison["baseline_prompt_tokens"]
    compact = comparison["memory_prompt_tokens"]
    request_with_memory = comparison["estimated_request_tokens_with_memory"]
    removed = comparison["repeated_prompt_reduction_tokens"]
    columns = st.columns(3)
    columns[0].metric("Prompt con reglas repetidas", f"{baseline} tokens")
    columns[1].metric("Prompt compacto", f"{compact} tokens", f"-{removed} tokens")
    columns[2].metric("Prompt + memoria relevante", f"{request_with_memory} tokens")

    chart = pd.DataFrame(
        {
            "Diseño de contexto": [
                "Reglas repetidas",
                "Prompt compacto",
                "Prompt + memoria relevante",
            ],
            "Tokens estimados": [baseline, compact, request_with_memory],
        }
    ).set_index("Diseño de contexto")
    st.bar_chart(chart, color="#2563EB", horizontal=True)
    reduction = comparison["estimated_request_reduction_tokens"]
    reduction_percent = round((reduction / baseline) * 100) if baseline else 0
    st.success(
        f"En esta solicitud se evitan aproximadamente {reduction} tokens repetidos "
        f"({reduction_percent}% del contexto base) al recuperar solo la guía pertinente."
    )
    st.caption(
        "Vista previa local de diseño. No es una medición de tokens de OCI y no puede usarse "
        "como evidencia del workshop."
    )


def render_before_execution() -> None:
    """Explain the real participant path before any credentials are requested."""

    st.subheader("Antes de ejecutar: qué ocurrirá realmente")
    preflight, memory_run, live_run, evidence = st.columns(4)
    preflight.markdown(
        """<div class="journey-card">
        <p class="journey-number">PRECHECK · 0 llamadas OCI</p>
        <h4>1. Validar acceso</h4>
        <p>Confirma Python, identidad OCI, wallet y acceso al memory store. Solicita claves solo en tu terminal.</p>
        </div>""",
        unsafe_allow_html=True,
    )
    memory_run.markdown(
        """<div class="journey-card journey-card-active">
        <p class="journey-number">MEMORIA REAL · 0 llamadas OCI</p>
        <h4>2. Persistir y recuperar</h4>
        <p>Elige una regla sintética, persístela y recupérala desde ADB dentro de tu alcance.</p>
        </div>""",
        unsafe_allow_html=True,
    )
    live_run.markdown(
        """<div class="journey-card journey-card-active">
        <p class="journey-number">EJECUCIÓN · 2 llamadas OCI</p>
        <h4>3. Comparar tokens</h4>
        <p>Compara baseline y memoria con el mismo modelo, usando solo dos inferencias autorizadas.</p>
        </div>""",
        unsafe_allow_html=True,
    )
    evidence.markdown(
        """<div class="journey-card">
        <p class="journey-number">EVIDENCIA · JSON seguro</p>
        <h4>4. Interpretar</h4>
        <p>Visualiza persistencia, aislamiento, tokens, latencia y calidad. No se cargan secretos al dashboard.</p>
        </div>""",
        unsafe_allow_html=True,
    )
    st.code(
        ".\\labs\\lab01_agent_memory\\scripts\\run_participant_live.ps1 "
        "-TeamCode T01 -ParticipantCode P01 -SessionFile <private-session.ps1> -Preflight",
        language="powershell",
    )
    st.caption(
        "El preflight no llama al modelo. La ejecución sin `-Preflight` realiza exactamente dos "
        "inferencias on-demand con datos sintéticos."
    )


def render_real_inference_comparison(inference: dict[str, object]) -> None:
    """Show provider-reported OCI token usage from the two comparable live calls."""

    baseline = inference["baseline"]
    optimized = inference["memory_optimized"]
    st.subheader("3. Inferencia real en OCI Generative AI")
    left, middle, right = st.columns(3)
    left.metric("Prompt base", f"{baseline['prompt_tokens']} tokens")
    middle.metric("Prompt con memoria", f"{optimized['prompt_tokens']} tokens")
    right.metric(
        "Reducción real de entrada",
        f"{inference['input_token_reduction']} tokens",
        f"-{inference['input_token_reduction_percent']}%",
    )
    chart = pd.DataFrame(
        {
            "Variante": ["Prompt base", "Prompt con memoria"],
            "Tokens de entrada OCI": [baseline["prompt_tokens"], optimized["prompt_tokens"]],
            "Tokens de salida OCI": [
                baseline["completion_tokens"],
                optimized["completion_tokens"],
            ],
        }
    ).set_index("Variante")
    st.bar_chart(chart, color=["#C74634", "#2F855A"], horizontal=True)
    detail_left, detail_right = st.columns(2)
    detail_left.caption(
        f"Base: {baseline['total_tokens']} tokens totales · {baseline['latency_ms']} ms · "
        f"calidad {'aprobada' if baseline['quality_passed'] else 'rechazada'}"
    )
    detail_right.caption(
        f"Memoria: {optimized['total_tokens']} tokens totales · {optimized['latency_ms']} ms · "
        f"calidad {'aprobada' if optimized['quality_passed'] else 'rechazada'}"
    )
    st.success(
        "OCI reportó una reducción real de tokens de entrada y ambas respuestas cumplieron los "
        "criterios de decisión del ejercicio."
    )
    st.caption(
        "La reducción de tokens de entrada no representa por sí sola el costo total de la solución: "
        "también deben evaluarse memoria, almacenamiento y recuperación."
    )


def _participant_evidence_paths() -> list[Path]:
    """Return safe participant evidence files without reading secret directories."""

    if not PARTICIPANT_EVIDENCE_DIRECTORY.is_dir():
        return []
    paths = [
        *PARTICIPANT_EVIDENCE_DIRECTORY.glob("*/local-algorithm-evidence.json"),
        *PARTICIPANT_EVIDENCE_DIRECTORY.glob("facilitator/oci-sdk-inference-evidence.json"),
        *PARTICIPANT_EVIDENCE_DIRECTORY.glob("*/*/memory-exercise-evidence.json"),
        *PARTICIPANT_EVIDENCE_DIRECTORY.glob("*/*/memory-exercise-*-evidence.json"),
        *PARTICIPANT_EVIDENCE_DIRECTORY.glob("*/*/oci-sdk-evidence.json"),
        *PARTICIPANT_EVIDENCE_DIRECTORY.glob("*/*/oci-inference-evidence.json"),
    ]
    return sorted(set(paths))


def _context_experiment_evidence_paths() -> list[Path]:
    """Return safe extended-experiment artifacts from the local artifacts tree."""

    if not PARTICIPANT_EVIDENCE_DIRECTORY.is_dir():
        return []
    return sorted(PARTICIPANT_EVIDENCE_DIRECTORY.glob("*/*/context-economy-experiment-evidence.json"))


def _custom_procedure_evidence_paths() -> list[Path]:
    """Return safe participant-authored procedure evidence artifacts."""

    if not PARTICIPANT_EVIDENCE_DIRECTORY.is_dir():
        return []
    return sorted(PARTICIPANT_EVIDENCE_DIRECTORY.glob("*/*/custom-procedure-evidence.json"))


def _evidence_path_label(path: Path) -> str:
    """Show a repository-relative label rather than an absolute machine path."""

    return str(path.relative_to(REPOSITORY_ROOT)).replace("\\", "/")


def render_executed_participant_evidence() -> None:
    """Render actual JSON emitted after a participant executes the visible algorithm."""

    local_paths = _participant_evidence_paths()
    with st.sidebar:
        st.divider()
        st.subheader("Evidencia real de ejecución")
        uploaded = st.file_uploader(
            "Cargar JSON seguro ya generado",
            type="json",
            key="participant_evidence_upload",
            help="El dashboard solo lee y visualiza este JSON. No ejecuta el laboratorio ni carga wallets o credenciales.",
        )
        selected_path: Path | None = None
        if uploaded is None and local_paths:
            selected_path = st.selectbox(
                "Evidencia real detectada en artifacts",
                options=local_paths,
                format_func=_evidence_path_label,
            )

    raw_json: str | None = None
    source_label: str | None = None
    if uploaded is not None:
        raw_json = uploaded.getvalue().decode("utf-8")
        source_label = uploaded.name
    elif selected_path is not None:
        raw_json = selected_path.read_text(encoding="utf-8")
        source_label = _evidence_path_label(selected_path)

    st.subheader("Evidencia de ejecución del equipo")
    if raw_json is None:
        st.info(
            "Aún no hay evidencia. Ejecuta primero el ejercicio real de memoria o la comparación "
            "OCI y carga el JSON seguro que genera."
        )
        return

    try:
        evidence = load_participant_evidence(raw_json)
    except (UnicodeDecodeError, ValueError) as error:
        st.error(f"No se puede mostrar esta evidencia: {error}")
        return

    algorithm = evidence["algorithm"]
    retrieved = evidence["retrieved_procedure_ids"]
    cross_team = evidence["cross_team_visible_procedure_ids"]
    is_sdk_execution = evidence["evidence_type"] in {
        "oci_sdk_execution_validation",
        "oci_sdk_inference_validation",
    }
    has_real_inference = evidence["evidence_type"] == "oci_sdk_inference_validation"
    if has_real_inference:
        st.success(
            "Evidencia OCI aprobada: Agent Memory persistió y recuperó decisiones; OCI Generative "
            "AI midió la reducción real de tokens."
        )
    elif is_sdk_execution:
        if evidence.get("exercise_mode") == "memory_only":
            st.success(
                "Ejercicio de memoria ADB aprobado: persistió, recuperó y aisló una decisión "
                "sin llamar a OCI Generative AI."
            )
        else:
            st.warning(
                "La memoria en ADB es real, pero este archivo no contiene la medición de tokens de OCI. "
                "No es evidencia final del Workshop 1."
            )
    else:
        st.success("Evidencia local aprobada: recuperó memoria propia y bloqueó el acceso cruzado.")
    col_team, col_scope, col_results = st.columns(3)
    col_team.metric("Equipo", evidence["active_team_name"])
    col_scope.metric("Alcance aplicado", algorithm["scope"])
    col_results.metric("Procedimientos recuperados", algorithm["max_results"])
    if is_sdk_execution:
        execution = evidence["sdk_execution"]
        st.subheader("1. Memoria real en Autonomous Database")
        sdk_left, sdk_middle, sdk_right = st.columns(3)
        sdk_left.metric("Política de esquema", execution["schema_policy"])
        sdk_middle.metric(
            "Búsqueda procedural",
            f"{execution['search_strategy']} · {', '.join(algorithm['record_types'])}",
        )
        sdk_right.metric("Persistencia ADB", "Confirmada")
        st.write(
            "**Procedimientos persistidos en ADB:** "
            + ", ".join(evidence["persisted_procedure_ids"])
        )
        st.caption(
            "Alcance individual: "
            f"{execution['individual_scope']} · Alcance compartido: {execution['team_shared_scope']} · "
            f"Alcance de control: {execution['control_scope']}"
        )

    st.subheader("2. Aislamiento del contexto")
    st.write(f"**Consulta ejecutada:** {algorithm['query']}")
    st.write("**Procedimientos recuperados:** " + ", ".join(retrieved))
    st.write(f"**Intento de acceso cruzado:** {evidence['cross_team_challenge']}")
    if cross_team:
        st.error("El resultado no está aprobado: se detectó contenido de otro equipo.")
    elif evidence.get("exercise_mode") == "memory_only":
        st.info(
            "Este ejercicio se detiene deliberadamente antes de inferencia. La telemetría de tokens "
            "se genera únicamente en la corrida final de dos solicitudes OCI."
        )
    else:
        st.markdown(
            '<div class="boundary-card"><strong>Frontera comprobada.</strong> '
            "El intento de acceso cruzado devolvió cero procedimientos.</div>",
            unsafe_allow_html=True,
        )

    if has_real_inference:
        render_real_inference_comparison(evidence["inference"])
        st.subheader("4. Interpretación")
        st.markdown(
            "- **Decisión recuperada:** " + ", ".join(retrieved) + ".  \n"
            "- **Contexto que no se reenvió:** las demás reglas del bundle.  \n"
            "- **Límite de la prueba:** el alcance demuestra una frontera de recuperación; "
            "no sustituye autorización de producción."
        )
    else:
        st.warning(
            "La comparación local de diseño no sustituye la telemetría real de OCI Generative AI."
        )
    st.caption(f"Fuente: {source_label}. El archivo declara explícitamente que no contiene secretos.")


def render_context_experiment() -> None:
    """Render a separately validated real OCI context-economy experiment."""

    st.subheader("Experimento real: economía de contexto")
    st.info(
        "Este ejercicio ampliado es opcional y posterior a la evidencia P01. Persiste un catálogo "
        "sintético, recupera la regla principal dentro del alcance individual y compara cuatro "
        "contextos con el mismo modelo y la misma pregunta. El dashboard solo interpreta el JSON; "
        "nunca ejecuta OCI ni solicita credenciales."
    )
    local_paths = _context_experiment_evidence_paths()
    uploaded = st.file_uploader(
        "Cargar evidencia segura del experimento de contexto",
        type="json",
        key="context_experiment_upload",
        help="Carga únicamente el JSON emitido por -ContextExperiment; no subas sesiones, wallets ni logs.",
    )
    selected_path: Path | None = None
    if uploaded is None and local_paths:
        selected_path = st.selectbox(
            "Experimento detectado en artifacts",
            options=local_paths,
            format_func=_evidence_path_label,
            key="context_experiment_artifact",
        )

    raw_json: str | None = None
    source_label: str | None = None
    if uploaded is not None:
        raw_json = uploaded.getvalue().decode("utf-8")
        source_label = uploaded.name
    elif selected_path is not None:
        raw_json = selected_path.read_text(encoding="utf-8")
        source_label = _evidence_path_label(selected_path)

    if raw_json is None:
        st.warning(
            "Todavía no hay evidencia del experimento ampliado. Primero completa la comparación "
            "P01 de dos llamadas y luego ejecuta el ejercicio opcional desde PowerShell."
        )
        st.code(
            ".\\labs\\lab01_agent_memory\\scripts\\run_participant_live.ps1 "
            "-TeamCode T01 -ParticipantCode P01 -SessionFile <private-session.ps1> "
            "-ContextExperiment",
            language="powershell",
        )
        st.caption(
            "La ejecución anterior hace exactamente cuatro llamadas on-demand con datos sintéticos. "
            "No reemplaza la comparación base de dos llamadas."
        )
        return

    try:
        evidence = load_context_experiment_evidence(raw_json)
    except (UnicodeDecodeError, ValueError) as error:
        st.error(f"No se puede mostrar esta evidencia ampliada: {error}")
        return

    experiment = evidence["experiment"]
    memory = evidence["memory_execution"]
    inference = evidence["inference_experiment"]
    variants = inference["variants"]
    by_id = {variant["variant_id"]: variant for variant in variants}
    baseline = by_id[inference["baseline_variant_id"]]
    lowest = by_id[inference["lowest_input_variant_id"]]

    st.success(
        "Experimento aprobado: catálogo persistido en ADB, recuperación acotada y todas las "
        "variantes completadas con los criterios de calidad requeridos."
    )
    left, middle, right, last = st.columns(4)
    left.metric("Procedimientos en catálogo", len(memory["persisted_procedure_ids"]))
    middle.metric("Regla recuperada", ", ".join(memory["retrieved_procedure_ids"]))
    right.metric("Variantes OCI", len(variants))
    last.metric(
        "Menor contexto vs baseline",
        f"-{inference['lowest_input_reduction_from_baseline']} tokens",
    )
    st.write(f"**Pregunta constante:** {experiment['question']}")
    st.write(f"**Consulta de recuperación:** `{experiment['retrieval_query']}`")
    st.caption(
        f"Baseline: {baseline['label']} ({baseline['prompt_tokens']} tokens de entrada). "
        f"Mejor variante: {lowest['label']} ({lowest['prompt_tokens']} tokens de entrada)."
    )
    rows = pd.DataFrame(
        [
            {
                "Variante": variant["label"],
                "Procedimientos": variant["procedure_count"],
                "Tokens de entrada": variant["prompt_tokens"],
                "Tokens de salida": variant["completion_tokens"],
                "Tokens totales": variant["total_tokens"],
                "Latencia (ms)": variant["latency_ms"],
            }
            for variant in variants
        ]
    )
    st.dataframe(rows, hide_index=True, use_container_width=True)
    st.bar_chart(
        rows.set_index("Variante")[["Tokens de entrada", "Tokens de salida"]],
        color=["#2563EB", "#93C5FD"],
        horizontal=True,
    )
    st.markdown(
        "**Cómo interpretar el resultado**  \n"
        "- El baseline reenvía todo el catálogo; no representa el diseño recomendado.  \n"
        "- La variante recuperada usa solo la decisión encontrada en Agent Memory.  \n"
        "- Las variantes con distractores muestran el costo de adjuntar contexto adicional aunque "
        "sea técnicamente válido.  \n"
        "- Todas usan la misma pregunta, modelo y límite de salida: el cambio medido es el contexto."
    )
    st.caption(
        f"Fuente: {source_label}. El validador exige JSON seguro, política REQUIRE_EXISTING, "
        "búsqueda KEYWORD, persistencia, aislamiento y telemetría OCI consistente."
    )


def render_custom_procedure() -> None:
    """Render the participant-authored procedure and its retrieval study."""

    st.subheader("Diseño y evaluación de una regla propia")
    st.info(
        "Este ejercicio no invoca OCI Generative AI. Persiste una regla sintética en ADB y "
        "compara recuperación dirigida, amplia y de control para discutir precisión antes de optimizar prompts."
    )
    local_paths = _custom_procedure_evidence_paths()
    uploaded = st.file_uploader(
        "Cargar evidencia segura de procedimiento propio",
        type="json",
        key="custom_procedure_upload",
        help="Carga únicamente custom-procedure-evidence.json; no cargues wallets, sesiones ni logs.",
    )
    selected_path: Path | None = None
    if uploaded is None and local_paths:
        selected_path = st.selectbox(
            "Procedimiento detectado en artifacts",
            options=local_paths,
            format_func=_evidence_path_label,
            key="custom_procedure_artifact",
        )
    raw_json: str | None = None
    source_label: str | None = None
    if uploaded is not None:
        raw_json = uploaded.getvalue().decode("utf-8")
        source_label = uploaded.name
    elif selected_path is not None:
        raw_json = selected_path.read_text(encoding="utf-8")
        source_label = _evidence_path_label(selected_path)
    if raw_json is None:
        st.warning("Aún no hay evidencia de una regla propia. Copia el template, edítalo y ejecuta el ejercicio sin inferencia.")
        st.code(
            ".\\labs\\lab01_agent_memory\\scripts\\run_participant_live.ps1 "
            "-TeamCode T01 -ParticipantCode P01 -SessionFile <private-session.ps1> "
            "-CustomProcedure <synthetic-procedure.json>",
            language="powershell",
        )
        return
    try:
        evidence = load_custom_procedure_evidence(raw_json)
    except (UnicodeDecodeError, ValueError) as error:
        st.error(f"No se puede mostrar esta evidencia: {error}")
        return
    procedure = evidence["procedure"]
    execution = evidence["sdk_execution"]
    st.success("Regla propia aprobada: persistencia, recuperación dirigida y control negativo confirmados.")
    first, second, third = st.columns(3)
    first.metric("Procedimiento", procedure["procedure_id"])
    second.metric("Dominio", procedure["domain"])
    third.metric("Registro", "Nuevo" if execution["created"] else "Ya existente")
    st.write("**Términos de activación:** " + ", ".join(procedure["trigger_terms"]))
    st.write("**Evidencia requerida:** " + ", ".join(procedure["required_evidence"]))
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Caso": case["label"],
                    "Consulta": case["query"],
                    "Resultados": case["result_count"],
                    "Regla propia recuperada": "Sí" if case["custom_procedure_retrieved"] else "No",
                }
                for case in evidence["retrieval_study"]
            ]
        ),
        hide_index=True,
        use_container_width=True,
    )
    st.markdown(
        "**Discusión:** la consulta dirigida debe recuperar la regla propia; la amplia puede traer "
        "más contexto del necesario; el control negativo debe evitar recuperar esa regla. Esto es "
        "evaluación de retrieval, no una garantía de autorización de producción."
    )
    st.caption(f"Fuente: {source_label}. La evidencia contiene identificadores y métricas seguras, no secretos.")


def render_live_evidence() -> None:
    """Display optional facilitator evidence without mixing it with participant evidence."""

    st.caption("Esta prueba es opcional y complementaria. No reemplaza la evidencia individual del participante que aparece arriba.")
    uploaded = st.file_uploader(
        "Cargar JSON opcional de aislamiento",
        type="json",
        key="facilitator_isolation_upload",
        help="Solo archivos de evidencia sin credenciales.",
    )
    live_evidence_available = LIVE_EVIDENCE_PATH.is_file()
    use_example = st.toggle(
        "Mostrar ejemplo de formato (no evidencia del trial)",
        value=uploaded is None and not live_evidence_available,
        key="facilitator_isolation_example",
    )

    raw_json: str | None = None
    evidence_label: str | None = None
    if uploaded is not None:
        raw_json = uploaded.getvalue().decode("utf-8")
        evidence_label = uploaded.name
    elif live_evidence_available and not use_example:
        raw_json = LIVE_EVIDENCE_PATH.read_text(encoding="utf-8")
        evidence_label = "evidencia OCI del trial (artefacto local)"
    elif use_example:
        raw_json = EXAMPLE_EVIDENCE_PATH.read_text(encoding="utf-8")
        evidence_label = "example evidence"

    st.subheader("Prueba adicional del facilitador en OCI AI Agent Memory")
    if raw_json is None:
        st.info(
            "Aún no se cargó evidencia en vivo. La experiencia de participante continúa en modo local; "
            "el facilitador puede cargar el JSON producido por validate_oci_isolation.py."
        )
        return

    try:
        evidence = load_live_evidence(raw_json)
    except (UnicodeDecodeError, ValueError) as error:
        st.error(f"No se puede mostrar esta evidencia: {error}")
        return

    teams = evidence["teams"]
    team_a = teams["team-a"]
    team_b = teams["team-b"]
    all_passed = team_a["isolation_passed"] and team_b["isolation_passed"]
    if evidence_label == "example evidence":
        st.info(
            "Este es un ejemplo de formato. El facilitador debe cargar el JSON generado por la "
            "validación OCI para presentar evidencia real del trial."
        )
    elif all_passed:
        st.success("La evidencia OCI confirma aislamiento bidireccional entre Team A y Team B.")
    else:
        st.error("La evidencia OCI indica que una prueba de aislamiento falló. No continúes el lab en vivo.")
    left, right = st.columns(2)
    left.metric("Team A", f"{team_a['result_count']} resultado", "Aislamiento aprobado" if team_a["isolation_passed"] else "Revisar")
    right.metric("Team B", f"{team_b['result_count']} resultado", "Aislamiento aprobado" if team_b["isolation_passed"] else "Revisar")
    st.caption(f"Fuente: {evidence_label}. Generada: {evidence['generated_at_utc']}. Sin secretos.")


def render_local_simulator() -> None:
    """Render a deliberately local teaching simulator, separate from OCI evidence."""

    st.subheader("Simulador docente local")
    st.warning("Esta pestaña no consulta ADB, OCI Generative AI ni el SDK. Sus botones solo cambian la visualización de datos sintéticos en el navegador; no alteran la evidencia real.")
    left, right = st.columns(2)
    with left:
        team_id = st.selectbox("Equipo simulado", options=tuple(TEAM_LABELS), format_func=TEAM_LABELS.get, key="simulation_team")
    with right:
        question = st.selectbox("Pregunta de ingeniería simulada", options=QUESTION_OPTIONS, key="simulation_question")
    controls, explanation = st.columns((1, 2))
    with controls:
        run_retrieval = st.button("Mostrar recuperación simulada", type="primary", use_container_width=True, key="simulation_show_memory_button")
        if st.button("Reiniciar demostración", use_container_width=True, key="simulation_reset_button"):
            st.session_state["lab01_show_memory"] = False
            st.session_state["lab01_isolation_checked"] = False
    with explanation:
        st.info("Cambiar la pregunta sirve para discutir el diseño de recuperación. Las cifras de «Mi evidencia real» no cambian porque provienen de un JSON generado por una corrida controlada.")

    report = build_report(team_id, question)
    if run_retrieval:
        st.session_state["lab01_show_memory"] = True
    retrieval_completed = st.session_state.get("lab01_show_memory", False)
    isolation_checked = st.session_state.get("lab01_isolation_checked", False)
    st.markdown(f'<span class="scope-chip">Alcance simulado: {TEAM_LABELS[team_id]}</span><span class="scope-chip">Datos sintéticos locales</span>', unsafe_allow_html=True)
    st.write(f"**Pregunta simulada:** {question}")
    render_journey(retrieval_completed, isolation_checked)
    st.divider()
    st.subheader("Memoria procedural simulada")
    if retrieval_completed:
        render_memory_cards(report["retrieved_guidelines"])
        st.markdown('<div class="boundary-card"><strong>Frontera de contexto simulada.</strong> La búsqueda cruzada devuelve cero guías de otro equipo en el conjunto local.</div>', unsafe_allow_html=True)
    else:
        st.info("Selecciona «Mostrar recuperación simulada» para revelar las guías locales.")
    with st.expander("Probar el intento de acceso entre equipos (simulado)"):
        st.write("El segundo alcance representa deliberadamente otro equipo. Esta verificación es una ilustración local; la prueba real aparece en el JSON de evidencia ejecutada.")
        if st.button("Comprobar aislamiento simulado", use_container_width=True, key="simulation_isolation_button"):
            st.session_state["lab01_isolation_checked"] = True
            isolation_checked = True
        if isolation_checked:
            render_scope_map(team_id)
            if report["isolation_passed"]:
                st.success("Acceso cruzado simulado bloqueado: no se recuperó ninguna guía de otro equipo.")
            else:
                st.error("El aislamiento local falló; no continúes hasta resolverlo.")
    st.divider()
    st.subheader("Vista previa local de contexto")
    render_offline_token_preview(report["prompt_comparison"])
    st.download_button("Descargar simulación local", data=json.dumps(report, indent=2), file_name=f"lab01-{team_id}-local-simulation.json", mime="application/json", help="Este archivo es didáctico; no es evidencia OCI del workshop.", key="simulation_download")


def render_sdk_reading() -> None:
    """Explain the code path exercised by the real participant runner."""

    st.subheader("Lectura guiada del código y del SDK")
    st.info("Esta pestaña explica la misma ruta que ejecutó el runner. No hace llamadas ni modifica la base de datos.")
    for index, (title, description) in enumerate(SDK_READING_STEPS, start=1):
        with st.expander(f"{index}. {title}", expanded=index == 1):
            st.write(description)
    st.subheader("Fragmentos esenciales")
    left, right = st.columns(2)
    with left:
        st.caption("El participante requiere que el store ya exista; no crea su propio esquema.")
        st.code("OracleAgentMemory(\n    memory_store_id=memory_store_id,\n    schema_owner=memory_schema_owner,\n    schema_policy=SchemaPolicy.REQUIRE_EXISTING,\n)", language="python")
        st.caption("La regla se persiste como guía procedural dentro del alcance individual.")
        st.code("memory.add_memory(\n    content=guideline_text,\n    memory_type=\"guideline\",\n    user_id=scopes.individual,\n)", language="python")
    with right:
        st.caption("La recuperación reutiliza exactamente el mismo alcance del participante.")
        st.code("memory.search(\n    query=\"idempotency\",\n    user_id=scopes.individual,\n    exact_user_match=True,\n    record_types=[\"guideline\"],\n)", language="python")
        st.caption("La comparación final conserva modelo y parámetros; cambia solo el contexto de entrada.")
        st.code("baseline = client.chat(full_context_prompt, settings)\nmemory = client.chat(compact_prompt_with_retrieved_rule, settings)", language="python")
    st.subheader("Preguntas para discutir durante el workshop")
    st.markdown("- ¿Qué texto se evita reenviar cuando solo se recupera `payment-idempotency`?  \n- ¿Qué frontera comprueba `exact_user_match=True` y qué controles adicionales requeriría producción?  \n- ¿Por qué la comparación de tokens mantiene el mismo modelo y los mismos parámetros?  \n- ¿Qué diferencia hay entre probar una regla recuperada y usar memoria como historial completo de conversación?")
    st.caption("La corrida OCI real usa una pregunta fija para que los dos prompts sean comparables. El selector de preguntas del simulador no vuelve a ejecutar inferencias ni cambia esa telemetría.")


def render_table_model() -> None:
    """Explain the memory-store tables installed by the owner bootstrap."""

    st.subheader("Modelo de tablas del memory store")
    st.info("Las ocho tablas fueron creadas una vez por el bootstrap del owner. Los participantes reciben privilegios de runtime sobre el store existente; no administran sus tablas.")
    st.graphviz_chart('''digraph memory_store { rankdir=LR; graph [bgcolor="transparent"]; node [shape=box, style="rounded,filled", fillcolor="#EFF6FF", color="#2563EB"]; actor [label="ACTOR_PROFILE"]; memory [label="MEMORY\\nregla procedural"]; chunks [label="RECORD_CHUNKS\\ncontenido recuperable"]; document [label="DOCUMENT"]; links [label="MEMORY_LINK"]; thread [label="THREAD"]; summary [label="THREAD_SUMMARY"]; message [label="MESSAGE"]; actor -> memory; memory -> chunks; document -> memory; memory -> links; thread -> summary; thread -> message; }''')
    st.caption("Diagrama conceptual: el prefijo físico depende del memory store. El laboratorio usa MEMORY y la recuperación procedural; los objetos de hilo están disponibles para otros patrones del SDK.")
    st.dataframe(pd.DataFrame(MEMORY_STORE_TABLES, columns=["Tabla conceptual", "Propósito"]), hide_index=True, use_container_width=True)
    st.markdown("Referencias: [Oracle AI Agent Memory](https://docs.oracle.com/en/database/oracle/oracle-database/26/aioci/ai-agent-memory.html) · [Oracle Database 26ai](https://docs.oracle.com/en/database/oracle/oracle-database/26/).")


def render_real_evidence_tab() -> None:
    """Keep real execution evidence as the first and unambiguous dashboard view."""

    render_before_execution()
    st.divider()
    render_executed_participant_evidence()
    st.divider()
    with st.expander("Prueba adicional del facilitador (opcional)"):
        render_live_evidence()
    st.divider()
    st.subheader("Cierre arquitectónico")
    st.markdown("1. Una guía procedural no es una conversación completa.  \n2. El alcance del equipo limita qué contexto puede recuperarse.  \n3. Menos texto repetido puede reducir el contexto de entrada, sin ocultar el costo del ciclo de memoria.")


def main() -> None:
    """Run the local, browser-based Lab 1 participant experience."""

    st.set_page_config(page_title="Khipu AI Memory Studio", page_icon="🧠", layout="wide")
    apply_styles()
    st.markdown(
        """
        <section class="hero">
          <h1>Khipu AI Memory Studio</h1>
          <p>Workshop 1: economía de tokens, memoria de decisiones y aislamiento de contexto.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

    real_tab, simulator_tab, sdk_tab, tables_tab, experiment_tab, design_tab = st.tabs(
        (
            "1. Mi evidencia real",
            "2. Simulador docente",
            "3. Código y SDK",
            "4. Modelo de tablas",
            "5. Experimentos reales",
            "6. Diseño y evaluación",
        )
    )
    with real_tab:
        render_real_evidence_tab()
    with simulator_tab:
        render_local_simulator()
    with sdk_tab:
        render_sdk_reading()
    with tables_tab:
        render_table_model()
    with experiment_tab:
        render_context_experiment()
    with design_tab:
        render_custom_procedure()


if __name__ == "__main__":
    main()
