# Guía del participante Workshop Khipu OCI AI

## Workshop 3: nuevo recorrido

Para el agente de pagos con memoria, RAG y herramientas, sigue la [guía única del participante](../../labs/lab03_payment_agent/docs/participant_step_by_step.md). El laboratorio de cambio de API de esta página se conserva como material complementario.

## Propósito

Estas guías conducen los tres laboratorios del Workshop Khipu OCI AI. Cada laboratorio tiene un objetivo concreto, pasos verificables, criterios de evidencia y una alternativa segura cuando un servicio compartido no está disponible.

La secuencia conserva el estilo progresivo del workshop de referencia: primero se prepara el entorno, luego se construye un resultado pequeño, se valida lo esperado y finalmente se revisa un error o riesgo realista.

## Agenda

| Fecha | Laboratorio | Resultado que debe obtener el equipo |
| --- | --- | --- |
| 20 de octubre | Economía de tokens y memoria de decisiones | Memoria procedural recuperada solo dentro del contexto del equipo y comparación real de tokens OCI. |
| 21 de octubre | RAG de contratos v1 y v2 con evidencia | Respuesta basada en la versión correcta del contrato y acompañada de evidencia. |
| Material complementario | Cambio seguro de API | Análisis de impacto, parche acotado y pruebas de regresión para una API sintética. |

## Estado de preparación del Trial técnico

| Laboratorio | Estado técnico comprobado | Regla para el workshop |
| --- | --- | --- |
| Lab 1 | El algoritmo local, el SDK directo, el ejercicio de memoria real y la comparación de inferencia están cubiertos por pruebas. La ejecución final requiere el prework de owner, usuarios de aplicación, grants de runtime y un modelo de chat aprobado por trial de equipo. | Cada participante recupera primero una decisión real desde ADB sin inferencia y luego realiza dos llamadas OCI Generative AI con datos sintéticos; el dashboard separa evidencia real de la simulación visual local. |
| Lab 2 | El piloto técnico validó embeddings, almacenamiento vectorial, recuperación filtrada por versión y respuesta con evidencia. El runner repetible fue cubierto con pruebas locales. | El facilitador ejecuta una vez el runner en el Trial antes de la sesión; cada equipo usa un esquema preparado o la alternativa local. |
| Laboratorio complementario de API | Análisis, parche y pruebas FastAPI verificados localmente. | No requiere ADB ni modificación de recursos OCI. La asistencia de OCI Generative AI es opcional. |

## Antes de comenzar

### Reglas de datos y seguridad

- Usa únicamente los archivos y mensajes sintéticos incluidos en el repositorio.
- No pegues contraseñas, wallets, tokens, OCID, código de Khipu, contratos reales, ni datos de clientes en una terminal, un prompt de IA o un repositorio.
- No ejecutes `terraform apply`, `terraform destroy`, ni comandos de administración ADB durante los laboratorios sin indicación explícita del facilitador.
- Un resultado de IA es un borrador. La evidencia, la revisión humana y las pruebas son la aceptación del ejercicio.

### Preparación local en Windows

Qué hacer:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev,lab01,lab03]"
python -m pytest
```

Qué deberías ver:

- La instalación termina sin exponer secretos.
- La suite completa informa pruebas correctas.

Error común:

- Ejecutar los comandos desde una carpeta distinta de la raíz del repositorio. Verifica que puedas ver `pyproject.toml` antes de crear el entorno virtual.

### Confirmar el Trial antes del segmento en vivo

El facilitador confirma que la ADB está disponible y que los modelos de chat y embeddings aprobados existen en la región seleccionada. Este control se realiza en Cloud Shell o con la consola OCI; los participantes no necesitan conocer identificadores sensibles.

Ejemplo de verificación del estado de ADB desde el directorio Terraform del Trial:

```bash
ADB_ID=$(terraform output -raw autonomous_database_id)
oci db autonomous-database get \
  --autonomous-database-id "$ADB_ID" \
  --query 'data.lifecycle-state' \
  --raw-output
```

Qué deberías ver:

```text
AVAILABLE
```

No continúes el segmento en vivo si el estado no es `AVAILABLE`. El facilitador decide si inicia ADB o si se usa la alternativa local.

## Cómo leer cada guía

Cada paso presenta cuatro elementos:

1. **Para qué se usa:** el propósito técnico del paso.
2. **Qué hacer:** la acción exacta y acotada.
3. **Qué deberías ver:** la señal esperada antes de avanzar.
4. **Error común:** una condición que se debe corregir o escalar al facilitador.

Al finalizar cada laboratorio, el equipo conserva solo los archivos de evidencia generados bajo `artifacts/`. Estos archivos están ignorados por Git y no deben incluir secretos.
