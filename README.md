# Workshop de IA OCI de Khipu

Este repositorio contiene los materiales públicos y reproducibles de los laboratorios de inteligencia artificial de Khipu sobre Oracle Cloud Infrastructure (OCI).

## ¿Participarás en Workshop 3?

**Empieza aquí:** [Guía única paso a paso del participante](labs/lab03_payment_agent/docs/participant_step_by_step.md).

Agente de investigación de pagos sintéticos con Oracle AI Agent Memory, RAG contractual versionado, Select AI Agent y herramientas PL/SQL. La guía en español explica desde la descarga e instalación hasta la confirmación humana del caso y la recuperación de una memoria desde una sesión nueva. Incluye resultados esperados, solución de problemas y comandos para Windows y macOS/Linux.

El recorrido dura **180 minutos**, después del prework. Recibirás tu asignación y wallet por un canal privado; no crees recursos OCI ni uses credenciales administrativas. El [cuaderno del participante](labs/lab03_payment_agent/docs/participant_workbook.md) permite registrar evidencia real.

El repositorio está preparado para la prueba end to end con un participante. Las validaciones locales y el piloto técnico no sustituyen esa prueba ni acreditan por sí solos aislamiento o concurrencia de 15 sesiones.

## ¿Participarás en Workshop 2?

**Empieza aquí:** [Guía única paso a paso del participante](labs/lab02_contract_rag/docs/participant_step_by_step.md).

Durante la sesión, usa además el [cuaderno de trabajo del participante](labs/lab02_contract_rag/docs/participant_workbook.md) y las [actividades](labs/lab02_contract_rag/docs/exercises.md). La preparación técnica se completa antes de la sesión; la guía contiene la ruta completa de 180 minutos.

La guía comienza con la descarga o clonación del repositorio, continúa con la instalación para Windows, macOS o Linux y termina con la ejecución del dashboard local, las actividades OCI reales y la revisión de evidencia.

Antes de la sesión, recibirás por un canal privado tu asignación individual de OCI y Autonomous Database (ADB). No necesitas crear recursos OCI, configurar IAM ni usar credenciales de administración.

## Laboratorios

1. [Workshop 1: memoria de decisiones y aislamiento de contexto](docs/participant-guides/01-decision-memory.md)
2. [Workshop 2: RAG contractual con evidencia verificable](labs/lab02_contract_rag/README.md)
3. [Workshop 3: agente de pagos con memoria, evidencia y herramientas](labs/lab03_payment_agent/README.md)

Material complementario: [laboratorio anterior de cambio de API](labs/lab03_api_change/README.md).

## Contenido público

```text
docs/                Guías y material público para participantes.
labs/                Código, contratos sintéticos, ejercicios y pruebas.
terraform/           Plantillas parametrizadas de infraestructura, sin valores reales.
```

Los procedimientos de preparación de tenant, credenciales, runbooks de facilitación, respuestas de evaluación y ensayos operativos se administran de forma privada y no forman parte del recorrido de participantes.

## Validación local para colaboradores

Si colaborarás en el código, utiliza Python 3.11.9:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,lab01,lab01-gateway,lab02,lab03,lab03-agent,ui]"
python -m pytest
```

No subas wallets, contraseñas, perfiles OCI, archivos de sesión ni reportes privados a Git.
