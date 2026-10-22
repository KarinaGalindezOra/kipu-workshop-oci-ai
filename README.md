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
- `platform/bootstrap/`: SQL de owner-only para crear el esquema, usuario temporal y permisos mínimos.
- `terraform/`: módulos y perfil de ejemplo para aprovisionar un entorno de workshop.
- `docs/participant-guides/`: guía de participante.
- `docs/facilitator-guides/`: prework, guía de facilitación y roster de ejemplo.

## Requisitos

- Windows PowerShell.
- Python 3.11.
- OCI CLI autenticado con una identidad individual del participante.
- SQLcl y Java para el prework del facilitador.
- Un Autonomous Database ya aprobado para el workshop, con wallet privado por participante.
- Un modelo de chat on-demand aprobado en OCI Generative AI.

No se requiere Docker ni Docker Desktop.

## Inicio rápido del participante

El participante no crea recursos OCI ni usa `ADMIN`. Debe recibir del facilitador, por un canal privado y fuera de GitHub:

- Un usuario temporal de aplicación de base de datos.
- Un wallet privado y su contraseña.
- Un archivo de sesión privado basado en `labs/lab01_agent_memory/config/participant-session.ps1.example`.
- Confirmación de acceso al modelo on-demand aprobado.

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

Continúe con la guía de participante: `docs/participant-guides/01-decision-memory.md`.

## Pruebas locales

```powershell
python -m pytest labs/lab01_agent_memory/tests -q
python -m ruff check labs/lab01_agent_memory/ui/app.py
```

Las pruebas de integración OCI están protegidas y no se ejecutan por defecto.

## Seguridad

No publique ni haga commit de wallets, contraseñas, sesiones OCI, tokens, OCIDs reales, archivos `terraform.tfvars`, estados Terraform ni evidencia generada por participantes. Revise `.gitignore` antes de cada commit.

## Uso de Terraform

El perfil `terraform/environments/trial-team/terraform.tfvars.example` contiene solo marcadores. Copie ese archivo a `terraform.tfvars` fuera del control de versiones, complete valores autorizados y revise el plan antes de aplicar. Consulte `docs/facilitator-guides/01-decision-memory-prework.md`.

## Licencia

Este material se distribuye para uso educativo del workshop. Confirme las políticas aplicables de Oracle, OCI y del tenant antes de utilizarlo en un entorno de cliente.
