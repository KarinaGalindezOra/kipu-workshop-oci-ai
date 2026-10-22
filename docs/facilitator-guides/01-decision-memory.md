# Guía de facilitación: Workshop 1 — economía de tokens y memoria de decisiones

## Resultado esperado

Cada participante ejecuta Oracle AI Agent Memory SDK contra la ADB del trial de su equipo con un usuario temporal de aplicación. Persiste decisiones sintéticas, recupera el alcance asignado y ejecuta dos inferencias reales de OCI Generative AI para comparar telemetría de tokens y latencia. El dashboard visualiza evidencia segura; no reemplaza la ejecución.

## Topología aprobada

La unidad de despliegue es **un trial por equipo**. No se necesita un trial nuevo para la facilitadora: el trial actual se reserva para ensayo técnico. Cada equipo nuevo usa el mismo artefacto Terraform parametrizado.

```mermaid
flowchart LR
  P1[Participant P01 workstation or Cloud Shell] -->|mTLS + app user| ADB
  P2[Participant P02 workstation or Cloud Shell] -->|mTLS + app user| ADB
  ADB[Autonomous Database] --> O[Team memory owner schema]
  O --> M[Oracle AI Agent Memory store]
  P1 --> S1[t01:p01 scope]
  P2 --> S2[t01:p02 scope]
  P1 --> SS[t01:shared scope]
  P2 --> SS
  C[t01:control scope] --> M
  M --> E[Safe JSON evidence]
  E --> UI[Khipu AI Memory Studio]
```

La ADB, el memory store y sus objetos administrados se crean una vez. Cada participante trabaja desde su máquina con un usuario de aplicación distinto. El alcance es una frontera real de recuperación, pero no sustituye una política de seguridad por fila.

## Roles

| Rol | Responsabilidad | No debe hacer |
| --- | --- | --- |
| Facilitador de plataforma | Crear trial, revisar Terraform, descargar wallet y ejecutar bootstrap único | Compartir `ADMIN`, wallet maestro o contraseñas |
| Memory owner | Crear store una vez y conceder acceso de runtime | Ejecutar el ejercicio participante como owner |
| Participante | Ejecutar SDK, modificar datos sintéticos y generar evidencia | Crear objetos de Agent Memory, ejecutar Terraform o usar credenciales ajenas |
| Observador técnico | Revisar dashboard y controles | Ejecutar con usuario de otra persona |

## Prework por trial de equipo

El procedimiento completo y la lista de salida se encuentran en el [prework operativo](01-decision-memory-prework.md). Usa también el [roster privado de participantes](lab01-participant-roster.csv.example) para controlar preparación sin registrar secretos.

### 1. Crear el trial y ejecutar preflight

La creación del trial se hace fuera de Terraform. Después usa [`terraform/environments/trial-team`](../../terraform/environments/trial-team/). El primer plan debe crear solo el compartment; ADB, Object Storage y políticas IAM empiezan deshabilitados.

Antes de habilitar ADB, confirma región, crédito, cuota, código de equipo, tags y plan exacto. La creación de ADB consume créditos y requiere aprobación explícita.

### 2. Crear ADB y manejar el wallet

Después del `apply` aprobado, descarga un wallet mTLS para el trial. No uses Terraform para descargar o guardar el wallet: su contenido quedaría en el estado. Conserva wallet y contraseñas en un canal privado aprobado y elimina la distribución al cierre.

### 3. Crear identidades de base de datos

Como administrador de ADB, ejecuta una vez:

```sql
@platform/bootstrap/02_create_agent_memory_owner.sql T01
@platform/bootstrap/03_create_agent_memory_application_user.sql T01 P01
@platform/bootstrap/03_create_agent_memory_application_user.sql T01 P02
```

Repite el segundo script por participante. Las contraseñas se solicitan ocultas y no se incluyen en el repositorio ni como argumentos.

### 4. Provisionar el paquete y crear el memory store una sola vez

Sigue la sección 4 del [prework operativo](01-decision-memory-prework.md): desde PowerShell, con las referencias de owner configuradas, ejecuta:

```powershell
.\.venv\Scripts\python.exe .\labs\lab01_agent_memory\scripts\bootstrap_team_memory.py --team-code T01
```

Escribe `BOOTSTRAP` solo tras verificar ADB, equipo y store. El script primero provisiona el paquete oficial `DBMS_AGENT_MEMORY_STORE` en el esquema propietario mediante la conexión mTLS; después crea o abre el store con `SchemaPolicy.CREATE_IF_NECESSARY` y siembra una regla sintética en `t01:control`.

Esta es una operación de plataforma que se ejecuta una única vez por trial de equipo y exclusivamente con el usuario propietario. Ningún participante ejecuta este paso ni usa una política de creación.

### 5. Conceder acceso de runtime

Conéctate como memory owner y ejecuta por cada usuario de aplicación:

```sql
@platform/bootstrap/04_grant_agent_memory_runtime_access.sql <application-user-1> <memory-store-id>
@platform/bootstrap/04_grant_agent_memory_runtime_access.sql <application-user-2> <memory-store-id>
```

El script concede DML únicamente sobre las tablas administradas del store, lectura del property graph, lectura de la tabla de registro `AGENT_MEMORY_STORES` y `EXECUTE` sobre el paquete público `DBMS_AGENT_MEMORY_STORE`. La lectura del registro permite que el SDK valide el store existente entre esquemas; no concede administración. Tampoco concede privilegios `CREATE`, acceso al paquete interno ni permisos de administración de ADB. Los participantes usan después `SchemaPolicy.REQUIRE_EXISTING`.

### 6. Reducir permisos y entregar sesiones individuales

Tras completar los grants de todos los participantes, sigue la sección 6 del prework para revocar los privilegios temporales de instalación del memory owner. Luego prepara una sesión OCI propia y un archivo de sesión `.ps1` privado por participante conforme a la sección 8 del prework.

Cada participante recibe de forma privada:

- Wallet/directorio mTLS y contraseña.
- Usuario de aplicación y contraseña temporal.
- Archivo de sesión con las referencias no secretas requeridas por el launcher.
- Código `TNN` y `PNN`.

No entregues un único usuario para el equipo. No incluyas wallets, contraseñas ni sesiones privadas en el ZIP de código, GitHub, Object Storage público ni el dashboard.

### 7. Ensayar y declarar go/no-go

Una persona de ensayo debe completar la guía de participante con un usuario de aplicación, nunca con `ADMIN` ni con el owner. Declara **go** solo si obtiene:

```text
LAB01_OCI_SDK_READY
SCHEMA_POLICY REQUIRE_EXISTING
PERSISTENCE_CONFIRMED True
ISOLATION_PASS True
TOKEN_QUALITY_PASS True
```

Antes de aceptar el ensayo, confirma también que el JSON contiene dos bloques de `usage` de OCI y que `memory_optimized.prompt_tokens` es menor que `baseline.prompt_tokens`. El ensayo de inferencia usa exactamente dos llamadas on-demand con datos sintéticos; ejecútalo con un usuario de aplicación no administrador y dentro del presupuesto aprobado.

## Guion de 180 minutos

| Minutos | Facilitador | Participantes | Evidencia |
| --- | --- | --- | --- |
| 0–20 | Explica el caso, seguridad y los dos diseños de contexto | Identifican la regla procedural relevante | Vista previa del dashboard |
| 20–40 | Explica el SDK y acompaña preflight | Validan sesión, wallet, ADB y Memory Store sin inferencia | `LAB01_PREFLIGHT_COMPLETE` |
| 40–65 | Facilita la primera regla sintética | Persisten, recuperan y aíslan `payment-idempotency` en ADB sin inferencia | JSON de memoria 1 |
| 65–80 | Facilita la segunda regla sintética | Persisten y recuperan `contract-compatibility`; contrastan ambos resultados | JSON de memoria 2 |
| 80–95 | Conecta memoria con arquitectura de agentes | Ubican recuperación, composición de contexto, inferencia y acción en el ciclo del agente | Explicación técnica acordada |
| 95–120 | Da soporte a la corrida final | Ejecutan exactamente dos llamadas OCI para baseline vs. memoria | JSON de tokens seguro |
| 120–155 | Abre dashboard y facilita lectura comparativa | Analizan tokens, latencia, calidad y sus límites | Cuatro hitos del dashboard |
| 155–180 | Cierra y atiende incidencias | Sintetizan aprendizajes | Lista de cierres por participante |

## Mensaje técnico obligatorio

1. `CREATE_IF_NECESSARY` corresponde al owner y se ejecuta una vez; no debe ejecutarse en paralelo. El participante solo usa `REQUIRE_EXISTING`.
2. Los participantes llaman realmente a `OracleAgentMemory.add_memory(..., memory_type="guideline")` y a `search(..., exact_user_match=True, record_types=["guideline"])` contra ADB. El tipo de registro hace explícito que el resultado recuperado es una regla procedural. Para mantener el comportamiento de `KEYWORD` reproducible, el bundle separa pregunta de negocio y término de recuperación; en Payments, `idempotency` debe devolver `payment-idempotency`.
3. Una búsqueda con `user_id` exacto limita la recuperación, pero no autoriza por sí sola a un cliente que pueda modificar el identificador. Producción requiere servicio autenticado, IAM, red y controles de base de datos.
4. Antes de la comparación final, cada participante ejecuta un ejercicio real de memoria sin inferencia. El launcher permite solo `payment-idempotency` o `contract-compatibility`, persiste y recupera la regla elegida desde ADB y guarda evidencia segura. La simulación visual del dashboard se rotula explícitamente como local y no conectada.
5. La segunda recuperación usa `contract-compatibility` y conserva evidencia separada. Permite demostrar que la memoria no es una regla fija ni una simulación, sin añadir llamadas al modelo.
6. La discusión de arquitectura ubica Agent Memory antes de la inferencia: recuperación scoped, composición de contexto, OCI Generative AI y, fuera del alcance de Lab 1, una posible herramienta o acción.
7. La comparación final hace dos llamadas reales, equivalentes y acotadas al mismo modelo OCI. El dashboard presenta los tokens de entrada, salida, total y latencia devueltos por el proveedor. La reducción de tokens de entrada no equivale por sí sola al costo total de la solución.
8. Lab 1 usa `KEYWORD` para disminuir prerequisitos. Lab 2 incorporará embeddings y ADB Vector Search.

## Fallas previsibles

| Señal | Causa probable | Acción segura |
| --- | --- | --- |
| `LAB01_SESSION_NOT_READY` | Wallet, entorno virtual o sesión faltante | Revisar el material privado; no pedir publicar wallet |
| Error al crear `OracleAgentMemory` como app user | Store, paquete propietario o grants faltantes | Corregir con owner; verificar `EXECUTE` sobre el paquete público y `SELECT` sobre `AGENT_MEMORY_STORES`; no reemplazar por `ADMIN` |
| Error mTLS / `tnsnames.ora` | Ruta de wallet equivocada | Redistribuir wallet privado; no copiar al repo |
| `ISOLATION_PASS False` | Error de algoritmo, bundle o control scope | Detener publicación compartida y revisar datos sintéticos |
| Recuperación procedural vacía | El término `KEYWORD` no aparece en la regla | Revisar `retrieval_query` y usar una palabra explícita de la regla, por ejemplo `idempotency`; no cambiar la política ni usar `ADMIN` |
| `MEMORY_PROMPT_TOKENS` no es menor | El bundle recuperó demasiadas decisiones o el modelo no devolvió uso comparable | Detener el cierre de evidencia, revisar el bundle y el modelo aprobado; no presentar resultados locales como medición OCI |
| Error de uso o respuesta truncada | El modelo no devolvió el bloque `usage`, faltan permisos o el límite es insuficiente | Validar el modelo durante preflight; no sustituir por estimaciones locales |

## Cierre y limpieza

Guarda solo JSON de evidencia sin secretos. Invalida credenciales temporales, retira wallets y elimina usuarios de aplicación únicamente con aprobación explícita. La destrucción de ADB, compartment o recursos Terraform se revisa y aprueba como actividad separada, nunca durante el laboratorio.
