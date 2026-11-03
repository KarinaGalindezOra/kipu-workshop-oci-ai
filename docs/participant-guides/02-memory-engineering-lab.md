# Workshop 1 Extension: Diseño, Evaluación y Gobernanza de Memoria

Este bloque amplía el recorrido base del Workshop 1. No sustituye el preflight, la memoria
procedural base ni la comparación controlada de dos llamadas. Su propósito es que cada
participante pase de ejecutar un ejemplo preparado a **diseñar, medir y defender** una decisión
de memoria para un agente.

> Usa únicamente reglas sintéticas. No copies datos de clientes, contratos reales, credenciales,
> código interno ni información sensible en archivos o prompts del laboratorio.

## Actividad 1: Diseñar una regla procedural sintética

Copia el template a una ruta privada de trabajo; no edites el template versionado directamente.

```powershell
New-Item -ItemType Directory -Force "C:\KhipuPrivate\exercises" | Out-Null
Copy-Item .\labs\lab01_agent_memory\exercises\participant-procedure-template.json `
  "C:\KhipuPrivate\exercises\my-procedure.json"
notepad "C:\KhipuPrivate\exercises\my-procedure.json"
```

Modifica solamente contenido sintético y conserva esta estructura:

- `procedure_id`: identificador estable, minúsculas, dígitos y guiones; por ejemplo
  `refund-traceability-v1`.
- `version`: formato `major.minor`; por ejemplo `1.0`.
- `domain`: dominio sintético como `payments`, `risk` o `api`.
- `trigger_terms`: palabras que deberían recuperar la regla.
- `procedure`: decisión concreta y comprobable, no una explicación genérica.
- `required_evidence`: rastros que una respuesta o proceso debe preservar.

## Actividad 2: Validar la definición antes de ADB

Valida primero tu archivo. Esta validación es local; no llama a ADB ni a OCI Generative AI.

```powershell
.\.venv\Scripts\python.exe .\labs\lab01_agent_memory\scripts\validate_procedure.py `
  "C:\KhipuPrivate\exercises\my-procedure.json"
```

El resultado esperado comienza con `LAB01_PROCEDURE_VALID True`. Después, si deseas validar
todo el paquete, ejecuta también las pruebas:

```powershell
.\.venv\Scripts\python.exe -m pytest .\labs\lab01_agent_memory\tests -q
```

Luego revisa tu JSON contra los criterios del template. Si cambias el identificador, la versión,
los términos o los campos obligatorios de forma inválida, el runner rechazará el archivo antes de
persistir nada.

Preguntas de diseño:

1. ¿La regla describe una decisión reutilizable o una conversación completa?
2. ¿Los trigger terms son suficientemente específicos para reducir ruido?
3. ¿La evidencia requerida permite auditar la decisión?
4. ¿La regla cambia de versión si cambia su comportamiento?

## Actividad 3: Persistir y evaluar la regla propia en Agent Memory

Este comando abre el memory store existente con `SchemaPolicy.REQUIRE_EXISTING`, persiste la
regla en tu scope individual, ejecuta una recuperación dirigida, una amplia y una de control.
No llama al modelo y no consume inferencias OCI.

```powershell
$participantSession = "C:\KhipuPrivate\sessions\T01-P01-session.ps1"
$myProcedure = "C:\KhipuPrivate\exercises\my-procedure.json"

powershell -ExecutionPolicy Bypass -File .\labs\lab01_agent_memory\scripts\run_participant_live.ps1 `
  -TeamCode T01 `
  -ParticipantCode P01 `
  -SessionFile $participantSession `
  -CustomProcedure $myProcedure
```

El resultado esperado contiene:

```text
LAB01_CUSTOM_PROCEDURE_EXERCISE_READY <procedure-id>
PERSISTENCE_CONFIRMED True
TARGETED_RETRIEVAL_CONFIRMED True
NEGATIVE_CONTROL_PASS True
NO_OCI_INFERENCE True
```

La evidencia segura queda en `artifacts/lab01/<team>/<participant>/custom-procedure-evidence.json`.
Una segunda ejecución es idempotente: indicará que la regla ya existe en lugar de duplicarla.

## Actividad 4: Interpretar retrieval, no solo “si funciona”

Abre el dashboard y ve a **6. Diseño y evaluación**. Carga el JSON anterior o selecciónalo desde
la lista de artifacts detectados.

Interpreta los tres casos:

| Caso | Lo que demuestra |
| --- | --- |
| `targeted` | Los trigger terms elegidos recuperan la regla que el participante diseñó. |
| `broad` | Un solo trigger term puede traer más resultados y, por tanto, más contexto del necesario. |
| `negative_control` | Una frase no relacionada no debe recuperar la regla propia. |

El control negativo prueba diseño de recuperación, no autorización. En producción, el scope debe
derivarse de una identidad autenticada y combinarse con controles de IAM, ADB y red.

## Actividad 5: Medir la economía de contexto con OCI

Después de aprobar la regla propia, vuelve al experimento de cuatro variantes descrito en la guía
principal. Mantiene pregunta, modelo, parámetros y criterios de calidad constantes; cambia solo el
conjunto de procedimientos que entra al prompt.

Este comando realiza exactamente **cuatro** llamadas on-demand a OCI Generative AI con datos
sintéticos:

```powershell
$participantSession = "C:\KhipuPrivate\sessions\T01-P01-session.ps1"

powershell -ExecutionPolicy Bypass -File .\labs\lab01_agent_memory\scripts\run_participant_live.ps1 `
  -TeamCode T01 `
  -ParticipantCode P01 `
  -SessionFile $participantSession `
  -ContextExperiment
```

La ejecución debe confirmar `PERSISTENCE_CONFIRMED True`, `ISOLATION_PASS True`,
`EXPERIMENT_VARIANTS 4` y `QUALITY_PASS True`. La evidencia resultante queda en
`artifacts/lab01/<team>/<participant>/context-economy-experiment-evidence.json` y se revisa en
la pestaña **5. Experimentos reales** de Streamlit.

Discute estos resultados antes de declarar una optimización:

1. ¿La variante con menor input tokens mantiene los criterios de calidad?
2. ¿Cuál es el efecto de introducir distractores válidos pero irrelevantes?
3. ¿Qué evidencia demostraría que un retrieval falló aunque la respuesta parezca razonable?
4. ¿Qué costos adicionales existen fuera de input tokens: memoria, ADB, retrieval, operación y
   observabilidad?

## Actividad 6: Inspección SQL de solo lectura

Esta actividad es opcional y requiere SQLcl previamente instalado. Conecta como tu usuario de
aplicación temporal, no como `ADMIN` ni como el owner. La consulta solo lee metadata del data
dictionary; no modifica Agent Memory ni tablas.

Desde una terminal donde ya cargaste tu sesión privada, configura el wallet local y conéctate:

```powershell
$sqlclBin = "C:\Tools\sqlcl\bin"
if (-not (Get-Command sql -ErrorAction SilentlyContinue)) {
  if (-not (Test-Path -LiteralPath $sqlclBin -PathType Container)) {
    throw "SQLcl was not found. Install SQLcl or update `$sqlclBin to its bin directory."
  }
  $env:Path = "$sqlclBin;$env:Path"
}

sql -V

. $participantSession
$env:TNS_ADMIN = $env:LAB01_WALLET_DIR
sql "$env:LAB01_DB_USER@$env:LAB01_DB_DSN"
```

En SQLcl, proporciona la contraseña del usuario temporal y ejecuta el script con el schema owner
y el prefijo lógico entregados por el facilitador. Ejecuta el script sin parámetros para que
SQLcl solicite ambos valores de forma visible:

```sql
@labs/lab01_agent_memory/sql/inspect_memory_store.sql
```

Para `T01`, escribe `OAM_T01_OWNER` cuando solicite el primer valor y `OAMT01` para el segundo.

Relaciona las tablas con el SDK:

- `*_MEMORY`: registros principales de memoria procedural.
- `*_RECORD_CHUNKS`: contenido recuperable.
- `*_DOCUMENT` y `*_MEMORY_LINK`: organización y relaciones.
- `*_ACTOR_PROFILE`, `*_THREAD`, `*_THREAD_SUMMARY`, `*_MESSAGE`: capacidades disponibles para
  otros patrones de memoria, aunque Lab 1 se concentra en decisiones procedurales.

## Cierre arquitectónico

Al terminar, cada participante debe poder explicar:

1. Por qué una decisión procedural no es un historial completo de conversación.
2. Cómo una regla se versiona, se persiste y se recupera desde ADB.
3. Por qué la calidad de retrieval precede a la optimización de tokens.
4. Qué diferencia hay entre una frontera de retrieval y una autorización de producción.
5. Qué controles se añadirían en producción: identidad derivada, Vault, IAM mínimo privilegio,
   red privada, observabilidad, evaluación continua y gobierno de cambios de reglas.
