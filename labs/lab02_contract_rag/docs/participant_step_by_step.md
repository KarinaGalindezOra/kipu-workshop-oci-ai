# Guía del participante — Workshop 2

Esta es la única guía que debes seguir durante el workshop. Trabajarás solamente con contratos y preguntas sintéticas. No ingreses datos de clientes, información personal, tokens ni credenciales en el dashboard, la terminal o el chat.

El workshop dura 180 minutos. Sigue los pasos en orden y conserva el dashboard abierto durante tu actividad.

## Antes de comenzar

Debes recibir por el canal privado aprobado:

- Una identidad OCI individual.
- Tu usuario o schema de ADB y las contraseñas que se solicitan localmente.
- Tu wallet privado.
- Tu archivo privado de sesión.
- La confirmación de que puedes usar el modelo OCI autorizado.

No crees usuarios, tablas, políticas IAM ni recursos OCI. No copies esos archivos privados dentro del repositorio ni los subas a Git.

## Paso 0: descarga el repositorio

Elige una de estas alternativas.

### Alternativa A: Git

Si tienes Git instalado, abre una terminal y ejecuta:

```bash
git clone https://github.com/KarinaGalindezOra/kipu-workshop-oci-ai.git
cd kipu-workshop-oci-ai
```

### Alternativa B: archivo ZIP

1. Abre la [página principal del repositorio](https://github.com/KarinaGalindezOra/kipu-workshop-oci-ai).
2. Selecciona **Code** y luego **Download ZIP**.
3. Descomprime el archivo descargado.
4. Abre una terminal dentro de la carpeta descomprimida `kipu-workshop-oci-ai-main`.

En los pasos siguientes, esa carpeta será la **raíz del repositorio**.

## Paso 1: verifica Python 3.11

### Windows

```powershell
py -3.11 --version
```

### macOS o Linux

```bash
python3.11 --version
```

Si no ves una versión 3.11, detente y solicita ayuda a la facilitación antes de continuar.

## Paso 2: crea el entorno e instala el proyecto

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,lab02,ui]"
```

### macOS o Linux

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,lab02,ui]"
```

Si usas macOS o Linux, consulta además la [guía macOS y Linux](macos_linux_participant_guide.md) para cargar tu sesión privada y resolver errores propios de esos sistemas.

## Paso 3: valida tu asignación privada

Carga el archivo de sesión entregado por la facilitación. El comando solicita las contraseñas localmente y no invoca OCI Generative AI.

### Windows PowerShell

La facilitación te enviará un bloque privado ya preparado para tu identidad. Pégalo sin modificarlo en una terminal dedicada. La ruta del archivo no es igual para todas las personas y no aparece en este repositorio. El bloque tendrá esta forma:

```powershell
. '<private-participant-session.ps1>'
python labs/lab02_contract_rag/scripts/validate_environment.py --check-db
```

No escribas literalmente los caracteres `<` y `>`: son una explicación visual, no parte del comando. No sustituyas la ruta por un wallet ni por la sesión de otra persona.

### macOS o Linux

La facilitación te enviará la ruta de tu archivo dotenv privado. Pega el bloque recibido; su forma será:

```bash
python labs/lab02_contract_rag/scripts/validate_environment.py \
  --session-file /private/path/lab02-participant.env \
  --check-db
```

El resultado esperado muestra `status` igual a `passed` y `database_session` igual a `participant_schema`. Si falla, detente y avisa a la facilitación. No cambies el schema ni intentes otras credenciales.

## Paso 4: abre el dashboard

### Windows PowerShell

```powershell
python labs/lab02_contract_rag/scripts/run_dashboard.py --port 8502
```

### macOS o Linux

```bash
python labs/lab02_contract_rag/scripts/run_dashboard.py \
  --session-file /private/path/lab02-participant.env \
  --port 8502
```

Abre `http://127.0.0.1:8502` en tu navegador. Verás **Ejecutar e inspeccionar** y **Mi historial de ejecuciones**. El dashboard es local: no lo expongas mediante un proxy público.

## Paso 5: conoce los contratos y prepara tu corpus

Lee `data/contract_v1.md` y `data/contract_v2.md`. Identifica endpoint, campos, estados e idempotencia de cada versión.

Cuando comience esta actividad, selecciona **Preparar mi corpus sintético** en el dashboard. Confirma las casillas de consumo y carga, e ingresa las contraseñas localmente si se solicitan. El flujo crea embeddings OCI reales e inserta los nueve fragmentos sintéticos en tu schema individual.

## Paso 6: ejecuta preguntas OCI reales

Selecciona una pregunta predefinida, marca **Preguntar usando OCI** y confirma el consumo aprobado. Comienza por una pregunta con versión explícita, como T01 o T03.

El flujo real es:

1. OCI crea el embedding de la pregunta.
2. ADB busca fragmentos dentro de la versión autorizada.
3. La aplicación selecciona evidencia que respalda la respuesta.
4. OCI chat genera únicamente afirmaciones respaldadas.
5. El dashboard muestra respuesta, citas, extractos y traza de servicios.

## Paso 7: revisa evidencia, no solo la respuesta

En **Referencia del ejercicio vs. respuesta obtenida**, comprueba que el estado y los hechos requeridos coincidan. Luego revisa:

- **Ejecución de servicios:** qué operaciones OCI/ADB ocurrieron y cuánto tardaron.
- **Afirmaciones y evidencia verificable:** cita, extracto, versión, sección y líneas que sustentan la respuesta.
- **Candidatos recuperados y evidencia seleccionada:** una distancia coseno menor expresa proximidad, pero no prueba por sí sola que un fragmento sea evidencia suficiente.

## Paso 8: prueba los límites correctos

Ejecuta una pregunta sin versión: el resultado correcto es `needs_clarification`, sin llamada al modelo.

Ejecuta una pregunta sobre SLA de disponibilidad: el resultado correcto es `insufficient_evidence`; el contrato no debe convertirse en una garantía inventada.

Ejecuta una pregunta de conteos operacionales: el resultado correcto es `structured_data_required`; los contratos no contienen transacciones reales.

## Paso 9: entrega tu evidencia

Abre **Mi historial de ejecuciones**. Verifica que los reportes son tuyos y contienen respuesta observada, citas y telemetría segura. Completa la actividad o rúbrica que te solicite la facilitación.

Una respuesta correcta no basta si no puedes mostrar qué extracto contractual la respalda. Una cita válida tampoco reemplaza la revisión humana de relevancia y completitud.

## Si algo falla

Consulta [Resolución de problemas para participantes](troubleshooting.md). No envíes por chat contraseñas, archivos wallet, perfiles OCI, contenido de sesiones ni mensajes de error completos.
