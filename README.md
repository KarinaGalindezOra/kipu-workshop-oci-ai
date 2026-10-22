# Kipu Workshop OCI AI

Laboratorio práctico del Workshop 1: economía de tokens, memoria de decisiones y aislamiento de contexto con Oracle AI Agent Memory, Autonomous Database y OCI Generative AI.

## Qué demuestra este laboratorio

Cada participante usa su propia identidad OCI, un usuario temporal de aplicación de Autonomous Database y un wallet privado. El recorrido ejecuta operaciones reales:

1. Persiste una regla procedural sintética en Oracle AI Agent Memory sobre Autonomous Database.
2. Recupera solo la regla relevante mediante búsqueda por palabra clave y valida el aislamiento de un alcance de control.
3. Ejecuta exactamente dos inferencias on-demand con OCI Generative AI: una baseline con todo el contexto y otra optimizada con la decisión recuperada.
4. Presenta en un dashboard local los tokens de entrada, salida y totales, la latencia y la validación de calidad.

El laboratorio usa únicamente datos sintéticos. Una reducción de tokens de entrada es evidencia de eficiencia de contexto; no es, por sí sola, una garantía de ahorro total de la solución.

## Contenido

- `labs/lab01_agent_memory/`: código Python, scripts PowerShell, UI Streamlit y pruebas del laboratorio.
- `docs/participant-guides/`: guía de participante.
- `docs/architecture.md`: arquitectura y límites del patrón de memoria del laboratorio.

## Requisitos

- Windows PowerShell.
- Python 3.11.
- OCI CLI autenticado con una identidad individual del participante.
- Un Autonomous Database ya aprobado para el workshop, con wallet privado por participante.
- Un modelo de chat on-demand aprobado en OCI Generative AI.

No se requiere Docker ni Docker Desktop.

## Inicio rápido del participante

El participante descarga o clona este repositorio público desde GitHub; el mismo enlace puede distribuirse mediante un QR. No crea recursos OCI ni usa `ADMIN`.

El workshop usa un tenant trial centralizado, una Autonomous Database y un memory store precreados. Cada participante realiza su propia ejecución y recibe por un canal privado, fuera de GitHub:

- Códigos de alcance únicos, por ejemplo `T01` y `P01`.
- Un usuario temporal individual de aplicación de base de datos.
- Un wallet privado y su contraseña.
- Un archivo de sesión privado basado en `labs/lab01_agent_memory/config/participant-session.ps1.example`.
- Confirmación de acceso al modelo on-demand aprobado con su identidad OCI individual.

Ejecute lo siguiente desde una copia local del repositorio:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[lab01,ui,dev]"

# The facilitator provides this private path. Do not save it in the repository.
$participantSession = "<absolute-path-to-private-participant-session.ps1>"

powershell -ExecutionPolicy Bypass -File .\labs\lab01_agent_memory\scripts\run_participant_live.ps1 `
  -TeamCode <team-code> `
  -ParticipantCode <participant-code> `
  -SessionFile $participantSession `
  -Preflight
```

Continúe con la guía de participante: `docs/participant-guides/01-decision-memory.md`. Antes de ejecutar, revise también `docs/architecture.md`.

## Pruebas locales

```powershell
python -m pytest labs/lab01_agent_memory/tests -q
python -m ruff check labs/lab01_agent_memory/ui/app.py
```

Las pruebas de integración OCI están protegidas y no se ejecutan por defecto.

## Seguridad

No publique ni haga commit de wallets, contraseñas, sesiones OCI, tokens, OCIDs reales, archivos `terraform.tfvars`, estados Terraform ni evidencia generada por participantes. Revise `.gitignore` antes de cada commit.

## Licencia

Este material se distribuye para uso educativo del workshop. Confirme las políticas aplicables de Oracle, OCI y del tenant antes de utilizarlo en un entorno de cliente.
