# Guía del participante — Workshop 2

Esta es la guía que debes seguir durante el workshop. Trabajarás solamente con contratos y preguntas sintéticas. No ingreses datos de clientes, información personal, tokens ni credenciales en el dashboard, la terminal o el chat.

El workshop dura **180 minutos**. La instalación, la asignación privada y la validación de tu estación de trabajo se realizan **antes** de comenzar ese tiempo.

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
```

#### macOS o Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,lab02,ui]"
```

Si usas macOS o Linux, consulta también la [guía macOS y Linux](macos_linux_participant_guide.md).

### Paso 3: valida tu asignación privada

Carga el archivo de sesión entregado por la facilitación. El comando solicita las contraseñas localmente y no invoca OCI Generative AI.

#### Windows PowerShell

La facilitación te enviará un bloque privado ya preparado para tu identidad. Pégalo sin modificarlo en una terminal dedicada. La ruta no es igual para todas las personas y no aparece en este repositorio. Tendrá esta forma:

```powershell
. '<private-participant-session.ps1>'
python labs/lab02_contract_rag/scripts/validate_environment.py --check-db
```

No escribas literalmente los caracteres `<` y `>`: son una explicación visual. No sustituyas la ruta por un wallet ni por la sesión de otra persona.

#### macOS o Linux

La facilitación te enviará la ruta de tu archivo dotenv privado. Pega el bloque recibido; tendrá esta forma:

```bash
python labs/lab02_contract_rag/scripts/validate_environment.py \
  --session-file /private/path/lab02-participant.env \
  --check-db
```

El resultado esperado muestra `status` igual a `passed` y `database_session` igual a `participant_schema`. Si falla, detente y avisa a la facilitación.

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

## Durante la sesión: ruta de 180 minutos

Descarga el [cuaderno de trabajo](participant_workbook.md) y cópialo a tu carpeta personal de artefactos antes de comenzar. Registrarás allí las decisiones y la evidencia que observarás en el dashboard.

| Minutos | Actividad | Resultado verificable |
|---:|---|---|
| 0–10 | Caso y riesgo de versiones | Explicas por qué una respuesta plausible puede pertenecer a la versión equivocada. |
| 10–25 | Comparación de contratos v1 y v2 | Registras cambios de endpoint, campo, estados e idempotencia. |
| 25–40 | Fragmentos, metadatos y manifiesto | Relacionas una sección con versión, localizador y hash. |
| 40–50 | Candidatos versus evidencia | Distingues proximidad vectorial de respaldo semántico. |
| 50–60 | Pausa | — |
| 60–75 | Preparación de corpus sintético | Verificas nueve fragmentos en tu schema individual. |
| 75–90 | Primera consulta OCI real | Ejecutas T01 o T03 y trazas la respuesta hasta su evidencia. |
| 90–105 | Revisión de evidencia | Interpretas respuesta, cita, extracto, candidatos y telemetría. |
| 105–125 | Migración y comparación | Ejecutas T06 y T08; mantienes v1 y v2 separadas. |
| 125–135 | Pausa | — |
| 135–150 | Límites correctos | Evalúas T05, T10 y T12: aclaración, abstención y datos estructurados. |
| 150–165 | RAG versus SQL controlado | Clasificas necesidades documentales, estructuradas y combinadas. |
| 165–175 | Revisión y entrega | Compruebas los artefactos solicitados en tu historial y cuaderno. |
| 175–180 | Cierre | Explicas una decisión de evidencia y una limitación del sistema. |

### Actividad 1: comparar la fuente de verdad

Abre `data/contract_v1.md` y `data/contract_v2.md`. Completa la primera tabla del cuaderno antes de usar OCI. No infieras equivalencias que no estén documentadas.

### Actividad 2: preparar y comprobar el corpus

En el dashboard, selecciona **Preparar mi corpus sintético**. Confirma las casillas de consumo y carga e ingresa las contraseñas localmente cuando se soliciten. Este flujo crea embeddings OCI reales e inserta los nueve fragmentos sintéticos en tu schema individual.

Registra en el cuaderno el número de fragmentos, el `corpus_id` y un ejemplo de sección, versión y hash. No copies contraseñas ni rutas privadas.

### Actividad 3: ejecutar y comprobar una respuesta respaldada

Selecciona T01 o T03, marca **Preguntar usando OCI** y confirma el consumo aprobado. El flujo real:

1. Crea el embedding OCI de la consulta.
2. Busca en ADB solo dentro de la versión autorizada.
3. Selecciona evidencia que respalda la afirmación.
4. Usa OCI chat solo cuando hay evidencia suficiente.
5. Publica respuesta, citas, extractos y traza de servicios.

En **Referencia del ejercicio vs. respuesta obtenida**, compara el estado y los hechos requeridos. Después sigue cada afirmación hasta su cita, extracto, versión, sección y líneas.

### Actividad 4: comparar versiones sin contaminarlas

Ejecuta T06 y T08. Para T06, revisa el cambio de endpoint, campo y estados al migrar a v2. Para T08, registra las dos recuperaciones por separado: una evidencia v1 y una evidencia v2. No uses un extracto de una versión para completar la otra.

### Actividad 5: demostrar un límite correcto

Completa los tres casos del cuaderno:

- T05 no define versión: el resultado correcto es `needs_clarification`, sin asumir v2.
- T10 pregunta por SLA de disponibilidad: el resultado correcto es `insufficient_evidence`; no se inventa una garantía.
- T12 pide conteos operacionales: el resultado correcto es `structured_data_required`; un contrato no contiene transacciones reales.

T05 y T12 son decisiones de control de la aplicación y no requieren generación. T10 comprueba que la recuperación no se convierta en una respuesta sin respaldo.

### Actividad 6: decidir entre RAG y SQL

Clasifica las preguntas del cuaderno. Usa RAG para explicar el contrato con evidencia; usa SQL controlado para hechos operacionales; separa ambos en una necesidad combinada. No se ejecuta SQL libre ni se inventan resultados.

### Actividad 7: entregar evidencia, no solo una respuesta

En **Mi historial de ejecuciones**, verifica que ves solo tus reportes. Entrega el cuaderno con una respuesta positiva, una comparación, un límite correcto y una decisión RAG/SQL. Una respuesta correcta no basta si no puedes mostrar el extracto contractual que la respalda.

## Si algo falla

Consulta [Resolución de problemas para participantes](troubleshooting.md). No envíes por chat contraseñas, archivos wallet, perfiles OCI, contenido de sesiones ni mensajes de error completos.
