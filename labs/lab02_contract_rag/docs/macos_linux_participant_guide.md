# Guía de participante para macOS y Linux

Esta es la ruta soportada para participantes en macOS y Linux. Usa los mismos comandos Python en ambos sistemas. Los launchers PowerShell de Windows se mantienen solo como compatibilidad administrativa y de facilitación.

## Antes del workshop

- Instala Python 3.11 y Git.
- Recibe por el canal aprobado tu identidad OCI, contraseña del schema de base de datos, directorio de wallet y archivo privado de sesión.
- Guarda wallet y archivo de sesión fuera del repositorio. El archivo de sesión se copia desde `config/participant-session.env.example` y nunca contiene contraseña, token, clave privada ni secreto.
- Cuando sea posible, limita el acceso de lectura del wallet al participante asignado.

## Instala localmente

Desde el checkout del repositorio:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev,lab02,ui]"
```

Usa `python3` solo si ya corresponde a Python 3.11. No pongas el archivo de sesión privado dentro del repositorio ni lo subas a Git.

## Valida tu asignación privada

El comando solicita localmente las contraseñas del schema y wallet. No invoca Generative AI ni carga datos.

```bash
python labs/lab02_contract_rag/scripts/validate_environment.py \
  --session-file /private/path/lab02-p001.env \
  --check-db
```

El resultado esperado es JSON seguro con `status` igual a `passed` y `database_session` igual a `participant_schema`.

## Prepara el corpus sintético aprobado

Ejecuta este paso solo cuando la facilitación apruebe embeddings pagados y carga sintética. Solicita contraseñas locales, genera embeddings documentales OCI reales y escribe únicamente en tu schema asignado.

```bash
python labs/lab02_contract_rag/scripts/ingest_oci.py \
  --session-file /private/path/lab02-p001.env \
  --confirm-live-inference \
  --confirm-synthetic-load
```

El resultado esperado incluye `STATUS ingested` y `OCI_EXECUTED True`.

## Congela la calibración de desarrollo

Ejecuta este paso después de la carga aprobada. El primer comando usa query embeddings pagados; el segundo es local y congela la calibración. Reutiliza mediciones privadas existentes para evitar una nueva recolección con costo.

```bash
python labs/lab02_contract_rag/scripts/collect_calibration.py \
  --session-file /private/path/lab02-p001.env \
  --confirm-live-inference

python labs/lab02_contract_rag/scripts/calibrate.py \
  --measurements /private/path/development-measurements.json \
  --output /private/path/calibration.json
```

Puede existir solapamiento de distancias en este corpus pequeño. No convierte un candidato en evidencia válida: siguen siendo obligatorias la selección y validación de afirmación–evidencia.

## Usa el dashboard local

```bash
python labs/lab02_contract_rag/scripts/run_dashboard.py \
  --session-file /private/path/lab02-p001.env
```

Abre `http://127.0.0.1:8502` en tu navegador local. El dashboard permanece local en el equipo participante. Cada solicitud pagada requiere confirmación nueva y contraseña local. No expongas el puerto por un proxy público.

## Ejecuta una pregunta aprobada desde línea de comandos

```bash
python labs/lab02_contract_rag/scripts/run_live_validation.py \
  --session-file /private/path/lab02-p001.env \
  --question "In v2, what method and endpoint update settlement status?" \
  --contract-version v2 \
  --confirm-live-inference
```

El comando escribe el reporte de evidencia privado bajo `LAB02_REPORT_ROOT`. Una prueba local, un reporte de otra persona o una llamada OCI fallida no acreditan la actividad.

## Resolución de problemas

- `HTTP_401` en query embeddings: reautentica el perfil OCI asignado, valídalo con un comando OCI aprobado de solo lectura y solicita autorización de reintento.
- `ORA-01017`: vuelve a ingresar la contraseña asignada del schema; no cambies schema ni tabla.
- El dashboard no inicia: confirma Python 3.11, `.venv` activado, ruta de sesión privada y disponibilidad del puerto 8502.
- Error de wallet: valida privadamente directorio y alias de servicio; no pegues archivos de wallet ni cuerpos de error en el chat o reportes.

Realiza el preflight en al menos un Mac y un Linux reales antes del workshop. Las pruebas unitarias en otro sistema operativo no prueban wallet, perfil OCI, navegador local ni compatibilidad de red.
