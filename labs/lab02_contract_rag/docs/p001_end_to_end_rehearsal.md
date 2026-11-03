# Ensayo end-to-end de p001

Este es el ensayo reproducible de facilitación para un participante real de Workshop 2. Usa el mismo dashboard local, schema individual, servicio OCI de embeddings, búsqueda vectorial en ADB y OCI chat que se usarán durante el workshop. No es una prueba de carga ni acredita capacidad para 15 participantes concurrentes.

Usa únicamente el corpus y las preguntas sintéticas aprobadas, además de la asignación privada de p001. Mantén wallet, archivo de sesión, contraseñas, tokens y reportes de evidencia fuera del repositorio.

## Criterio de término

El ensayo termina solo cuando los siguientes resultados fueron revisados en el dashboard y registrados en la bitácora privada de facilitación:

- T01 y T03 quedan en estado `answered`, tienen la ruta esperada para la versión solicitada y muestran evidencia seleccionada válida.
- T05 queda en estado `needs_clarification`, con origen `application_control`; no debe llamar a OCI.
- T10 queda en estado `insufficient_evidence`; no debe inventar un SLA ni publicar una respuesta de chat.
- Toda afirmación contractual publicada tiene cita resoluble, extracto, versión, sección y rango de líneas.
- La traza de servicios y el reporte local pertenecen a p001, no usan modo simulado y no contienen credenciales.

## 1. Asignación privada y preflight local

Completa este paso antes de toda inferencia pagada. Valida schema, wallet y asignación sin llamar a OCI Generative AI.

En Windows, carga la sesión privada de PowerShell en una terminal dedicada y ejecuta:

```powershell
. '<private-p001-session.ps1>'
python labs/lab02_contract_rag/scripts/validate_environment.py --check-db
```

En macOS o Linux, usa el archivo privado dotenv:

```bash
python labs/lab02_contract_rag/scripts/validate_environment.py \
  --session-file /private/path/lab02-p001.env \
  --check-db
```

Resultado esperado: JSON seguro con `status` igual a `passed` y `database_session` igual a `participant_schema`.

Si el resultado no es exitoso, detente. No cambies el schema asignado, no crees credenciales de reemplazo ni repitas una contraseña fallida a ciegas. Sigue `troubleshooting.md`.

## 2. Inicia el dashboard local

El listener predeterminado es local en el puerto 8502. Usa otro puerto local disponible solo cuando 8502 ya esté ocupado.

Windows, con la sesión privada cargada:

```powershell
python labs/lab02_contract_rag/scripts/run_dashboard.py --port 8502
```

macOS o Linux, con archivo dotenv privado:

```bash
python labs/lab02_contract_rag/scripts/run_dashboard.py \
  --session-file /private/path/lab02-p001.env \
  --port 8502
```

Abre `http://127.0.0.1:8502`. No uses un proxy público, un perfil de navegador compartido ni la sesión de otro participante.

## 3. Confirma el corpus

Si p001 aún no cargó el corpus aprobado de nueve fragmentos, selecciona **Preparar mi corpus sintético** en el dashboard. Confirma inferencia pagada y carga sintética, luego ingresa las contraseñas locales cuando se soliciten.

Resultado esperado: el dashboard registra embeddings documentales reales e inserción en ADB dentro del schema privado de p001. Si el corpus ya existe, no fuerces una recarga ni borres filas. Antes de preguntar, confirma que el archivo de calibración privado es el aprobado y compatible.

## 4. Ejecuta y revisa los cuatro casos de puerta

Ejecuta las siguientes preguntas una por una desde la lista predefinida del dashboard. Para cada solicitud pagada, confirma explícitamente el consumo OCI. Registra el estado visible y revisa evidencia antes de continuar.

| Caso | Resultado esperado | Comportamiento OCI por comprobar |
|---|---|---|
| T01 — endpoint v1 | `answered`; `PATCH /v1/disbursements/{disbursement_id}` | Ocurren query embedding, búsqueda vectorial filtrada por versión y chat. La evidencia seleccionada es la sección v1 de actualización de estado. |
| T03 — endpoint de settlement v2 | `answered`; `PUT /v2/disbursements/{disbursement_id}/status` | Ocurren query embedding, búsqueda vectorial limitada a v2 y chat. La evidencia seleccionada es la sección v2 de settlement status. |
| T05 — actualización ambigua | `needs_clarification` | El control de aplicación solicita versión. No debe haber llamada de embedding, vector search ni chat. |
| T10 — SLA de disponibilidad | `insufficient_evidence` | Puede haber recuperación, pero el sistema no publica un SLA inventado ni una respuesta de chat sin evidencia seleccionada. |

Para T01 y T03, revisa lo siguiente en **Referencia del ejercicio vs. respuesta obtenida**, **Ejecución de servicios** y **Afirmaciones y evidencia verificable**:

- La respuesta observada coincide con los hechos de referencia y el estado esperado.
- `version_scope_pass` y `citation_checks_pass` son verdaderos.
- La evidencia aceptada está diferenciada de los candidatos recuperados.
- El extracto seleccionado declara directamente la ruta afirmada.
- `cosine_distance` solo expresa proximidad: una distancia menor no demuestra que el candidato respalde la afirmación.
- La traza identifica ADB, query embedding, vector search y chat como operaciones independientes con sus propios tiempos.

Para T05 y T10, confirma que el dashboard distingue una decisión de aplicación de una respuesta del modelo. Una aclaración o abstención correcta es un resultado exitoso para ese caso.

## 5. Registra el resultado de forma segura

Actualiza **Mi historial de ejecuciones** y verifica que cada reporte pertenece a p001. En la bitácora privada de facilitación guarda únicamente resumen seguro, estado, tiempos, contadores de uso y resultado de revisión humana. No copies contraseñas, wallets, perfiles OCI, vectores completos, errores crudos del proveedor ni borradores rechazados.

## 6. Decisión posterior al ensayo

Aprueba p001 solo si los cuatro casos cumplen sus criterios y una persona revisó los extractos citados. Ante un error operacional, deja el caso pendiente, conserva su reporte seguro e investiga en privado. No lo reemplaces por un fixture, una respuesta de referencia ni un fallback local.

Después de aprobar p001, los prerrequisitos operativos restantes son identidades de participantes, schemas/tablas aislados, entrega privada, al menos un preflight en macOS y Linux, y el plan de oleadas del workshop.
