# Paso a paso del participante — Workshop 2

Esta es la guía que seguirás durante el workshop. Trabajarás solamente con contratos y preguntas sintéticas. No ingreses datos de clientes, credenciales, tokens, archivos wallet ni información personal en el dashboard, terminal o chat.

## Antes de comenzar

Recibirás por el canal privado aprobado:

- Tu identidad OCI individual.
- Tu schema de ADB y las contraseñas que se solicitan localmente.
- Tu wallet privado.
- Tu archivo privado de sesión.
- La confirmación de que puedes usar el modelo OCI aprobado.

No crees usuarios, tablas, políticas IAM ni recursos OCI. Esa preparación corresponde a la facilitación.

## Paso 1: instala el proyecto

En Windows, desde la raíz del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,lab02,ui]"
```

En macOS o Linux, sigue la [guía macOS/Linux](macos_linux_participant_guide.md).

## Paso 2: valida tu asignación

En Windows, abre una terminal privada, carga el archivo de sesión entregado por la facilitación y ejecuta:

```powershell
. '<private-participant-session.ps1>'
python labs/lab02_contract_rag/scripts/validate_environment.py --check-db
```

El resultado esperado muestra `status: passed` y `database_session: participant_schema`. Si falla, detente y avisa a la facilitación; no cambies el schema ni adivines credenciales.

## Paso 3: abre el dashboard

```powershell
python labs/lab02_contract_rag/scripts/run_dashboard.py --port 8502
```

Abre `http://127.0.0.1:8502` en tu navegador. Verás tu espacio de trabajo, la pregunta seleccionada y dos pestañas: **Ejecutar e inspeccionar** y **Mi historial de ejecuciones**.

## Paso 4: conoce los contratos y prepara el corpus

Lee los contratos `data/contract_v1.md` y `data/contract_v2.md`. Identifica endpoint, campos, estados e idempotencia de cada versión.

Cuando la facilitación lo indique, selecciona **Preparar mi corpus sintético**. Confirma las casillas de consumo y carga, luego ingresa localmente las contraseñas solicitadas. El dashboard crea embeddings OCI reales e inserta los nueve fragmentos sintéticos en tu schema.

## Paso 5: ejecuta una pregunta OCI real

Selecciona una pregunta predefinida, marca **Preguntar usando OCI**, confirma el consumo aprobado e ingresa las contraseñas locales si se solicitan. Empieza por una pregunta con versión explícita, por ejemplo T01 o T03.

El flujo real es:

1. OCI crea el embedding de la pregunta.
2. ADB busca fragmentos dentro de la versión autorizada.
3. La aplicación selecciona evidencia que respalda la respuesta.
4. OCI chat genera únicamente afirmaciones respaldadas.
5. El dashboard muestra la respuesta, citas, extractos y traza de servicios.

## Paso 6: revisa evidencia, no solo el resultado

En **Referencia del ejercicio vs. respuesta obtenida**, comprueba que estado y hechos requeridos coinciden. Luego revisa:

- **Ejecución de servicios**: qué operaciones OCI/ADB ocurrieron y cuánto tardaron.
- **Afirmaciones y evidencia verificable**: cita, extracto, versión, sección y líneas que respaldan cada afirmación.
- **Candidatos recuperados y evidencia seleccionada**: una distancia coseno menor expresa proximidad, pero no prueba que un fragmento sea evidencia suficiente.

## Paso 7: prueba los límites correctos

Ejecuta una pregunta sin versión: el resultado esperado es `needs_clarification`, sin llamar al modelo.

Ejecuta una pregunta sobre SLA de disponibilidad: el resultado esperado es `insufficient_evidence`; el contrato no debe convertirse en una garantía inventada.

Ejecuta una pregunta de conteos operacionales: el resultado esperado es `structured_data_required`; los contratos no contienen transacciones reales.

## Paso 8: entrega tu evidencia

Actualiza **Mi historial de ejecuciones**. Revisa que los reportes son tuyos y contienen respuesta observada, citas y telemetría segura. Completa la rúbrica solicitada por la facilitación.

Una respuesta correcta no es suficiente si no puedes mostrar qué extracto contractual la respalda. Una cita válida tampoco reemplaza la revisión humana de relevancia y completitud.
