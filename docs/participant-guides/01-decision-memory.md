# Workshop 1: Economía de Tokens y Memoria de Decisiones en OCI

## Resultado

Cada participante usa Oracle AI Agent Memory SDK desde Python para persistir, recuperar y reutilizar decisiones sintéticas en Autonomous Database. Después ejecuta dos llamadas reales al mismo modelo de OCI Generative AI Inference y compara los tokens y la latencia que reporta el proveedor.

**Mensaje para Khipu:** el agente conserva decisiones de ingeniería útiles, no conversaciones completas, y recupera solo el contexto pertinente antes de llamar al modelo.

## Aprendizajes

1. Diseñar decisiones cortas y recuperables en vez de repetir reglas extensas en cada prompt.
2. Ejecutar `add_memory` y `search` contra Oracle AI Agent Memory respaldado por ADB.
3. Usar un alcance individual, otro compartido por equipo y un alcance de control.
4. Diferenciar aislamiento de recuperación de autorización de producción.
5. Comparar telemetría real de OCI para un prompt repetitivo y un prompt con memoria recuperada.

## Actividades del recorrido

1. Validar el entorno local, la sesión OCI, el wallet y el acceso de runtime sin llamar al modelo.
2. Leer el SDK y ubicar los alcances, la persistencia, la recuperación y el aislamiento.
3. Persistir y recuperar dos decisiones procedurales sintéticas en Autonomous Database.
4. Ejecutar la comparación real de dos solicitudes on-demand a OCI Generative AI.
5. Analizar en Streamlit la evidencia de memoria, aislamiento, telemetría y calidad de respuesta.
6. Explicar los límites del patrón y su evolución hacia una arquitectura de producción.

## Antes de comenzar

El código se obtiene desde el repositorio público del workshop: [KarinaGalindezOra/kipu-workshop-oci-ai](https://github.com/KarinaGalindezOra/kipu-workshop-oci-ai). El facilitador puede compartir este mismo enlace mediante un QR; el QR solo dirige al repositorio público y no contiene credenciales.

El workshop usa un **tenant trial centralizado**, una Autonomous Database y un memory store precreados. Cada participante trabaja individualmente desde su propio computador Windows con PowerShell y recibe por un canal privado:

- Un código lógico de aislamiento, por ejemplo `T01` y `P01`. Para diez participantes se asignan pares únicos como `T01/P01`, `T02/P01` hasta `T10/P01`.
- Un usuario temporal de aplicación de ADB, distinto de `ADMIN` y del propietario del esquema de memoria.
- Un wallet mTLS privado, su contraseña y un archivo de sesión `.ps1` con valores no secretos.
- Confirmación de que su identidad OCI individual tiene acceso al modelo on-demand aprobado.

La ADB y el memory store son compartidos como infraestructura; la terminal, identidad OCI, usuario temporal, wallet, códigos de alcance y evidencia son individuales. En esta guía, `TeamCode` identifica un límite lógico de aislamiento y no implica que dos personas compartan una ejecución.

> Solo se permiten datos sintéticos del repositorio. No ingreses contratos, clientes, credenciales, código interno ni información de Khipu.

## Paso 1: preparar Python y validar el algoritmo

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[lab01,dev,ui]"
python -m pytest labs/lab01_agent_memory/tests/test_participant_lab.py labs/lab01_agent_memory/tests/test_sdk_exercise.py -q
```

**Resultado esperado:** las pruebas pasan. No crean recursos OCI; verifican alcances deterministas e inserciones idempotentes.

## Paso 2: leer el código que ejecutarás contra ADB

Abre [sdk_exercise.py](../../labs/lab01_agent_memory/src/lab01_agent_memory/sdk_exercise.py) y [run_participant_sdk_lab.py](../../labs/lab01_agent_memory/scripts/run_participant_sdk_lab.py).

El primer archivo construye los alcances `tNN:pNN`, `tNN:shared` y `tNN:control`. El segundo crea `OracleAgentMemory` con `SchemaPolicy.REQUIRE_EXISTING`, `SearchStrategy.KEYWORD` y una conexión mTLS.

La operación es real y visible: `add_memory(..., memory_type="guideline")` persiste una regla procedural y `search(..., user_id=..., exact_user_match=True, record_types=["guideline"])` la recupera desde Agent Memory. El filtro explícito evita presentar mensajes, hechos o preferencias como si fueran un procedimiento. Como Lab 1 usa `KEYWORD`, el bundle separa la pregunta de negocio de la consulta de recuperación: para Payments, `idempotency` recupera de manera determinista la regla de pagos. El propietario creó el store una única vez; el participante no puede recrearlo.

## Paso 3: cargar la sesión privada

Por un canal privado recibirás un wallet privado y un archivo de sesión `.ps1` privado. Ese archivo contiene rutas y referencias no secretas: tu perfil OCI individual, el compartment aprobado, el modelo on-demand, el usuario temporal, el alias del wallet, el owner y el identificador del store. No contiene contraseñas y no debe copiarse al repositorio.

Antes del preflight, crea **tu propia** sesión OCI en una ruta privada. Usa el navegador; no
uses `--no-browser` para una primera sesión, porque ese modo requiere previamente una API key
o un token de sesión vigente. El ejemplo usa los códigos de ensayo `P01`; sustituye solo los
valores entregados por el facilitador.

```powershell
$participantProfile = "LAB01_P01"
$participantRegion = "<tenant-home-region>"
$participantOciConfig = "C:\KhipuPrivate\oci\p01-config"
$env:BROWSER = "C:\Program Files\Google\Chrome\Application\chrome.exe"

oci session authenticate `
  --config-location $participantOciConfig `
  --profile-name $participantProfile `
  --region $participantRegion

oci session validate `
  --config-file $participantOciConfig `
  --profile $participantProfile `
  --auth security_token
```

Completa el inicio de sesión en Chrome con tu identidad OCI individual y espera que PowerShell
confirme la sesión válida. Durante este prework privado, verifica que `OCI_CONFIG_FILE` en tu
archivo de sesión apunte a `$participantOciConfig` y que `OCI_CONFIG_PROFILE` sea
`$participantProfile`; no cambies los demás valores entregados por el facilitador. La sesión,
su token y las claves locales son privados: no se copian entre laptops ni se suben al repositorio.

No cargues el archivo de sesión directamente ni modifiques sus valores después del prework.
Entrégalo al launcher mediante `-SessionFile` en el paso siguiente. El launcher lo cargará solo
dentro de ese proceso, validará la identidad OCI y el wallet, y solicitará las contraseñas de
base de datos y wallet únicamente en la terminal local.

No pases contraseñas como argumentos ni las declares en archivos `.env` compartidos.

Verifica que `LAB01_MEMORY_SCHEMA_OWNER` y `LAB01_MEMORY_STORE_ID` sean valores distintos: el primero nombra el esquema owner de memoria; el segundo nombra el store lógico creado dentro de ese esquema. No intercambies ambos valores.

## Paso 4: preflight real sin inferencia

En Windows, el facilitador entrega un archivo privado de sesión que solo configura rutas y
parámetros asignados. No se versiona, no contiene contraseñas y no debe compartirse entre
participantes. Ejecuta primero el preflight:

```powershell
$participantSession = "C:\KhipuPrivate\sessions\T01-P01-session.ps1"
powershell -ExecutionPolicy Bypass -File .\labs\lab01_agent_memory\scripts\run_participant_live.ps1 `
  -TeamCode T01 `
  -ParticipantCode P01 `
  -SessionFile $participantSession `
  -Preflight
```

Usa la ruta real privada entregada por el facilitador. No copies la notación de marcador de posición de ejemplos anteriores: PowerShell interpreta `<` como un operador.

El programa solicitará las contraseñas de base de datos y wallet localmente. No llama al modelo
ni consume inferencias. Debe terminar con:

```text
LAB01_OCI_IDENTITY_CHECK True
LAB01_PREFLIGHT_DATABASE_ACCESS True
LAB01_PREFLIGHT_MEMORY_STORE_ACCESS True
LAB01_PREFLIGHT_INFERENCE_CLIENT_READY True
LAB01_PREFLIGHT_COMPLETE
```

## Paso 5: dos ejercicios reales de memoria sin inferencia

Elige una de las dos reglas sintéticas aprobadas. Este paso es real: persiste la regla elegida
en tu alcance individual de Agent Memory en ADB, la recupera con `KEYWORD` y comprueba que el
procedimiento de control no es visible. **No llama a OCI Generative AI, no consume inferencias ni
requiere una llamada a la API de identidad OCI.**

Ejemplo con la decisión de idempotencia:

```powershell
$participantSession = "C:\KhipuPrivate\sessions\T01-P01-session.ps1"
powershell -ExecutionPolicy Bypass -File .\labs\lab01_agent_memory\scripts\run_participant_live.ps1 `
  -TeamCode T01 `
  -ParticipantCode P01 `
  -SessionFile $participantSession `
  -MemoryExercise payment-idempotency
```

Después, recupera la segunda decisión:

```powershell
powershell -ExecutionPolicy Bypass -File .\labs\lab01_agent_memory\scripts\run_participant_live.ps1 `
  -TeamCode T01 `
  -ParticipantCode P01 `
  -SessionFile $participantSession `
  -MemoryExercise contract-compatibility
```

El resultado esperado es:

```text
LAB01_MEMORY_EXERCISE_READY
SELECTED_PROCEDURE <assigned-procedure>
PERSISTENCE_CONFIRMED True
ISOLATION_PASS True
NO_OCI_INFERENCE True
```

Cada ejercicio guarda su JSON seguro por separado: `memory-exercise-payment-idempotency-evidence.json`
y `memory-exercise-contract-compatibility-evidence.json`. Ábrelos en el dashboard para verificar
que cambian la regla, la consulta y el resultado recuperado sin hacer llamadas al modelo. La regla
ya existente en una segunda ejecución es normal: prueba que la memoria persiste y que el ejercicio
es idempotente.

### Discusión técnica: dónde entra la memoria en un agente

Con las dos evidencias abiertas, responde antes de la comparación final:

```text
User question
  -> retrieve scoped procedural memory from ADB
  -> compose compact context
  -> OCI Generative AI inference
  -> response or downstream tool/action
```

La memoria pertenece antes de la inferencia: decide qué contexto se recupera y se envía al
modelo. Este workshop no implementa herramientas ni autonomía; demuestra un componente real y
gobernado que un agente puede usar. La acción posterior queda deliberadamente fuera del alcance.

## Paso 6: medir tokens con dos inferencias OCI

Usa el bundle de Payments. Sustituye solo los códigos que te asignó el facilitador; no modifiques el usuario ni el propietario del esquema.

```powershell
$participantSession = "C:\KhipuPrivate\sessions\T01-P01-session.ps1"
powershell -ExecutionPolicy Bypass -File .\labs\lab01_agent_memory\scripts\run_participant_live.ps1 `
  -TeamCode T01 `
  -ParticipantCode P01 `
  -SessionFile $participantSession
```

El programa pide la contraseña del usuario de aplicación y la del wallet de forma oculta. Después realiza exactamente dos inferencias on-demand con datos sintéticos: una con decisiones repetidas en el prompt y otra con solo la decisión recuperada desde Agent Memory. No quedan contraseñas, wallets ni tokens de autenticación en la evidencia.

La consola muestra los hitos `PERSIST`, `RETRIEVE`, `ISOLATE` y `COMPARE`. El último confirma que
se realizan exactamente dos llamadas de OCI Generative AI.

`LAB01_MEMORY_STORE_ID` identifica el store lógico que el SDK abre; corresponde a
`MEMORY_STORE_NAME` en ADB. No reemplaces ese valor por `MEMORY_STORE_UID`, que es
un identificador interno de la base de datos y no es válido para el SDK.

**Resultado esperado:**

```text
LAB01_OCI_SDK_READY
SCHEMA_POLICY REQUIRE_EXISTING
SEARCH_STRATEGY KEYWORD
RETRIEVAL_QUERY idempotency
RETRIEVED_PROCEDURES payment-idempotency
PERSISTED_PROCEDURES payment-idempotency,contract-compatibility
INDIVIDUAL_CREATED 2
INDIVIDUAL_EXISTING 0
PERSISTENCE_CONFIRMED True
ISOLATION_PASS True
BASELINE_PROMPT_TOKENS <provider_reported_value>
MEMORY_PROMPT_TOKENS <provider_reported_value>
INPUT_TOKEN_REDUCTION <provider_reported_value>
TOKEN_QUALITY_PASS True
```

El resultado confirma que se crearon o reencontraron decisiones individuales, que al menos una `guideline` fue recuperada por búsqueda de palabras clave y que una consulta por el procedimiento de control no devolvió contenido desde ese alcance. También confirma que OCI devolvió dos bloques completos de uso y que el prompt con memoria usó menos tokens de entrada sin degradar los criterios de respuesta. En una segunda ejecución, lo esperado es `INDIVIDUAL_CREATED 0` e `INDIVIDUAL_EXISTING 2`: la prueba de que las reglas permanecieron en ADB y que el comando es idempotente.

## Paso 6B: experimento ampliado de economía de contexto (opcional)

Completa este paso solo después de aprobar el recorrido base de dos inferencias. El experimento
ampliado no sustituye esa comparación: convierte el mismo principio en una prueba más rigurosa.
Persiste un catálogo de cinco decisiones sintéticas, recupera la regla principal dentro de tu
alcance individual y compara cuatro variantes con **la misma pregunta, el mismo modelo y el mismo
límite de salida**. Lo único que cambia es el contexto enviado al modelo.

```powershell
$participantSession = "C:\KhipuPrivate\sessions\T01-P01-session.ps1"
powershell -ExecutionPolicy Bypass -File .\labs\lab01_agent_memory\scripts\run_participant_live.ps1 `
  -TeamCode T01 `
  -ParticipantCode P01 `
  -SessionFile $participantSession `
  -ContextExperiment
```

La confirmación explícita está incorporada al launcher. Esta corrida realiza exactamente **cuatro**
llamadas on-demand a OCI Generative AI, con datos sintéticos aprobados, y produce
`context-economy-experiment-evidence.json`. No copies contraseñas, wallet, token de sesión ni la
salida completa de la consola al repositorio.

Las variantes son:

1. **All rules baseline**: reenvía el catálogo completo; es el control deliberadamente amplio.
2. **Retrieved top 1**: usa solamente la regla recuperada de Agent Memory; es el diseño objetivo.
3. **Relevant plus distractors**: añade decisiones válidas pero no necesarias para observar el costo
   del contexto adicional.
4. **Payment and risk**: compara otra combinación de contexto acotado y sintético.

El resultado es válido solamente si la evidencia confirma `REQUIRE_EXISTING`, `KEYWORD`,
persistencia, aislamiento, calidad de todas las respuestas y contabilidad de tokens consistente.
En el dashboard, abre la pestaña **5. Experimentos reales** y carga ese JSON. Allí compara la
telemetría por variante y discute por qué la recuperación selectiva puede reducir los tokens de
entrada sin reemplazar los demás controles de producción.

## Simulación visual opcional después del recorrido obligatorio

No repitas la ejecución real durante el workshop: cada recorrido autorizado usa exactamente dos
llamadas on-demand. El dashboard tiene una sección rotulada **“Simulación visual local — no
consulta ADB ni OCI”**. Sus botones no ejecutan el SDK, no persisten ni recuperan memoria real y
no generan evidencia. Úsala exclusivamente para explicar el algoritmo de forma visual.

- La ejecución real es idempotente: las mismas reglas ya persistidas aparecen como existentes.
- En `KEYWORD`, una palabra de recuperación elegida deliberadamente hace visible el vínculo entre
  la regla y el resultado.
- El alcance compartido sirve para conversar sobre conocimiento reutilizable; no representa
  autorización de producción.

## Paso 7: visualizar evidencia real

Desde el computador local, inicia el dashboard:

```powershell
python -m streamlit run labs/lab01_agent_memory/ui/app.py
```

Carga los dos JSON `memory-exercise-*-evidence.json` y después `oci-inference-evidence.json` en
**Evidencia de ejecución del equipo**. La pantalla distingue claramente la memoria real en ADB
de la comparación de tokens de entrada, salida, total y latencia reportada por OCI Generative AI.
Si completaste el Paso 6B, abre **5. Experimentos reales** para cargar
`context-economy-experiment-evidence.json`; este JSON se valida por separado y no altera la
evidencia base.

La reducción de tokens de entrada proviene del bloque `usage` de OCI Generative AI. No equivale por sí sola a la facturación total de la solución: no incluye costos de memoria, almacenamiento o recuperación.

## Qué demuestra el aislamiento — y qué no

La consulta en `t01:p01` no recupera el dato presembrado en `t01:control`. Es una demostración real de recuperación con alcance, respaldada por Agent Memory y ADB.

No equivale por sí sola a seguridad de filas: un usuario que pudiera editar el código y consultar otro `user_id` podría intentar otro alcance. El workshop usa datos sintéticos y usuarios temporales. En producción, un servicio debe derivar el alcance desde la identidad autenticada y complementarlo con controles de base de datos, IAM y red.

## Puerta de evidencia

- [ ] Ejecuté las pruebas locales.
- [ ] Leí `OracleAgentMemory`, `add_memory` y la búsqueda con `record_types=["guideline"]` en el código.
- [ ] Ejecuté una recuperación real sin inferencia y obtuve `NO_OCI_INFERENCE True`.
- [ ] Ejecuté el SDK contra ADB con mi usuario temporal.
- [ ] Obtuve `PERSISTENCE_CONFIRMED True`, `ISOLATION_PASS True` y `TOKEN_QUALITY_PASS True`.
- [ ] Verifiqué que `MEMORY_PROMPT_TOKENS` es menor que `BASELINE_PROMPT_TOKENS`.
- [ ] Si ejecuté el experimento ampliado, comparé cuatro variantes con la misma pregunta y guardé
  solo `context-economy-experiment-evidence.json`.
- [ ] Guardé solo el JSON de evidencia; no guardé ni compartí credenciales.
- [ ] Expliqué por qué el alcance es una frontera de recuperación y no una autorización completa.
