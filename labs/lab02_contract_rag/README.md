# Lab 2: RAG contractual OCI real con respuestas y evidencia visibles

Workshop 2 dura 180 minutos y está diseñado para 15 participantes. Cada persona usa un dashboard local, una identidad OCI individual y un schema de base de datos aislado. Se comparten un tenant y una Autonomous AI Database en Chicago; no se necesita un tenant ni una ADB por persona. Tenant, modelos, cuota y presupuesto deben aprobarse en el preflight. La capacidad para 15 personas simultáneas es una meta de ensayo, no una afirmación ya validada.

## Qué ve el participante

El dashboard Streamlit local ejecuta operaciones OCI reales. Muestra pregunta, respuesta obtenida, criterios de referencia, comprobaciones automáticas, limitaciones, afirmaciones, extractos fuente, versión/sección/líneas, ranking de candidatos, operaciones de servicio, latencia y uso del proveedor cuando está disponible. No contiene simulador, respuestas preparadas, carga de reportes ni selector de participante. Solo abre reportes reales del participante asignado.

El corpus aprobado contiene contratos sintéticos de desembolsos v1 y v2, con cuatro y cinco secciones respectivamente. Los datos sintéticos son intencionales; una ejecución simulada no está permitida.

## Instalación y lanzamiento

Usa Python 3.11.9 y un entorno virtual del proyecto. En Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev,lab02,ui]"
```

Los participantes macOS y Linux usan la [guía específica](docs/macos_linux_participant_guide.md), basada en los mismos runners Python.

La facilitación entrega por un canal privado una asignación individual: identidad OCI, schema de ADB, wallet, ruta de reportes y archivo de sesión privado. `LAB02_PARTICIPANT_ID` es obligatorio: `p001` corresponde a `KHIPU_L2_P001`, hasta `p015`. Nadie usa credenciales de administrador ni credenciales de otro participante.

En Windows, tras cargar la sesión privada en una terminal dedicada:

```powershell
. '<private-participant-session.ps1>'
python labs/lab02_contract_rag/scripts/validate_environment.py --check-db
python labs/lab02_contract_rag/scripts/run_dashboard.py --port 8502
```

En macOS/Linux se agrega `--session-file /private/path/lab02-p001.env` a los runners. Abre `http://127.0.0.1:8502`. El dashboard escucha únicamente en loopback; no lo expongas mediante un proxy público.

Abrir el dashboard no invoca OCI. Cada operación pagada requiere una confirmación explícita. La primera solicitud ADB de una sesión local solicita contraseñas privadas; solicitudes posteriores pueden reutilizar una sola conexión local ligada al participante mientras el dashboard permanezca abierto. Las contraseñas nunca se almacenan en reportes ni cachés.

## Secuencia real del workshop

1. Inspecciona los dos contratos y sus nueve fragmentos. El parsing local es preprocesamiento, no un reemplazo de recuperación.
2. Elige **Preparar mi corpus sintético** cuando la facilitación autorice embeddings y carga. OCI crea embeddings documentales y ADB inserta únicamente fragmentos faltantes en el schema individual.
3. La facilitación congela una calibración de desarrollo para corpus, modelo, región y dimensión aprobados. La tabla vectorial sigue siendo individual.
4. Elige una pregunta predefinida y usa **Preguntar usando OCI**. El SDK crea el embedding de consulta, ADB realiza búsqueda vectorial exacta con filtro de versión y OCI chat publica solo afirmaciones respaldadas.
5. Revisa respuesta obtenida, criterios de referencia y evidencia. Prueba comparación de versiones, falta de versión y ausencia de documentación.
6. Inspecciona el historial propio y completa la rúbrica individual.

El modelo recibe pregunta y evidencia recuperada, nunca la respuesta de referencia. Las afirmaciones del MVP se publican solo cuando tienen evidencia validada. Una cita inválida, una paráfrasis sin respaldo o un error del proveedor producen error; no se sustituye por una respuesta local.

## Casos de referencia y aceptación

`data/evaluation/workshop_questions.json` contiene 16 escenarios de ejecución real: diez positivos documentales, dos preguntas documentales sin respaldo y cuatro controles de aplicación. No todos invocan modelo: la traza distingue las decisiones de control de las operaciones OCI.

Las comprobaciones automáticas validan estado, citas, hashes, secciones requeridas, scope de versión y hechos obligatorios. Una aprobación no certifica por sí sola relevancia o completitud semántica: cada participante debe leer la respuesta y sus fuentes. Un sistema que se abstiene siempre falla los casos positivos.

El ensayo guiado de facilitación está en [p001_end_to_end_rehearsal.md](docs/p001_end_to_end_rehearsal.md). Usa T01, T03, T05 y T10 como puertas antes de incorporar al resto de participantes.

## Preparación administrativa

Revisa [aislamiento por participante](docs/participant_isolation.md), [operaciones del dashboard](docs/dashboard_operations.md), [capacidad para 15 personas](docs/capacity_15.md), [runbook del tenant](docs/tenant_setup_runbook.md) y [runbook de facilitación](docs/facilitator_runbook.md).

El dashboard nunca crea usuarios, políticas IAM, redes, bases de datos ni tablas. La preparación administrativa debe ocurrir antes de la sesión. El esquema v2 de tabla vectorial es incompatible con tablas históricas: crea una tabla/schema aprobados en lugar de sobrescribir ejercicios anteriores.

Para carga y calibración aprobadas desde línea de comandos:

```powershell
python labs/lab02_contract_rag/scripts/ingest_oci.py --confirm-live-inference --confirm-synthetic-load
python labs/lab02_contract_rag/scripts/collect_calibration.py --confirm-live-inference
python labs/lab02_contract_rag/scripts/calibrate.py --measurements <private_measurements_json> --output <private_calibration_json>
```

Nunca calibres con casos de aceptación. La calibración conserva recuperación de evidencia positiva; no convierte distancia vectorial en prueba de respaldo. La configuración aprobada utiliza `cohere.embed-v4.0` para embeddings y `xai.grok-4.7` para chat. xAI recibe solamente las preguntas y evidencia sintéticas autorizadas.

## Evidencia, seguridad y operación

Los reportes bajo `artifacts/lab02/<participant-id>/<run-id>/` contienen únicamente respuesta publicada validada, afirmaciones, fuentes sintéticas, resultados de servicio y telemetría segura. No muestran borradores crudos del proveedor, credenciales, perfiles OCI, cadenas de conexión ni vectores completos.

Los archivos locales no son atestaciones cloud firmadas. La aplicación valida `SESSION_USER` y `CURRENT_SCHEMA`, rechaza privilegios excesivos y mantiene namespaces individuales. La facilitación confirma la identidad OCI por separado.

Las pruebas de desarrollo no consumen OCI:

```powershell
python -m pytest labs/lab02_contract_rag/tests
python -m ruff check labs/lab02_contract_rag
```

Las pruebas unitarias y de interfaz usan doubles solo para validar software. No son un modo participante ni acreditan ejecución cloud.

## Checklist antes de la sesión

- [ ] Identidades individuales, schemas, wallets, red, modelos y presupuesto aprobados.
- [ ] Cada persona pasa el own-table check y se verifica denegación de lectura entre pares.
- [ ] Cada schema tiene nueve fragmentos sintéticos y calibración compatible congelada.
- [ ] El dashboard muestra respuesta real, criterios de referencia y evidencia resoluble.
- [ ] Cada participante completa los casos y la revisión humana asignados.
- [ ] La facilitación usa oleadas controladas si la concurrencia total no fue ensayada.
- [ ] No se cuentan resultados simulados, locales o no ejecutados como éxito OCI.

ADB, embeddings y chat consumen capacidad y presupuesto compartidos. Ante un error, registra el caso pendiente e investiga; no presentes una respuesta simulada como reemplazo. La eliminación de recursos requiere aprobación explícita del propietario.
