# Arquitectura del Workshop 1

## Propósito

El laboratorio demuestra cómo una aplicación o un agente puede utilizar memoria procedural gobernada antes de llamar a un modelo generativo. La memoria no reemplaza al modelo ni ejecuta acciones; selecciona contexto relevante para la pregunta actual.

```text
Pregunta de ingeniería
    -> recuperación por alcance en Oracle AI Agent Memory sobre Autonomous Database
    -> armado de contexto compacto
    -> OCI Generative AI Inference
    -> respuesta validada
```

## Componentes que utiliza el participante

| Componente | Responsabilidad | Límite de seguridad |
|---|---|---|
| Identidad OCI individual | Autentica las dos solicitudes de OCI Generative AI. | Cada participante usa una sesión privada; nunca una sesión compartida. |
| Usuario temporal de ADB | Ejecuta operaciones de runtime contra el memory store. | No es `ADMIN` ni propietario del esquema. |
| Oracle AI Agent Memory SDK | Persiste, recupera y busca procedimientos sintéticos. | Usa `SchemaPolicy.REQUIRE_EXISTING`; no crea ni actualiza infraestructura. |
| Autonomous Database | Aloja el esquema owner y el memory store precreado. | El owner y los grants se preparan antes del workshop. |
| OCI Generative AI Inference | Recibe los dos prompts comparables y reporta telemetría de uso. | Se utiliza un modelo on-demand aprobado y un límite de salida fijo. |
| Streamlit | Visualiza los JSON de evidencia local. | No guarda credenciales ni ejecuta llamadas OCI. |

## Topología del workshop

El workshop se ejecuta en un tenant trial centralizado. La infraestructura se prepara una vez y los participantes ejecutan el recorrido individualmente. Para una cohorte de hasta diez personas, se asigna un `TeamCode` único por participante, por ejemplo `T01/P01` hasta `T10/P01`. El término `TeamCode` conserva el modelo de scopes del SDK; no exige que dos personas compartan terminal o credenciales.

```text
Tenant trial del workshop
  -> Autonomous Database compartida
     -> Memory store precreado
        -> T01 / P01: identidad OCI, usuario temporal, wallet y evidencia propios
        -> T02 / P01: identidad OCI, usuario temporal, wallet y evidencia propios
        -> ...
        -> T10 / P01: identidad OCI, usuario temporal, wallet y evidencia propios
```

El repositorio se distribuye públicamente mediante el enlace de GitHub o un QR que apunte a ese enlace. Los wallets, contraseñas, usuarios temporales y archivos de sesión se entregan por un canal privado y nunca se suben al repositorio.

## Secuencia del laboratorio

1. El participante ejecuta preflight para validar Python, sesión OCI, wallet y acceso de runtime.
2. En el primer ejercicio ADB persiste y recupera `payment-idempotency` en su alcance individual.
3. En el segundo ejercicio ADB persiste y recupera `contract-compatibility` en ese mismo alcance.
4. En ambos ejercicios se comprueba que el alcance de control no devuelve contenido al participante.
5. En la corrida final, el mismo modelo procesa dos solicitudes: baseline con todas las decisiones y memoria con la regla recuperada.
6. El runner acepta la evidencia únicamente si ambas respuestas son completas, cumplen los criterios técnicos y la variante con memoria usa menos tokens de entrada.
7. Streamlit muestra memoria, aislamiento, tokens, latencia y calidad desde los JSON generados localmente.

## Qué se mide

La métrica principal es la reducción de `prompt_tokens` reportada por OCI. La comparación es válida porque conserva la pregunta, modelo, temperatura y límite de salida; cambia únicamente el contexto suministrado.

La reducción de tokens de entrada demuestra eficiencia de contexto en ese caso. No demuestra automáticamente menor costo total ni menor latencia end-to-end: memoria, almacenamiento, recuperación, red y operación también tienen costo y latencia.

## Qué no hace este laboratorio

- No permite que el modelo consulte el memory store de forma autónoma.
- No ejecuta herramientas, cambios de infraestructura ni acciones de negocio.
- No sustituye IAM, roles de base de datos, controles de red ni gobierno de datos de producción.
- No utiliza datos reales del cliente.

## Evolución hacia producción

Una arquitectura productiva puede incorporar filtros de metadata, recuperación vectorial o híbrida, evaluaciones de recuperación, observabilidad OCI, controles de presupuesto, guardrails y herramientas con permisos mínimos. El alcance de memoria debe derivarse de la identidad autenticada por el servicio; no debe ser un valor que el usuario final pueda escoger libremente.
