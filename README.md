# Workshop de IA OCI de Khipu

Este repositorio contiene materiales reproducibles para tres laboratorios de inteligencia artificial sobre Oracle Cloud Infrastructure (OCI):

1. Memoria de decisiones, aislamiento de contexto y comparación de tokens medida en OCI.
2. RAG sobre contratos de API versionados, con evidencia verificable.
3. Análisis de cambios de API, generación de parches y pruebas de regresión.

## Modelo operativo

- `trial-chicago` es el entorno técnico utilizado para los ensayos en `us-chicago-1`.
- `trial-team` es un perfil reutilizable para ejecutar un workshop después de que la facilitación cree y prepare el tenant trial correspondiente.
- `khipu` es un entorno objetivo parametrizado; no se despliega hasta que Khipu apruebe las decisiones de IAM, red, región y presupuesto.
- Cada persona ejecuta los laboratorios desde su propia estación de trabajo o desde una sesión local de Cloud Shell, con un usuario de aplicación temporal e individual cuando el laboratorio lo requiere.
- En los laboratorios solo se utilizan datos sintéticos.

> **Workshop 2:** un tenant y una Autonomous Database compartidos en Chicago; cada participante utiliza una identidad OCI, schema, sesión local y espacio de evidencias aislados. Consulta [aislamiento del participante](labs/lab02_contract_rag/docs/participant_isolation.md).

## Estructura del repositorio

```text
docs/                Documentos de arquitectura, preparación, seguridad y facilitación.
labs/                Material, código y pruebas de los laboratorios.
platform/bootstrap/  Scripts idempotentes de preparación posterior al aprovisionamiento.
terraform/           Infraestructura OCI parametrizada.
```

## Configuración local

Se requiere Python 3.11.9. En Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,lab01,lab01-gateway,lab02,lab03,ui]"
python -m pytest
```

Para macOS o Linux, revisa las guías específicas de cada laboratorio antes de ejecutar los comandos.

## Terraform

La infraestructura se configura mediante variables de ejemplo. No se incluyen credenciales, wallets, archivos de estado ni valores reales de OCI en el repositorio.

```powershell
cd terraform\environments\trial-chicago
Copy-Item terraform.tfvars.example terraform.tfvars
terraform init
terraform validate
terraform plan
```

Revisa el plan y solicita aprobación explícita antes de ejecutar `terraform apply`.

## Puertas de validación

- Ejecutar las pruebas locales antes de un ensayo o workshop.
- Validar la sesión de OCI, la región, la conectividad de Autonomous Database y los modelos autorizados antes de usar servicios facturables.
- Mantener wallets, contraseñas, perfiles de OCI y reportes privados fuera de Git.
- Ejecutar el preflight y el ensayo completo siguiendo el runbook del laboratorio correspondiente.

## Instrucciones para participantes

- [Workshop 1: guía de memoria de agente](docs/participant-guides/01-agent-memory.md)
- [Workshop 2: guía paso a paso del participante](labs/lab02_contract_rag/docs/participant_step_by_step.md)
- [Workshop 2: guía de evidencia RAG](docs/participant-guides/02-contract-rag-evidence.md)
- [Workshop 3: guía de cambios de API](docs/participant-guides/03-api-change-analysis.md)

Cada guía indica los prerrequisitos, el recorrido práctico, las validaciones esperadas y cómo informar un fallo sin exponer datos sensibles.
