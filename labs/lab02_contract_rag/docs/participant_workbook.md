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

## 6. Consultas OCI con respuesta respaldada

Ejecuta T01 o T03, luego T06 y T08. Para cada caso, usa el dashboard para seguir la respuesta hasta la evidencia seleccionada.

| Caso | Estado esperado | Estado observado | Evidencia seleccionada | Métrica y valor | Por qué el extracto respalda la afirmación | Cita verificable |
|---|---|---|---|---|---|---|
| T01 o T03 | `answered` |  |  |  |  |  |
| T06 | `answered` |  |  |  |  |  |
| T08 | `answered` |  |  |  |  |  |

Para T08, deja explícito qué cita corresponde a v1 y cuál a v2. Una `cosine_distance` menor significa mayor proximidad, no que el candidato sea automáticamente el mejor respaldo semántico.

## 7. Límites correctos

| Caso | Resultado correcto | ¿Hubo embedding? | ¿Hubo chat? | Explicación |
|---|---|---:|---:|---|
| T05: pregunta sin versión | `needs_clarification` |  |  |  |
| T10: SLA de disponibilidad | `insufficient_evidence` |  |  |  |
| T12: conteo de transacciones | `structured_data_required` |  |  |  |

Explica por qué una abstención correcta es mejor que una respuesta plausible sin respaldo:

## 8. RAG o SQL controlado

| Necesidad | RAG, SQL o combinado | Justificación | Control necesario |
|---|---|---|---|
| Explicar estados permitidos en v2 |  |  |  |
| Identificar cambios entre v1 y v2 |  |  |  |
| Contar transacciones `SETTLED` ayer |  |  |  |
| Explicar un estado y contar transacciones con ese estado |  |  |  |

## 9. Entrega y reflexión

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
