# Kipu Workshop OCI AI

Laboratorio práctico del Workshop 1: economía de tokens, memoria de decisiones y aislamiento de contexto con Oracle AI Agent Memory, Autonomous Database y OCI Generative AI.

## Qué demuestra este laboratorio

Cada participante usa su propia identidad OCI, un usuario temporal de aplicación de Autonomous Database y un wallet privado. El recorrido ejecuta operaciones reales:

1. Persiste una regla procedural sintética en Oracle AI Agent Memory sobre Autonomous Database.
2. Recupera solo la regla relevante mediante búsqueda por palabra clave y valida el aislamiento de un alcance de control.
3. Ejecuta exactamente dos inferencias bajo demanda con OCI Generative AI: una línea base con todo el contexto y otra optimizada con la decisión recuperada.
4. Presenta en un panel local los tokens de entrada, salida y totales, la latencia y la validación de calidad.

El laboratorio usa únicamente datos sintéticos. Una reducción de tokens de entrada es evidencia de eficiencia de contexto; no es, por sí sola, una garantía de ahorro total de la solución.

## Contenido

- `labs/lab01_agent_memory/`: código Python, scripts de PowerShell, interfaz de Streamlit y pruebas del laboratorio.
- `docs/participant-guides/`: guías de participante.
- `docs/architecture.md`: arquitectura y límites del patrón de memoria del laboratorio.

## Requisitos

- Windows PowerShell.
- Python 3.11.
- OCI CLI autenticado con la identidad individual del participante.
- Una Autonomous Database aprobada para el workshop, con un wallet privado por participante.
- Un modelo de chat bajo demanda aprobado en OCI Generative AI.

No se requiere Docker ni Docker Desktop.

## Inicio rápido del participante

El participante descarga o clona este repositorio público desde GitHub; el mismo enlace puede distribuirse mediante un QR. No crea recursos OCI ni usa `ADMIN`.

El workshop usa un tenant trial centralizado, una Autonomous Database y un almacén de memoria (`memory store`) precreados. Cada participante realiza su propia ejecución y recibe por un canal privado, fuera de GitHub:

- Códigos de alcance únicos, por ejemplo `T01` y `P01`.
- Un usuario temporal individual de aplicación de base de datos.
- Un wallet privado y su contraseña.
- Un archivo de sesión privado basado en `labs/lab01_agent_memory/config/participant-session.ps1.example`.
- Confirmación de acceso al modelo bajo demanda aprobado con su identidad OCI individual.

### Paso 0: clonar el repositorio público

Abre PowerShell y ejecuta este bloque una sola vez. Descarga código y documentación públicos; no
descarga wallets, sesiones, contraseñas ni evidencia de otro participante. El comando se detiene
si la ruta de destino ya existe para evitar sobrescribir archivos.

```powershell
$workshopDirectory = "C:\KhipuPrivate\participant-workshop"

if (Test-Path -LiteralPath $workshopDirectory) {
  throw "El directorio del workshop para participante ya existe. Detente antes de reemplazarlo."
}

git clone https://github.com/KarinaGalindezOra/kipu-workshop-oci-ai.git $workshopDirectory
Set-Location $workshopDirectory
git log -1 --oneline
```

### Paso A: preparar el computador local

Ejecuta este bloque desde una copia local del repositorio. Solo crea un entorno Python local e
instala dependencias; no requiere wallet, sesión OCI ni contraseñas, y no accede a OCI o ADB.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[lab01,ui,dev]"
```

### Paso A.1: validar el código local

Ejecuta las pruebas después de instalar las dependencias y antes de cargar cualquier elemento
privado. Estas pruebas no usan OCI, ADB, wallet ni contraseñas.

```powershell
python -m pytest labs/lab01_agent_memory/tests -q
python -m ruff check labs/lab01_agent_memory/ui/app.py
```

Las pruebas de integración con OCI están protegidas y no se ejecutan de forma predeterminada.

### Paso B: cargar la asignación privada y ejecutar preflight

Ejecuta este bloque solo después de recibir los elementos privados del facilitador. La participante
no crea usuarios, wallets ni contraseñas: recibe un usuario temporal de ADB, un wallet, la contraseña
del wallet y la contraseña del usuario de base de datos por el canal privado aprobado.

```powershell

# La facilitadora asigna los tres valores por un canal privado. No los guardes en el repositorio.
# Ejemplo: T01/P01 se asocia con C:\KhipuPrivate\sessions\T01-P01-session.ps1.
# No uses los valores del ejemplo salvo que la facilitadora te los haya asignado.
$participantSession = "C:\KhipuPrivate\sessions\T01-P01-session.ps1"
$teamCode = "T01"
$participantCode = "P01"

powershell -ExecutionPolicy Bypass -File .\labs\lab01_agent_memory\scripts\run_participant_live.ps1 `
  -TeamCode $teamCode `
  -ParticipantCode $participantCode `
  -SessionFile $participantSession `
  -Preflight
```

Durante la validación previa (`preflight`), el programa solicita las contraseñas localmente sin
mostrarlas. Valida la identidad OCI, el wallet, la conectividad a ADB y el acceso al almacén de
memoria existente (`memory store`). También consulta el catálogo de modelos para comprobar que la
identidad tiene acceso efectivo al modelo configurado. No crea memorias ni realiza inferencias de
OCI Generative AI.

`TeamCode` y `ParticipantCode` son alcances lógicos de recuperación; la participante no los elige.
Para participantes individuales, la facilitadora asigna un par único por persona, por ejemplo
`T01/P01`, `T02/P01` y `T03/P01`. El nombre del archivo de sesión privado debe coincidir con el
par asignado. Las participantes reciben el repositorio mediante GitHub, pero reciben su archivo
de sesión, wallet, usuario de base de datos y contraseñas únicamente por el canal privado aprobado.

Continúa con la guía de participante: `docs/participant-guides/01-decision-memory.md`. Antes de ejecutar, revisa también `docs/architecture.md`.

## Seguridad

No publiques ni hagas commit de wallets, contraseñas, sesiones OCI, tokens, OCIDs reales, archivos `terraform.tfvars`, estados de Terraform ni evidencia generada por participantes. Revisa `.gitignore` antes de cada commit.

## Licencia

Este material se distribuye para uso educativo del workshop. Confirma las políticas aplicables de Oracle, OCI y del tenant antes de utilizarlo en un entorno de cliente.
