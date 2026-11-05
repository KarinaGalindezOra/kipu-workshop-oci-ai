# Workshop 2: evidencia RAG contractual

La guía canónica del participante está en [Paso a paso del participante](../../labs/lab02_contract_rag/docs/participant_step_by_step.md). Comienza allí; incluye descarga mediante Git o ZIP, instalación, validación de tu asignación privada, dashboard y actividades del workshop.

El ejercicio usa contratos sintéticos de desembolsos en dos versiones. El dashboard ejecuta embeddings, búsqueda vectorial en ADB y chat de OCI reales. Una respuesta se considera utilizable solo si sus afirmaciones tienen evidencia resoluble y pertinente.

Durante la actividad debes revisar la respuesta publicada, sus citas, el extracto que la sustenta y los candidatos recuperados. Una distancia coseno menor indica cercanía vectorial; no prueba por sí sola que el texto responda la pregunta.

Si la pregunta no especifica versión, el resultado correcto es solicitar aclaración. Si el contrato no documenta el dato pedido, el resultado correcto es `insufficient_evidence`. Los conteos y hechos operacionales requieren datos estructurados, no el contrato.
