# Guía del participante — Workshop 2

En este laboratorio construirás evidencia para responder preguntas sobre contratos API sintéticos versionados. No es una demostración de un chatbot: comprobarás qué ocurre entre la fuente, los fragmentos, la recuperación, la selección de evidencia y la respuesta OCI.

El workshop dura **180 minutos**. La instalación, la asignación privada y la validación de tu estación de trabajo se realizan **antes** de comenzar ese tiempo. Las actividades locales no son una sustitución de OCI: preparan y explican las decisiones que luego comprobarás mediante servicios reales.

## Resultado que debes entregar

Al terminar, tu carpeta local de artefactos y tu [cuaderno de trabajo](participant_workbook.md) deben permitir demostrar:

1. Una diferencia contractual entre v1 y v2, localizada en ambos documentos.
2. Nueve fragmentos manifestados, con versión, sección, líneas y hash verificables.
3. Una recuperación léxica local que aplique el filtro de versión antes del ranking.
4. Una respuesta OCI real con afirmación, cita y extracto que la sustente.
5. Una comparación entre v1 y v2 sin reutilizar evidencia de una versión en la otra.
6. Una aclaración, abstención o derivación a datos estructurados que sea correcta.

No copies contraseñas, rutas privadas, wallet, tokens ni datos de clientes en el cuaderno o en los artefactos.

## Antes de la sesión: preparación obligatoria

Debes recibir por el canal privado aprobado:

- Una identidad OCI individual.
- Tu usuario o schema de ADB y las contraseñas que se solicitan localmente.
- Tu wallet privado.
- Tu archivo privado de sesión.
- La confirmación de que puedes usar el modelo OCI autorizado.

No crees usuarios, tablas, políticas IAM ni recursos OCI. No copies esos archivos privados dentro del repositorio ni los subas a Git.

### Paso 0: descarga el repositorio

Elige una de estas alternativas.

#### Alternativa A: Git

```bash
git clone https://github.com/KarinaGalindezOra/kipu-workshop-oci-ai.git
cd kipu-workshop-oci-ai
```

#### Alternativa B: archivo ZIP

1. Abre la [página principal del repositorio](https://github.com/KarinaGalindezOra/kipu-workshop-oci-ai).
2. Selecciona **Code** y luego **Download ZIP**.
3. Descomprime el archivo descargado.
4. Abre una terminal dentro de la carpeta descomprimida `kipu-workshop-oci-ai-main`.

En los pasos siguientes, esa carpeta será la **raíz del repositorio**.

### Paso 1: verifica Python 3.11

#### Windows

```powershell
py -3.11 --version
```

#### macOS o Linux

```bash
python3.11 --version
```

Si no ves una versión 3.11, detente y solicita ayuda a la facilitación.

### Paso 2: crea el entorno e instala el proyecto

#### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,lab02,ui]"
oci --version
```

#### macOS o Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,lab02,ui]"
oci --version
```

Si usas macOS o Linux, consulta también la [guía macOS y Linux](macos_linux_participant_guide.md).

### Paso 3: activa tu sesión OCI individual y valida tu asignación privada

Carga el archivo de sesión entregado por la facilitación y crea o renueva el token local de tu identidad OCI individual. Este paso abre un navegador para iniciar sesión; no llama a OCI Generative AI, no genera embeddings y no inserta datos en ADB. Hazlo antes de abrir el dashboard y repítelo si tu token expira.

#### Windows PowerShell

La facilitación te enviará un bloque privado ya preparado para tu identidad. Pégalo sin modificarlo en una terminal dedicada. La ruta no es igual para todas las personas y no aparece en este repositorio.

```powershell
. '<private-participant-session.ps1>'
python labs/lab02_contract_rag/scripts/authenticate_oci_session.py
python labs/lab02_contract_rag/scripts/validate_environment.py --check-db
```

No escribas literalmente los caracteres `<` y `>`: son una explicación visual. No sustituyas la ruta por un wallet ni por la sesión de otra persona.

#### macOS o Linux

La facilitación te enviará la ruta de tu archivo dotenv privado. Pega el bloque recibido; tendrá esta forma:

```bash
python labs/lab02_contract_rag/scripts/authenticate_oci_session.py \
  --session-file /private/path/lab02-participant.env
python labs/lab02_contract_rag/scripts/validate_environment.py \
  --session-file /private/path/lab02-participant.env \
  --check-db
```

El resultado esperado primero muestra `OCI_SESSION_AUTHENTICATED` y `OCI_SESSION_VALID`; después, la validación de base de datos muestra `status` igual a `passed` y `database_session` igual a `participant_schema`. Si falla, detente y avisa a la facilitación. No sustituyas tu perfil, wallet o archivo de sesión por el de otra persona.

### Paso 4: abre el dashboard

#### Windows PowerShell

```powershell
python labs/lab02_contract_rag/scripts/run_dashboard.py --port 8502
```

#### macOS o Linux

```bash
python labs/lab02_contract_rag/scripts/run_dashboard.py \
  --session-file /private/path/lab02-participant.env \
  --port 8502
```

Abre `http://127.0.0.1:8502` en tu navegador. Verás **Ejecutar e inspeccionar** y **Mi historial de ejecuciones**. El dashboard es local: no lo expongas mediante un proxy público.

Si el terminal informa que el puerto `8502` no está disponible, no es un error de OCI: otro dashboard local ya lo está usando. Cierra ese proceso o inicia este dashboard con `--port 8503` y abre `http://127.0.0.1:8503`.

## Durante la sesión: laboratorio de 180 minutos

Abre el [cuaderno de trabajo](participant_workbook.md) y cópialo a tu carpeta de artefactos. Hazlo en la misma terminal donde cargaste tu sesión privada en el Paso 3. No copies el cuaderno dentro del repositorio ni incluyas contraseñas, wallet, tokens o datos de clientes.

#### Windows PowerShell

```powershell
$artifactDir = Join-Path $env:LAB02_REPORT_ROOT $env:LAB02_PARTICIPANT_ID
New-Item -ItemType Directory -Force -Path $artifactDir | Out-Null
Copy-Item `
  labs\lab02_contract_rag\docs\participant_workbook.md `
  (Join-Path $artifactDir "participant_workbook.md")
```

#### macOS o Linux

```bash
artifact_dir="${LAB02_REPORT_ROOT}/${LAB02_PARTICIPANT_ID}"
mkdir -p "$artifact_dir"
cp labs/lab02_contract_rag/docs/participant_workbook.md \
  "$artifact_dir/participant_workbook.md"
```

Conserva abierta la terminal y el dashboard.

| Minutos | Módulo | Trabajo práctico | Entregable observable |
|---:|---|---|---|
| 0–10 | M0: caso y objetivo | Identificar una respuesta plausible, pero contaminada entre versiones. | Riesgo de versión explicado. |
| 10–25 | M1: fuente de verdad | Comparar v1 y v2 directamente en los archivos Markdown. | Tabla contractual completada. |
| 25–40 | M2: fragmentos y manifiesto | Ejecutar la inspección local del corpus. | Reporte de nueve fragmentos y un hash localizado. |
| 40–55 | M3: recuperación local | Ejecutar recuperación léxica local para T03. | Candidatos v2, ranking y evidencia aceptada. |
| 55–70 | M4: comparación local | Ejecutar recuperación local para T08 y separar v1 de v2. | Dos conjuntos de evidencia sin contaminación. |
| 70–80 | Pausa | — | — |
| 80–95 | M5: ingesta OCI | Preparar el corpus sintético en el schema individual. | Traza de embeddings y ADB; nueve fragmentos. |
| 95–110 | M6: primera respuesta OCI | Ejecutar T01 o T03 con confirmación de consumo. | Respuesta, cita, extracto y traza real. |
| 110–125 | M7: evidencia versus candidatos | Revisar cada panel del dashboard y contrastar con la matriz. | Afirmación → evidencia → extracto → fuente. |
| 125–135 | M8: migración OCI | Ejecutar T06 y validar sus tres cambios. | Endpoint, campo y mapeos respaldados. |
| 135–145 | Pausa | — | — |
| 145–160 | M9: comparación OCI | Ejecutar T08 y contrastarlo con la práctica local. | Recuperaciones separadas y citas v1/v2. |
| 160–170 | M10: límites seguros | Resolver T05, T10 y T12. | Aclaración, abstención y decisión SQL correctas. |
| 170–180 | M11: cierre | Clasificar RAG/SQL y completar el cuaderno. | Entrega individual verificable. |

### M0 y M1 — fuente de verdad antes de recuperar

Lee `labs/lab02_contract_rag/data/contract_v1.md` y `labs/lab02_contract_rag/data/contract_v2.md`. Completa las secciones 1 y 2 del cuaderno. En particular, contrasta método, endpoint, campo de solicitud, estados, header de idempotencia, respuesta y error. No ejecutes OCI todavía.

Preguntas para discutir:

- ¿Por qué `PATCH /v1/...` junto con `Idempotency-Key` sería una respuesta incorrecta aunque ambas partes existan en el corpus?
- ¿Qué cambio debe realizar una integración que envía `payment_status=PAID` al migrar a v2?

### M2 — inspeccionar corpus, fragmentos y manifiesto

Este paso no usa OCI, no pide contraseña y no genera embeddings. Verifica que el corpus congelado contiene nueve fragmentos y registra los metadatos solicitados.

#### Windows PowerShell

```powershell
python labs/lab02_contract_rag/scripts/run_local_practice.py inspect
```

#### macOS o Linux

```bash
python labs/lab02_contract_rag/scripts/run_local_practice.py \
  --session-file /private/path/lab02-participant.env \
  inspect
```

El resultado debe indicar `OCI_EXECUTED False` y `CHUNK_COUNT 9`. Abre el `CORPUS_REPORT` local y registra una fila v1 y otra v2 en el cuaderno: sección, líneas, `chunk_id` y `content_hash`.

### M3 — practicar recuperación local para T03

La práctica local usa ranking léxico determinista y salida extractiva. Sirve para observar filtro y ranking; **no valida embeddings, ADB ni generación OCI**.

```powershell
python labs/lab02_contract_rag/scripts/run_local_practice.py retrieve --case-id T03
```

En macOS o Linux, agrega tu `--session-file` antes de `retrieve`. El resultado esperado es `STATUS answered`, candidatos solo v2 y una evidencia de la sección **Endpoint de estado de liquidación**. Abre el `EVIDENCE_REPORT` y responde en el cuaderno:

1. ¿Qué candidatos quedaron excluidos antes del ranking y por qué?
2. ¿Qué valor expresa el ranking léxico?
3. ¿Por qué el candidato con mayor coincidencia no sustituye una revisión del extracto?

### M4 — comparar localmente sin mezclar versiones

```powershell
python labs/lab02_contract_rag/scripts/run_local_practice.py retrieve --case-id T08
```

El resultado esperado contiene evidencia `Idempotencia` de v1 y v2. Registra por separado `X-Idempotency-Key` y `Idempotency-Key`. Si falta una de las versiones, no completes la respuesta con conocimiento previo: revisa el filtro y avisa a la facilitación.

### Dónde revisar los reportes

Los reportes de M2, M3 y M4 son archivos JSON locales. La terminal siempre imprime la ruta exacta como `CORPUS_REPORT` o `EVIDENCE_REPORT`; ábrela para revisar fragmentos, candidatos, afirmaciones y citas. Estos archivos se guardan bajo `artifacts/lab02/local-practice/<participant-id>/` y están excluidos de Git. No se muestran en el dashboard porque no son ejecuciones OCI.

#### Windows PowerShell

Reemplaza `<ruta-impresa-por-la-terminal>` por la ruta completa que acabas de recibir:

```powershell
notepad '<ruta-impresa-por-la-terminal>'
```

#### macOS

```bash
open '<ruta-impresa-por-la-terminal>'
```

#### Linux

```bash
xdg-open '<ruta-impresa-por-la-terminal>'
```

Los resultados OCI de M5 en adelante se revisan en el dashboard local: **Ejecutar e inspeccionar** muestra la ejecución recién terminada y **Mi historial de ejecuciones** conserva las ejecuciones de tu propia sesión. Esos reportes también se guardan en tu carpeta privada de artefactos configurada por la facilitación.

### M5 — preparar el corpus en OCI

En el dashboard, selecciona **Preparar mi corpus sintético**. Confirma las casillas de consumo y carga, e ingresa las contraseñas localmente si se solicitan. El flujo realiza embeddings OCI reales e inserta o reutiliza de forma compatible los nueve fragmentos sintéticos en tu schema individual.

Después de una ingesta exitosa, congela la calibración compatible con ese corpus, región y modelo. Este paso usa únicamente las preguntas sintéticas de desarrollo, hace embeddings de consulta reales y no llama al modelo de chat:

```powershell
python labs/lab02_contract_rag/scripts/calibrate_participant.py --confirm-live-inference
```

Si informa `CALIBRATION_ALREADY_VALID`, no realizó llamadas nuevas. Si informa `CALIBRATION_WRITTEN`, quedó una calibración local privada compatible. Si falla, no avances a una consulta OCI: avisa a la facilitación.

Registra en el cuaderno:

- Cantidad de fragmentos.
- `corpus_id` activo.
- Operaciones OCI/ADB que aparecieron en la traza.
- Diferencia entre el reporte de M2 y esta carga OCI.

### M6 y M7 — ejecutar y auditar una respuesta OCI

Selecciona T01 o T03, marca **Preguntar usando OCI** y confirma el consumo aprobado. Después revisa, en este orden:

1. **Respuesta de referencia del ejercicio:** criterio congelado antes de llamar a OCI.
2. **Respuesta obtenida de OCI:** texto publicado después de validar referencias.
3. **Comprobaciones automáticas:** estado, aislamiento de versión y referencias existentes.
4. **Ejecución de servicios:** embedding, búsqueda ADB y chat; una operación omitida también es información.
5. **Afirmaciones y evidencia verificable:** extracto, versión, sección, líneas y hash.
6. **Candidatos recuperados:** candidatos evaluados, incluso aquellos que no se usaron en la respuesta.

Cuando la búsqueda vectorial inicial no contiene una sección necesaria para un aspecto solicitado, la traza puede mostrar `adb_section_coverage`. Es una recuperación estructurada de completitud, limitada al mismo corpus, API, versión, clasificación y espacio de embeddings; no mezcla versiones ni sustituye la revisión semántica del extracto.

Una `cosine_distance` menor significa que un candidato vectorial está más cerca de la consulta. No prueba que responda la pregunta. La evidencia se publica solo si el extracto respalda la afirmación concreta.

### M8 y M9 — migración y comparación OCI

Ejecuta T06. Comprueba tres aspectos distintos: endpoint nuevo, cambio de `payment_status` a `status`, y mapeo de estados. Después ejecuta T08 y contrasta el resultado con M4.

En la comparación OCI debes poder indicar qué cita es v1 y cuál es v2. No aceptes una respuesta que presente un header sin identificar su versión.

### M10 — comprobar límites correctos

Ejecuta o revisa los casos siguientes:

- **T05:** no especifica versión. Resultado correcto: `needs_clarification`; no debe asumir v2 ni consumir chat.
- **T10:** solicita un SLA no documentado. Resultado correcto: `insufficient_evidence`; puede haber recuperación real, pero no una garantía inventada.
- **T12:** solicita un conteo operacional. Resultado correcto: `structured_data_required`; no debe inventar SQL ni un número.

Registra qué operaciones ocurrieron y cuáles se omitieron. Un modelo que se abstiene correctamente es un resultado funcional, no un fallo.

### M11 — cierre y entrega

Completa la sección final del cuaderno y revisa **Mi historial de ejecuciones**. Entrega únicamente los artefactos solicitados por la facilitación; no subas información privada a Git ni la compartas por chat.

## Si algo falla

Consulta [Resolución de problemas para participantes](troubleshooting.md). No envíes por chat contraseñas, archivos wallet, perfiles OCI, contenido de sesiones ni mensajes de error completos.
