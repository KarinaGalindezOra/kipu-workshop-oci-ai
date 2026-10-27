# Workshop 1 Extension: Diseño, Evaluación y Gobernanza de Memoria

Este bloque amplía el recorrido base: cada participante diseña, valida y defiende una decisión de memoria sintética. No sustituye el preflight, el ejercicio de memoria base ni la comparación controlada de dos llamadas.

> Usa únicamente reglas sintéticas. No copies datos de clientes, contratos reales, credenciales, código interno ni información sensible en archivos o prompts del laboratorio.

## Actividad 1: Diseñar una regla procedural sintética

Copia el template a una ruta privada de trabajo; no edites el template versionado directamente.

```powershell
New-Item -ItemType Directory -Force "C:\KhipuPrivate\exercises" | Out-Null
Copy-Item .\labs\lab01_agent_memory\exercises\participant-procedure-template.json `
  "C:\KhipuPrivate\exercises\my-procedure.json"
notepad "C:\KhipuPrivate\exercises\my-procedure.json"
```

Modifica contenido sintético y conserva `procedure_id`, `version`, `domain`, `trigger_terms`, `procedure` y `required_evidence`. La regla debe representar una decisión reutilizable y comprobable; no un historial de conversación.

## Actividad 2: Validar localmente

```powershell
.\.venv\Scripts\python.exe .\labs\lab01_agent_memory\scripts\validate_procedure.py `
  "C:\KhipuPrivate\exercises\my-procedure.json"
```

El resultado debe comenzar con `LAB01_PROCEDURE_VALID True`. Este paso no llama a ADB ni a OCI Generative AI. Para validar el paquete completo:

```powershell
.\.venv\Scripts\python.exe -m pytest .\labs\lab01_agent_memory\tests -q
```

## Actividad 3: Persistir y evaluar la regla propia

Este comando abre el store existente con `SchemaPolicy.REQUIRE_EXISTING`, persiste la regla en tu alcance individual y realiza recuperación dirigida, amplia y de control. No invoca el modelo.

```powershell
$participantSession = "C:\KhipuPrivate\sessions\T01-P01-session.ps1"
$myProcedure = "C:\KhipuPrivate\exercises\my-procedure.json"

powershell -ExecutionPolicy Bypass -File .\labs\lab01_agent_memory\scripts\run_participant_live.ps1 `
  -TeamCode T01 `
  -ParticipantCode P01 `
  -SessionFile $participantSession `
  -CustomProcedure $myProcedure
```

Resultado esperado:

```text
PERSISTENCE_CONFIRMED True
TARGETED_RETRIEVAL_CONFIRMED True
NEGATIVE_CONTROL_PASS True
NO_OCI_INFERENCE True
```

La evidencia segura queda en `artifacts/lab01/<team>/<participant>/custom-procedure-evidence.json`. Una segunda ejecución es idempotente y no duplica la regla.

## Actividad 4: Interpretar retrieval

En Streamlit abre **6. Diseño y evaluación** y selecciona el JSON anterior desde `artifacts` o súbelo. Interpreta:

| Caso | Lo que demuestra |
| --- | --- |
| `targeted` | Los trigger terms elegidos recuperan la regla diseñada. |
| `broad` | Un solo trigger term puede traer más contexto del necesario. |
| `negative_control` | Una frase no relacionada no debe recuperar la regla propia. |

Esto evalúa retrieval; no sustituye controles de IAM, ADB, red ni un scope derivado de identidad autenticada en producción.

## Actividad 5: Economía de contexto con OCI

Después de aprobar la regla propia, ejecuta el experimento de cuatro variantes de la guía principal. Mantiene pregunta, modelo, parámetros y criterios de calidad; cambia solo el contexto procedimental. Discute calidad, distractores, fallas de retrieval y costos de memoria, ADB, retrieval y operación además de input tokens.

Este comando realiza exactamente **cuatro** llamadas on-demand a OCI Generative AI con datos
sintéticos. No ejecutes otra modalidad (`-Preflight`, `-MemoryExercise` o `-CustomProcedure`) en
la misma invocación.

```powershell
$participantSession = "C:\KhipuPrivate\sessions\T01-P01-session.ps1"

powershell -ExecutionPolicy Bypass -File .\labs\lab01_agent_memory\scripts\run_participant_live.ps1 `
  -TeamCode T01 `
  -ParticipantCode P01 `
  -SessionFile $participantSession `
  -ContextExperiment
```

El resultado aprobado incluye:

```text
PERSISTENCE_CONFIRMED True
ISOLATION_PASS True
EXPERIMENT_VARIANTS 4
QUALITY_PASS True
```

La evidencia segura queda en `artifacts/lab01/<team>/<participant>/context-economy-experiment-evidence.json`.
En Streamlit, abre **5. Experimentos reales** y selecciónala desde `artifacts` o súbela. La
telemetría permite comparar las variantes `all-rules-baseline`, `retrieved-top-1`,
`relevant-plus-distractors` y `payment-and-risk` con el mismo modelo y la misma pregunta.

## Actividad 6: Inspección SQL opcional y de solo lectura

Con SQLcl, el usuario temporal y el wallet configurado, desde la raíz del repositorio:

```powershell
$participantSession = "C:\KhipuPrivate\sessions\T01-P01-session.ps1"
. $participantSession
$env:TNS_ADMIN = $env:LAB01_WALLET_DIR
sql "$env:LAB01_DB_USER@$env:LAB01_DB_DSN"
```

Cuando SQLcl solicite la contraseña, escribe la contraseña del usuario temporal de ADB. El wallet
usa el archivo de auto-login local, por lo que no debes escribir su contraseña en SQLcl.

En el prompt `SQL>` ejecuta el script **sin parámetros**:

```sql
@labs/lab01_agent_memory/sql/inspect_memory_store.sql
```

SQLcl solicitará dos valores. Para el equipo de ensayo `T01`, escribe primero `OAM_T01_OWNER` y
luego `OAMT01`. El primer valor es el schema owner; el segundo es el prefijo físico de las tablas
del store. Escribe `exit` al terminar.

El script solo lee metadata. `*_MEMORY` guarda registros principales; `*_RECORD_CHUNKS` apoya contenido recuperable; las demás tablas modelan documentos, enlaces, perfiles de actor e hilos para otros patrones del SDK.

## Cierre arquitectónico

Cada participante debe explicar por qué una regla procedural no es historial completo, cómo se versiona y recupera, por qué la calidad de retrieval precede a optimizar tokens y qué controles de identidad, Vault, IAM, red y observabilidad se necesitan en producción.
