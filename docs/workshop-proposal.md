# Propuesta de Workshops: IA Empresarial en OCI

## Propósito

Tres workshops técnicos e independientes para expertos en IA, desarrolladores y arquitectos. Cada sesión puede tomarse por separado; juntas forman una ruta opcional: **contexto y memoria -> datos empresariales -> construcción de soluciones de IA en OCI**.

Todos los ejercicios usan datos sintéticos. No requieren código, documentos ni credenciales de producción del cliente.

## Workshop 1: Economía de Tokens y Memoria de Decisiones en OCI

### Objetivo

Diseñar y validar una memoria procedural para agentes que reutilice decisiones de ingeniería, evite repetir contexto innecesario en los prompts y mantenga separada la recuperación de información por participante y equipo.

### Qué harán los participantes

- Persistir procedimientos sintéticos mediante Oracle AI Agent Memory SDK sobre Autonomous Database.
- Recuperar solo la regla relevante desde un alcance individual o compartido.
- Ejecutar dos inferencias reales y comparar los tokens de entrada, salida, total y latencia reportados por OCI.
- Validar que un alcance de control no aparece en la recuperación del participante.
- Generar evidencia de persistencia, recuperación, aislamiento y reducción real de tokens de entrada.

### Resultado esperado

Cada participante termina con evidencia técnica de que la memoria procedural persiste en Autonomous Database, recupera la regla correcta dentro de su alcance y reduce los tokens de entrada reportados por OCI Generative AI sin perder los criterios de respuesta.

### Mensaje clave

Los agentes no deben repetir todo el contexto ni recordar todo indiscriminadamente. La memoria debe ser específica, recuperable y delimitada por identidad y propósito; su valor se comprueba con telemetría real del proveedor.

> El aislamiento demostrado es una frontera de recuperación. En producción debe complementarse con identidad autenticada, IAM, controles de base de datos y red.

## Workshop 2: Verifiable RAG with Autonomous AI Database and AI Vector Search

### Objective

Build and validate a version-aware synthetic contract RAG workflow in 180 minutes on prepared infrastructure. All 15 participants independently execute real OCI embedding, retrieval and generation through local dashboards, cites every contractual claim, and clarifies or abstains when support is missing.

### Observable learning outcomes

- Compare v1/v2 disbursement contracts and validate nine source-traceable chunks.
- Execute lexical and vector retrieval with mandatory corpus/API/version filters.
- Read the actual obtained answer beside expected criteria and inspect claim-level evidence.
- Debug ambiguity, weak evidence, conflicts and invalid citations.
- Justify documentary RAG versus controlled operational SQL.

### Acceptance and boundaries

Workshop 2 uses one shared Chicago tenancy and one ADB, with an individual OCI identity, database user/schema, session and evidence directory per participant.

Zero version contamination, all published claims supported and cited, mandatory negative cases correctly rejected, and positive cases answered. Use the [canonical lab](../labs/lab02_contract_rag/README.md) and human rubric. The MVP permits verbatim claims; general paraphrase entailment is outside automated validation. Object Storage, operational SQL execution and production deployment are later extensions. Provisioning and paid OCI execution require separate approval.

## Workshop 3: Construye Soluciones de IA en OCI

### Objetivo

Permitir que desarrolladores y arquitectos seleccionen y apliquen los servicios y patrones de OCI adecuados para construir soluciones de IA, desde la inferencia y los agentes hasta el despliegue seguro y la operación.

### Qué harán los participantes

- Identificar los patrones principales de IA en OCI: inferencia, RAG, agentes con herramientas y asistentes de desarrollo.
- Usar OCI Generative AI como asistente para analizar un cambio de API sintético y proponer un plan técnico.
- Generar y revisar un parche candidato y pruebas de regresión para el cambio propuesto.
- Entender cómo integrar recuperación, Function Calling o MCP según el caso de uso.
- Definir los controles mínimos para una solución operable: IAM, secretos, datos permitidos, revisión humana, pruebas, logging y métricas.

### Resultado esperado

Cada equipo termina con un flujo de ingeniería asistido por IA que genera una propuesta de cambio revisable y pruebas ejecutables, además de un criterio claro para decidir qué servicios OCI usar en una solución de IA.

### Mensaje clave

OCI permite acelerar la construcción de soluciones de IA, pero la salida del modelo es un borrador: la aceptación sigue dependiendo de evidencia, revisión humana y pruebas automatizadas.

## Resultado de la ruta completa

Al completar los tres workshops, los participantes podrán diseñar soluciones de IA empresarial en OCI que administren contexto de forma eficiente, usen datos empresariales con trazabilidad y apliquen prácticas de ingeniería y operación seguras.
