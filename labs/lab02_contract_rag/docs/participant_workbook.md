# Cuaderno de trabajo del participante — Workshop 2

Este cuaderno transforma la ejecución técnica en evidencia de aprendizaje. Antes de empezar, cópialo a tu carpeta personal de artefactos; no edites el archivo del repositorio ni subas tus artefactos privados a Git.

```text
artifacts/lab02/<your-participant-id>/participant_workbook.md
```

Trabaja solo con los contratos y preguntas sintéticas incluidos en el repositorio. No registres contraseñas, rutas privadas, wallet, tokens ni datos de clientes.

## 1. Riesgo de versiones

Escribe un ejemplo de una respuesta que parezca razonable, pero mezcle v1 y v2. Luego explica por qué el filtro por versión debe aplicarse antes del ranking.

- Mezcla incorrecta posible:
- Riesgo para una integración:
- Cómo la evita el filtro estricto:

## 2. Comparación de contratos

Completa la tabla leyendo `labs/lab02_contract_rag/data/contract_v1.md` y `labs/lab02_contract_rag/data/contract_v2.md`.

| Elemento | v1 | v2 | Cambio comprobado |
|---|---|---|---|
| Método y endpoint |  |  |  |
| Campo del cuerpo |  |  |  |
| Estados permitidos |  |  |  |
| Header de idempotencia |  |  |  |
| Error por reutilización distinta |  |  |  |
| Timestamp de respuesta exitosa |  |  |  |
| Error por estado inválido |  |  |  |

## 3. Fragmentos y procedencia local

Ejecuta M2 con `run_local_practice.py inspect`. Este reporte no llama a OCI. Registra un fragmento de cada versión. No necesitas copiar el contenido completo: identifica cómo volverías a encontrarlo.

| Versión | Sección | Líneas | `chunk_id` | `content_hash` | Por qué este fragmento es trazable |
|---|---|---|---|---|---|
| v1 |  |  |  |  |  |
| v2 |  |  |  |  |  |

¿Qué valida el `content_hash` y qué no puede validar por sí solo?

## 4. Recuperación léxica local

Ejecuta M3 con T03 y M4 con T08. Los resultados deben declarar `OCI_EXECUTED False`: esta práctica demuestra la separación entre filtro y ranking léxico, no una validación RAG cloud.

| Caso | Versiones recuperadas | Candidato de mayor ranking | Evidencia seleccionada | Por qué el ranking no basta para publicar una afirmación |
|---|---|---|---|---|
| T03 |  |  |  |  |
| T08 |  |  |  |  |

Para T08, escribe la diferencia entre `X-Idempotency-Key` y `Idempotency-Key` y asóciala a la versión correcta.

## 5. Preparación del corpus en OCI

Ejecuta M5 en el dashboard mediante **Preparar mi corpus sintético**. Esta actividad usa OCI Generative AI para crear embeddings de documentos e inserta o reutiliza los fragmentos compatibles en tu schema individual de ADB. No formula una pregunta contractual ni solicita una respuesta de chat.

| Elemento | Registro de la ejecución |
|---|---|
| Estado observado |  |
| Cantidad de fragmentos del corpus |  |
| `corpus_id` activo |  |
| Operaciones OCI/ADB exitosas |  |
| Llamadas de embedding de consulta |  |
| Llamadas de chat |  |
| Resultado de la calibración |  |
| Embeddings de consulta usados para calibrar |  |
| Diferencia respecto de M2 |  |

¿Por qué es correcto que la ingesta no publique candidatos, citas ni una respuesta del modelo? ¿Por qué la calibración no llama al modelo de chat?

## 6. M6 — primera respuesta OCI

Ejecuta T01 o T03 en el dashboard. Registra la respuesta de referencia antes de OCI, la respuesta observada, la traza de servicios y la evidencia publicada. No transcribas contraseñas, rutas privadas ni tokens.

| Caso | Estado esperado | Estado observado | Afirmación publicada | Evidencia seleccionada | Métrica y valor | Cita verificable |
|---|---|---|---|---|---|---|
| T01 o T03 | `answered` |  |  |  |  |  |

¿Qué operaciones de servicio ocurrieron? ¿Hubo exactamente una llamada de embedding de consulta y una llamada de chat?

## 7. M7 — auditar evidencia versus candidatos

Usa la misma ejecución de M6. Sigue el orden del dashboard: respuesta de referencia, respuesta obtenida, comprobaciones automáticas, traza, evidencia seleccionada y candidatos recuperados.

| Comprobación | Valor observado | Interpretación |
|---|---|---|
| `passed` |  |  |
| `version_scope_pass` |  |  |
| `citation_checks_pass` |  |  |
| `support_recall` |  |  |
| `accepted_evidence_precision` |  |  |

¿Qué candidato fue seleccionado como evidencia? ¿Qué candidatos no se publicaron? ¿Por qué una `cosine_distance` menor no convierte automáticamente un candidato en respaldo semántico?

## 8. M8 — migración OCI

Ejecuta T06. La respuesta debe respaldar por separado el endpoint v2, el cambio de `payment_status` a `status` y los tres mapeos de estados.

| Estado esperado | Estado observado | Cambio de endpoint | Cambio de campo | Mapeos de estados | Evidencia y cita para cada aspecto |
|---|---|---|---|---|---|
| `answered` |  |  |  |  |  |

¿La traza mostró `adb_section_coverage`? Si ocurrió, explica qué aspecto necesario completó y por qué sigue limitado a la misma versión, corpus y espacio de embeddings.

## 9. M9 — comparación OCI entre versiones

Ejecuta T08 y contrástalo con M4. La respuesta debe mantener v1 y v2 separadas, tanto en las afirmaciones como en las citas.

| Estado esperado | Estado observado | Header y cita de v1 | Header y cita de v2 | Diferencia comprobada |
|---|---|---|---|---|
| `answered` |  |  |  |  |

¿Qué diferencia observaste entre la recuperación léxica local de M4 y la búsqueda vectorial OCI de M9? ¿Qué propiedad debe mantenerse igual en ambas rutas?

## 10. M10 — límites correctos

| Caso | Resultado correcto | ¿Hubo embedding? | ¿Hubo chat? | Explicación |
|---|---|---:|---:|---|
| T05: pregunta sin versión | `needs_clarification` |  |  |  |
| T10: SLA de disponibilidad | `insufficient_evidence` |  |  |  |
| T12: conteo de transacciones | `structured_data_required` |  |  |  |

Explica por qué una abstención correcta es mejor que una respuesta plausible sin respaldo:

## 11. M11 — RAG o SQL controlado

| Necesidad | RAG, SQL o combinado | Justificación | Control necesario |
|---|---|---|---|
| Explicar estados permitidos en v2 |  |  |  |
| Identificar cambios entre v1 y v2 |  |  |  |
| Contar transacciones `SETTLED` ayer |  |  |  |
| Explicar un estado y contar transacciones con ese estado |  |  |  |

## 12. Entrega y reflexión

Antes de cerrar, confirma:

- [ ] Registré una respuesta positiva con cita y extracto.
- [ ] Ejecuté inspección del corpus y recuperación léxica local sin OCI.
- [ ] Separé evidencia v1 y v2 en una comparación.
- [ ] Registré una aclaración o abstención correcta.
- [ ] Justifiqué cuándo usar RAG y cuándo SQL controlado.
- [ ] Revisé que mi historial local contiene solo mis ejecuciones.
- [ ] No registré ni compartí secretos o rutas privadas.

Mi hallazgo principal sobre evidencia verificable:

Mi limitación principal del sistema:
