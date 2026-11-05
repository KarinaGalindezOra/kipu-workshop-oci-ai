# Workshop de IA OCI de Khipu

Este repositorio contiene los materiales públicos y reproducibles de los laboratorios de inteligencia artificial de Khipu sobre Oracle Cloud Infrastructure (OCI).

## ¿Participarás en Workshop 2?

**Empieza aquí:** [Guía única paso a paso del participante](labs/lab02_contract_rag/docs/participant_step_by_step.md).

La guía comienza con la descarga o clonación del repositorio, continúa con la instalación para Windows, macOS o Linux y termina con la ejecución del dashboard local, las actividades OCI reales y la revisión de evidencia.

Antes de la sesión, recibirás por un canal privado tu asignación individual de OCI y Autonomous Database (ADB). No necesitas crear recursos OCI, configurar IAM ni usar credenciales de administración.

## Laboratorios

1. [Workshop 1: memoria de decisiones y aislamiento de contexto](docs/participant-guides/01-agent-memory.md)
2. [Workshop 2: RAG contractual con evidencia verificable](labs/lab02_contract_rag/README.md)
3. [Workshop 3: análisis de cambios de API](docs/participant-guides/03-api-change-analysis.md)

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
python -m pip install -e ".[dev,lab01,lab01-gateway,lab02,lab03,ui]"
python -m pytest
```

No subas wallets, contraseñas, perfiles OCI, archivos de sesión ni reportes privados a Git.
