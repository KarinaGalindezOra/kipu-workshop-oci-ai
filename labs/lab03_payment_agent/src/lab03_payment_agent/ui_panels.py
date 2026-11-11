"""Spanish learning views over actual reports and observed evidence."""

import streamlit as st

from .workbench import execution_metrics, learning_checks, payment_facts

STATUS = {
    "answered": "Respondido",
    "requires_clarification": "Requiere aclaración",
    "insufficient_evidence": "Evidencia insuficiente",
    "conflict": "Conflicto",
    "error": "Error",
}
MESSAGES = {
    "Synthetic payment not found. No case was proposed.": "No se encontró el pago. No se propuso registrar un caso.",
    "Requests and payment events are required.": "Faltan solicitudes o eventos para respaldar la recomendación.",
    "Provide a question, a synthetic payment identifier and v1 or v2.": "Indica una pregunta, un pago sintético y la versión v1 o v2.",
    "The synthetic payment corpus does not support this topic.": "El corpus no contiene evidencia sobre este tema.",
    "No contractual evidence passed retrieval validation.": "Ninguna cláusula superó los filtros y el umbral de recuperación. Revisa Evidencia RAG.",
    "An approved procedure and contractual evidence are required.": "Falta memoria aprobada o evidencia contractual.",
    "Review the memory against the approved v2 procedure.": "La memoria requiere revisión frente al contrato vigente.",
    "The approved memory applies to v2, not this contract.": "La memoria es de v2 y entra en conflicto con la versión seleccionada.",
    "Execution failed. Check readiness and retry explicitly; no automatic write occurred.": "La ejecución falló. Conserva el informe y revisa el diagnóstico con el facilitador antes de otro intento.",
}


def result_origin(result, verified):
    if not verified:
        st.warning(
            "Informe local guardado: en esta vista no se ha revalidado contra ADB. No habilita confirmaciones."
        )
    elif result.execution_mode == "stored_oci_revalidation":
        st.info(
            "Respuesta real retenida en OCI y revalidada. Esta recuperación no hizo nuevas inferencias."
        )
    elif result.execution_mode == "offline_test":
        st.info("Prueba local con dobles: no acredita ejecución OCI.")
    else:
        st.caption("Resultado de la ejecución real conectada a ADB.")


def render_metrics(result, verified):
    metrics = execution_metrics(result)
    st.subheader("Métricas de la investigación")
    result_origin(result, verified)
    columns = st.columns(4)
    columns[0].metric(
        "Duración original",
        f"{metrics['original_elapsed_seconds']} s"
        if metrics["original_elapsed_seconds"] is not None
        else "No disponible",
    )
    columns[1].metric("Herramientas observadas", metrics["tool_observations"])
    columns[2].metric("Cláusulas recuperadas", metrics["contract_sources"])
    columns[3].metric("Memorias recuperadas", metrics["recovered_memories"])
    columns = st.columns(4)
    columns[0].metric(
        "Embeddings de la investigación",
        metrics["original_embedding_calls"]
        if metrics["original_embedding_calls"] is not None
        else "No disponible",
    )
    columns[1].metric(
        "Tokens reportados", metrics["tokens"] if metrics["tokens"] is not None else "No disponible"
    )
    columns[2].metric(
        "Llamadas internas al modelo",
        metrics["provider_calls"] if metrics["provider_calls"] is not None else "No disponible",
    )
    columns[3].metric(
        "Memorias citadas por el agente",
        metrics["model_referenced_memories"]
        if metrics["model_referenced_memories"] is not None
        else "No reportado",
    )
    if metrics["recovered"]:
        st.caption(
            f"Nuevas llamadas al modelo durante la recuperación: {metrics['new_calls_during_recovery']}. La duración corresponde a la ejecución original."
        )
    if metrics["stages_ms"]:
        labels = {
            "memory": "Memoria",
            "retrieval": "Recuperación RAG",
            "agent": "Agente y herramientas",
            "validation": "Validación",
        }
        st.bar_chart(
            {
                "Etapa": [labels.get(key, key) for key in metrics["stages_ms"]],
                "Milisegundos": list(metrics["stages_ms"].values()),
            },
            x="Etapa",
            y="Milisegundos",
        )
    st.caption(
        "No se estiman tokens ni costo a partir de la duración. Un dato no expuesto permanece como no disponible."
    )
    st.dataframe(learning_checks(result), hide_index=True, width="stretch")
    with st.expander("Telemetría técnica original"):
        st.json(result.telemetry)


def render_answer(result, verified):
    st.subheader("Respuesta y recomendación")
    st.write("Estado:", STATUS.get(result.status, result.status))
    result_origin(result, verified)
    if result.status == "answered":
        facts = payment_facts(result)
        if result.answer.startswith("ESCALATE"):
            st.success("Recomendación: escalar el conflicto para investigación humana.")
        else:
            st.success(
                "No se encontró evidencia de un conflicto de payload en las solicitudes consultadas."
            )
        st.write(
            f"Se observaron **{facts['request_count']} solicitudes**, **{facts['distinct_keys']} claves de idempotencia** y **{facts['distinct_payloads']} hashes distintos**."
        )
        st.caption(
            "Este resumen se deriva de las herramientas. La recomendación y las citas del modelo se conservan abajo sin traducir ni modificar."
        )
    else:
        st.warning(
            MESSAGES.get(result.answer, "Revisa el estado y la evidencia antes de continuar.")
        )
    with st.expander("Respuesta original y citas literales", expanded=result.status == "answered"):
        st.code(result.answer, language=None)
    st.caption("Identificador de ejecución: " + result.run_id)


def render_rag(result):
    st.subheader("Del lenguaje natural a la cláusula contractual")
    st.markdown(
        "**Pregunta → embedding → filtros de corpus/API/versión → distancia coseno → cláusula → cita.**"
    )
    metrics = result.telemetry.get("original_execution", result.telemetry)
    if metrics.get("rag_distance_threshold") is not None:
        st.write("Umbral aplicado:", metrics["rag_distance_threshold"])
    candidates = metrics.get("retrieval_candidates", [])
    if candidates:
        st.dataframe(
            [
                {
                    "Fragmento": c["chunk_id"],
                    "Versión": c["version"],
                    "Distancia coseno": c["distance"],
                    "Aceptado": c["accepted"],
                }
                for c in candidates
            ],
            hide_index=True,
            width="stretch",
        )
    elif metrics.get("rag_best_distance") is not None:
        st.metric("Mejor distancia registrada", round(metrics["rag_best_distance"], 4))
        st.caption("Este informe anterior no contiene la lista completa de candidatos.")
    if not result.citations:
        st.info(
            "No hay cláusulas aceptadas en esta ejecución. El agente debe abstenerse si falta evidencia suficiente."
        )
    for source in result.citations:
        with st.container(border=True):
            st.markdown(
                f"**{source['evidence_id']} · {source['source_title']} · {source['contract_version']}**"
            )
            st.write(source["excerpt"])
            st.caption(
                f"Sección: {source['section']} · Fragmento: {source['chunk_id']} · Distancia: {source.get('rank_value', 'No disponible')}"
            )
            st.caption(
                f"Corpus: {source['corpus_id']} · API: {source['api_name']} · Origen: {source['source_uri']}"
            )


def render_tools(result):
    st.subheader("Qué consultó el agente")
    labels = {
        "get_payment": "Datos del pago",
        "get_payment_events": "Eventos del pago",
        "find_related_requests": "Solicitudes relacionadas",
    }
    if not result.tools:
        st.info("No se observaron herramientas en esta ejecución.")
    for index, tool in enumerate(result.tools, 1):
        with st.expander(
            f"{index}. {labels.get(tool['name'], tool['name'])} · {tool['name']}", expanded=True
        ):
            value = tool["result"]
            if "requests" in value:
                st.dataframe(value["requests"], hide_index=True, width="stretch")
            elif "events" in value:
                st.dataframe(value["events"], hide_index=True, width="stretch")
            else:
                st.write(value)
            st.caption(f"Pago: {tool['payment_id']} · Ejecución: {tool['run_id']}")
    st.caption(
        "Se muestran entradas y resultados verificables, no razonamiento interno del modelo."
    )
