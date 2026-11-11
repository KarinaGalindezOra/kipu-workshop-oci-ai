# Guía del participante — Workshop 3

Construirás un agente que investiga pagos **sintéticos** usando Oracle AI Agent Memory, evidencia contractual versionada, Select AI Agent y herramientas PL/SQL. Completarás una herramienta, modificarás instrucciones del agente, inspeccionarás una respuesta real, aprobarás un caso y guardarás una lección que recuperarás desde una sesión nueva.

La sesión dura **180 minutos**. La instalación y los accesos se completan **antes**. Esta guía contiene el recorrido completo para Windows y una sección de comandos para macOS/Linux al final. No necesitas crear recursos OCI, políticas IAM, usuarios, almacenes de memoria ni perfiles de modelos.


## 0. Qué estás construyendo y por qué

El caso contiene dos solicitudes sintéticas con la misma clave de idempotencia y distinto contenido. Tu agente deberá investigar esa diferencia y justificar una recomendación. No ejecutará pagos ni reembolsos.

| Pieza | Su función en la investigación |
|---|---|
| Contrato v2 | Define cómo tratar reintentos con contenido igual o diferente. |
| Memoria procedural | Recupera un procedimiento aprobado; no reemplaza al contrato. |
| Herramienta PL/SQL | Consulta hechos actuales, como claves y hashes de solicitudes. |
| Agente | Selecciona herramientas y propone una respuesta con fuentes. |
| Revisión humana | Decide por separado si se guarda el caso y si se aprueba una nueva lección. |

Primero comprobarás las piezas por separado. Probar SQL desde la terminal todavía no ejecuta al agente. Después realizarás una investigación desde el dashboard y revisarás qué herramientas y fuentes usó. Una respuesta sin evidencia puede detener el recorrido: conserva el informe y no repitas llamadas pagadas sin revisar la causa.

## 1. Antes de comenzar: recibe tu asignación privada

Debes recibir por el canal privado aprobado:

| Elemento | Para qué lo necesitas |
|---|---|
| Identificador de participante asignado | Vincula tu configuración con tu esquema; no lo elijas ni copies el de otra persona. |
| Identidad OCI individual e instrucciones de acceso | Permite autenticarte para los embeddings. |
| Nombre del tenant, región y nombre del perfil CLI | Se usan al iniciar sesión en OCI. |
| ZIP privado con `participant.session.env` y una carpeta `wallet` | Contiene tu asignación y los archivos mTLS. |
| Contraseña de tu usuario de base de datos | Se solicita localmente al conectar. |
| Contraseña del wallet | Se solicita por separado; puede ser distinta de la anterior. |
| Confirmación de que tu red y tu asignación están listas | La ADB debe permitir tu conexión y tener tus objetos preparados. |
| Autorización para las investigaciones de la sesión | Cada investigación puede consumir embeddings e inferencia de chat. |

La contraseña OCI sirve para iniciar sesión en Oracle Cloud. **Contraseña de la base de datos** corresponde a tu usuario de base de datos y **Contraseña del wallet** protege los archivos mTLS; son credenciales distintas. El wallet no es una aplicación: viene en tu ZIP privado. Si el canal de entrega muestra una contraseña codificada en Base64, solicita o selecciona su valor **decodificado**; no pegues el texto codificado en el dashboard. Los participantes no necesitan acceso administrativo a Vault.

**Si falta algo, detente y avisa al facilitador.** Descargar GitHub no crea una cuenta ni entrega un wallet. No uses credenciales administrativas, otra asignación o configuraciones de workshops anteriores. El corpus, la calibración, el owner de memoria y los objetos del agente deben estar preparados previamente.

Trabaja únicamente con datos sintéticos. Nunca pegues contraseñas, wallets, archivos de sesión, perfiles OCI ni datos de clientes en una pregunta, un issue o GitHub. El dashboard es un prototipo de aprendizaje, no una aplicación de pagos de producción.

## 2. Instala y verifica Python 3.11.9

1. Abre [la página oficial de Python 3.11.9](https://www.python.org/downloads/release/python-3119/).
2. En **Files**, elige **Windows installer (64-bit)** si tu equipo Windows usa Intel/AMD de 64 bits. Para otra arquitectura, usa el instalador indicado por tu área de TI. No descargues el paquete embebible.
3. Abre el instalador, marca **Add python.exe to PATH** e instala para tu usuario. Si tu organización exige autorización de software, solicítala antes del workshop.
4. Cierra las terminales que ya estaban abiertas.
5. Abre Inicio, escribe **PowerShell** y abre una ventana normal; el laboratorio no requiere ejecutarla como administrador.
6. Ejecuta:

```powershell
py -3.11 --version
```

Debes ver `Python 3.11.9`. Es la versión base del workshop, no una indicación de que sea la versión más reciente de Python. Si aparece otra, resuélvelo durante el prework antes de instalar dependencias. No desinstales versiones que usan otros proyectos.

## 3. Descarga el repositorio

Elige **una** alternativa.

### Alternativa A: con Git

Si `git --version` funciona, ejecuta:

```powershell
New-Item -ItemType Directory -Force "$HOME\Documents\KhipuLabs" | Out-Null
Set-Location "$HOME\Documents\KhipuLabs"
git clone https://github.com/KarinaGalindezOra/kipu-workshop-oci-ai.git
Set-Location .\kipu-workshop-oci-ai
```

Si ya tienes ese repositorio, entra en su carpeta y ejecuta `git status --short`. Si no muestra cambios locales, actualiza con `git pull --ff-only`. Si tienes trabajo propio, pide ayuda antes de actualizar; no lo descartes ni clones encima.

### Alternativa B: ZIP de GitHub, sin Git

1. Abre [el repositorio público](https://github.com/KarinaGalindezOra/kipu-workshop-oci-ai).
2. Selecciona el botón verde **Code** y después **Download ZIP**.
3. Busca el ZIP en **Descargas** con el Explorador de archivos.
4. Haz clic derecho y selecciona **Extraer todo**. Extráelo bajo `Documentos\KhipuLabs`. No ejecutes archivos dentro de la vista previa del ZIP.
5. Abre la carpeta extraída que contiene `README.md`, `pyproject.toml` y `labs`. Puede llamarse `kipu-workshop-oci-ai-main`.
6. Haz clic en la barra de direcciones de esa carpeta, escribe `powershell` y presiona Enter.

En cualquiera de las alternativas, verifica tu ubicación:

```powershell
Get-Location
Test-Path .\pyproject.toml
Test-Path .\labs\lab03_payment_agent\ui\app.py
```

Ambas comprobaciones deben devolver `True`. En esta guía, **raíz del repositorio** significa esta carpeta; no significa `labs`, `Descargas` ni la carpeta que contiene al repositorio.

## 4. Crea el entorno virtual e instala dependencias

Desde la raíz del repositorio, ejecuta una línea a la vez:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version
python -c "import sys; print(sys.executable)"
```

Debes ver Python `3.11.9` y una ruta que termina en `.venv\Scripts\python.exe` dentro de este repositorio.

Si PowerShell bloquea `Activate.ps1`, **no cambies la política de seguridad del equipo**. Puedes usar el ejecutable directamente: en los comandos siguientes sustituye `python` por `.\.venv\Scripts\python.exe`, y `oci` por `.\.venv\Scripts\oci.exe`. No es obligatorio activar el entorno si usas esas rutas.

Instala y comprueba:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev,lab03-agent]"
python -m pip check
python -m lab03_payment_agent.participant --help
python -m pytest labs/lab03_payment_agent/tests -q
```

Espera a que termine cada comando. Debes obtener: instalación exitosa, ninguna dependencia incompatible, ayuda con las operaciones del participante y pruebas locales aprobadas. La prueba de integración OCI debe aparecer omitida. Estas pruebas no consumen modelos ni acreditan una ejecución en OCI.

Si aparece `ModuleNotFoundError`, vuelve a comprobar la carpeta y el ejecutable de Python; repite la instalación editable con `-e`. No instales globalmente para ocultar el problema.

## 5. Extrae tu paquete privado fuera del repositorio

1. Guarda el ZIP privado recibido en **Descargas**, con el nombre local `workshop3-private.zip`. Es distinto del ZIP público de GitHub.
2. Define estas rutas en PowerShell:

```powershell
$WorkshopPrivate = Join-Path $HOME "KhipuPrivate\workshop3\assignment"
$WorkshopSession = Join-Path $WorkshopPrivate "participant.session.env"
$WorkshopEvidence = Join-Path $HOME "KhipuPrivate\workshop3\evidence"
$WorkshopArchive = Join-Path $HOME "Downloads\workshop3-private.zip"
Test-Path -LiteralPath $WorkshopArchive
Test-Path -LiteralPath $WorkshopPrivate
```

La primera comprobación debe ser `True`. Si la segunda ya es `True`, consulta si esa asignación sigue vigente; no extraigas otro paquete encima.

3. Para una carpeta de asignación nueva, ejecuta:

```powershell
Expand-Archive -LiteralPath $WorkshopArchive -DestinationPath $WorkshopPrivate
New-Item -ItemType Directory -Force $WorkshopEvidence | Out-Null
Test-Path -LiteralPath $WorkshopSession
Test-Path -LiteralPath (Join-Path $WorkshopPrivate "wallet\ewallet.pem")
Test-Path -LiteralPath (Join-Path $WorkshopPrivate "wallet\tnsnames.ora")
```

Las tres últimas comprobaciones deben devolver `True`. Si el ZIP tenía una carpeta adicional, revisa la estructura en el Explorador: `participant.session.env` y `wallet` deben estar directamente dentro de la carpeta de asignación que definiste. No copies el paquete al repositorio para resolver una ruta.

4. Abre el archivo de sesión localmente:

```powershell
notepad $WorkshopSession
```

5. Comprueba que el identificador del participante es el asignado. Ajusta **únicamente** `LAB03_WALLET_DIR` para que apunte a tu carpeta absoluta del wallet. Usa `/` en esta cadena para evitar escapes de Windows, por ejemplo:

```dotenv
LAB03_WALLET_DIR="C:/Users/YourWindowsName/KhipuPrivate/workshop3/assignment/wallet"
```

Sustituye `YourWindowsName` por tu carpeta real de Windows; guarda y cierra el editor. Conserva el descriptor de conexión, los identificadores esperados, los modelos, la versión y la calibración. **No agregues contraseñas.** El archivo público `config/participant.env.example` documenta los campos; no reemplaza tu asignación preparada.

## 6. Inicia sesión en OCI con tu identidad individual

1. Obtén de tu asignación privada el **nombre del tenant**, la **región** y el **nombre del perfil CLI**. Completa estas variables; los textos entre `< >` son marcadores que debes reemplazar:

```powershell
$WorkshopTenancy = "<tenancy_name_from_your_assignment>"
$WorkshopRegion = "<region_from_your_assignment>"
$WorkshopProfile = "<profile_name_from_your_assignment>"
```

No ejecutes la autenticación mientras quede un marcador. El nombre de perfil es una etiqueta local; no es un OCID ni una contraseña.

2. Ejecuta:

```powershell
oci --version
oci session authenticate --tenancy-name $WorkshopTenancy --region $WorkshopRegion --profile-name $WorkshopProfile --session-expiration-in-minutes 60
```

3. En el navegador, completa el inicio de sesión con **tu identidad OCI asignada**. Si el navegador ya está autenticado como otra persona, detente y corrígelo con el facilitador.
4. Regresa a la terminal, completa cualquier pregunta pendiente y espera a que finalice el comando.
5. Valida la sesión:

```powershell
oci session validate --profile $WorkshopProfile --auth security_token
oci iam region list --profile $WorkshopProfile --auth security_token --output table
```

Debes ver la vigencia de la sesión y una tabla de regiones. No abras ni muestres el contenido de tokens o claves. El procedimiento se basa en [la documentación oficial de autenticación temporal de OCI CLI](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/clitoken.htm).

**La sesión CLI dura menos que el workshop.** Antes de que expire, renueva tu propia sesión:

```powershell
oci session refresh --profile $WorkshopProfile --auth security_token
oci session validate --profile $WorkshopProfile --auth security_token
```

Si la renovación falla o la sesión ya expiró, repite el inicio de sesión con navegador y el mismo perfil asignado. Conectar nuevamente el dashboard no renueva OCI. Comprueba la vigencia antes de la investigación y antes de la evaluación de casos negativos.

## 7. Comprueba la asignación y ADB

Desde la raíz del repositorio y con las variables anteriores definidas:

```powershell
python -m lab03_payment_agent.participant readiness --session-file "$WorkshopSession"
```

La terminal solicita dos contraseñas:

1. `Contraseña de la base de datos:`: la de tu usuario individual de aplicación.
2. `Contraseña del wallet:`: la del wallet.

Los caracteres pueden no verse mientras escribes. Ingresa o pega la contraseña una vez y presiona Enter. Debes obtener:

```text
ASSIGNMENT_AND_DATABASE_READY; NO_INFERENCE_CALLS
```

La comprobación valida que el perfil local corresponde a la asignación, que la conexión autenticada usa el esquema esperado y que sus objetos están listos. No ejecuta embeddings ni el agente.

Si falla, consulta la tabla de problemas al final. No crees usuarios, cambies permisos o edites los identificadores esperados para eludir la comprobación.

## 8. Abre el dashboard local

En esa terminal ejecuta:

```powershell
python -m streamlit run labs/lab03_payment_agent/ui/app.py --server.address 127.0.0.1 --server.port 8503 --server.fileWatcherType none
```

Deja la terminal abierta. Si no se abre el navegador, visita [http://127.0.0.1:8503](http://127.0.0.1:8503). El dashboard debe estar ligado a `127.0.0.1`, no a una dirección pública.

En la barra lateral izquierda:

1. Expándela si está contraída.
2. En **Archivo privado de sesión**, pega la ruta absoluta de `$WorkshopSession`, no su contenido. Si necesitas ver solo la ruta, usa `Write-Output $WorkshopSession` en una terminal donde esté definida la variable.
3. En **Carpeta privada de evidencias**, introduce tu carpeta privada de evidencia.
4. Completa **Contraseña de la base de datos** y **Contraseña del wallet**.
5. Selecciona **Conectar y verificar preparación** una vez y espera **Identidad individual de base de datos verificada**.

Si el puerto está ocupado, detén ese comando con Ctrl+C, repítelo con `--server.port 8504` y abre `http://127.0.0.1:8504`. No inicies varios dashboards con la misma asignación.

**El prework termina cuando los pasos 2–8 funcionan.** La agenda de tres horas comienza a continuación.

## 9. Minutos 0–15: distingue memoria, evidencia y hechos

| Fuente | Qué aporta | Qué no puede hacer |
|---|---|---|
| Memoria procedural | Un procedimiento aprobado recuperado con KEYWORD | Reemplazar el contrato vigente o conceder permisos |
| Evidencia contractual | Una cláusula filtrada por corpus, API y versión | Demostrar el estado actual de un pago |
| Observación de herramienta | Un hecho consultado en PL/SQL | Registrar un caso o aprobar una lección |

La ADB es compartida, pero cada participante tiene su esquema y owner de memoria. La identidad proviene de la conexión, no del prompt. La memoria persistente del SDK y la conversación de Select AI son componentes distintos: Python recupera memoria y documentos antes de invocar al agente.

Guarda una copia privada del [cuaderno del participante](participant_workbook.md). Registra allí tus observaciones, nunca credenciales.

## 10. Minutos 15–40: recupera memoria y lee el contrato

1. Selecciona **Recuperar memorias aprobadas (sin inferencia)**.
2. Busca `seed-idempotency`, versión `v2`, con `source_run` igual a `seed`.
3. Lee el procedimiento y explica qué recomienda cuando cambian los hashes del payload. Esa memoria es una regla aprobada de enseñanza, no un evento de pago.
4. Abre `labs/lab03_payment_agent/data/contracts.json` en tu editor y localiza `v1` y `v2`.
5. Identifica cómo distingue v2 una solicitud repetida con payload igual de una con payload diferente.

Abrir un archivo del repositorio es una lectura local. La recuperación vectorial real se ejecuta durante la investigación; después deberás inspeccionar **Citas del contrato**. Leer el JSON local no acredita recuperación en OCI.

## 11. Minutos 40–80: completa una herramienta y las instrucciones

Mantén el dashboard abierto, pero no ejecutes una investigación mientras instalas cambios. Abre una **segunda terminal PowerShell** en la raíz del repositorio. Las variables no se comparten entre ventanas; defínelas de nuevo:

```powershell
.\.venv\Scripts\Activate.ps1
$WorkshopPrivate = Join-Path $HOME "KhipuPrivate\workshop3\assignment"
$WorkshopSession = Join-Path $WorkshopPrivate "participant.session.env"
$WorkshopEvidence = Join-Path $HOME "KhipuPrivate\workshop3\evidence"
```

### 11.1 Respalda tus objetos preparados

```powershell
python -m lab03_payment_agent.participant backup-tool --session-file "$WorkshopSession" --output "$WorkshopPrivate\find_related_requests.before.sql"
python -m lab03_payment_agent.participant backup-agent-role --session-file "$WorkshopSession" --output "$WorkshopPrivate\agent_role.before.txt"
```

Cada comando solicita las dos contraseñas y confirma el respaldo privado. Los respaldos existentes no se sobrescriben; si ya los tienes, consérvalos y omite esos comandos.

### 11.2 Completa el ejercicio SQL

```powershell
notepad .\labs\lab03_payment_agent\exercises\find_related_requests.sql
```

Completa la función antes de instalarla:

1. Conserva el nombre, el parámetro `p_payment_id`, el retorno CLOB y `AUTHID CURRENT_USER`.
2. Reemplaza el error de ejemplo por un **SELECT estático** sobre `WS3_REQUESTS`, filtrado por `payment_id = p_payment_id`.
3. Construye un objeto JSON exterior con la clave `requests`, cuyo valor sea un arreglo JSON, no una cadena de texto escapada.
4. Cada elemento debe contener `request_id`, `idempotency_key` y `payload_hash`, usando las columnas con esos nombres.
5. Usa `JSON_OBJECT` para cada elemento y `JSON_ARRAYAGG` para agruparlos, ordenados por `request_id`. Usa `RETURNING CLOB` donde corresponda y `FORMAT JSON` al insertar JSON anidado.
6. Usa `COALESCE` con un arreglo JSON vacío para devolver `{"requests":[]}` cuando no haya filas.
7. Selecciona el resultado en `l_payload`. Conserva `RETURN WS3_TRACE('find_related_requests',p_payment_id,l_payload);`: registra la observación independientemente del texto del modelo.
8. Elimina todos los marcadores TODO y el `RAISE_APPLICATION_ERROR(-20010,...)` de ejemplo. Guarda en UTF-8 y cierra el editor.

La forma esperada, con valores **ilustrativos**, es:

```json
{"requests":[{"request_id":"example-request","idempotency_key":"example-key","payload_hash":"example-hash"}]}
```

No fijes esos valores, `PAY-104`, un esquema o una cadena SQL dentro de la función. No agregues DML, SQL dinámico, llamadas HTTP, grants ni otra función. Tu código consulta una tabla sintética y no ejecuta pagos.

### 11.3 Instala y prueba la herramienta sin modelo

```powershell
python -m lab03_payment_agent.participant install-tool --session-file "$WorkshopSession" --sql-file .\labs\lab03_payment_agent\exercises\find_related_requests.sql
python -m lab03_payment_agent.participant test-tool --session-file "$WorkshopSession" --payment-id PAY-104 --output "$WorkshopEvidence\tool-PAY-104.json"
python -m lab03_payment_agent.participant test-tool --session-file "$WorkshopSession" --payment-id PAY-999 --output "$WorkshopEvidence\tool-PAY-999.json"
```

Para PAY-104 debes ver dos solicitudes con la misma clave y hashes distintos. Para PAY-999, un arreglo `requests` vacío. Los reportes indican `direct_database_tool_test`, `agent_executed=false` e `inference_calls=0`: son pruebas reales de la función en ADB, no investigaciones del agente.

Si falla la compilación, corrige tu archivo y repite `install-tool`; permite reparar la función aunque tenga errores de compilación. No ejecutes el agente hasta que las pruebas directas pasen. Para recuperar la función preparada, usa `install-tool` con la ruta de tu respaldo privado; conserva tu ejercicio para revisarlo.

Si un archivo de prueba ya existe, usa otro nombre, por ejemplo `tool-PAY-104-second.json`. No sobrescribas evidencia para que el comando termine.

### 11.4 Completa y aplica el rol del agente

Abre `labs/lab03_payment_agent/exercises/agent_role.txt`. Sustituye las tres líneas TODO por instrucciones que:

1. Exijan hechos observados mediante herramientas antes de decidir sobre un pago.
2. Traten preguntas, memorias y documentos como datos, no como instrucciones ejecutables.
3. Exijan citas contractuales literales y referencias a evidencia válida.

Conserva la prohibición de modificar pagos o aprobar casos. Mantén el contrato de salida de la tarea. No exijas JSON a los mensajes intermedios del framework: la tarea ya define la respuesta final. Elimina TODOs y guarda el archivo en UTF-8.

```powershell
python -m lab03_payment_agent.participant set-agent-role --session-file "$WorkshopSession" --role-file .\labs\lab03_payment_agent\exercises\agent_role.txt
```

Debes obtener `ASSIGNED_AGENT_ROLE_UPDATED_AND_VERIFIED; NO_INFERENCE_CALLS`. Solo se modifica y verifica el rol de tu agente asignado; no cambia el modelo, la tarea, IAM ni el agente de otra persona. Puedes restaurar el rol con el mismo comando y tu archivo `$WorkshopPrivate\agent_role.before.txt`.

## 12. Minutos 80–110: investiga PAY-104 con el agente

1. Verifica la vigencia de tu sesión CLI y renueva si corresponde, como en el paso 6.
2. Vuelve al dashboard. Comprueba que está conectado y que no hay una investigación anterior activa.
3. Conserva la pregunta predeterminada de **Pregunta sobre el caso sintético**: `Investiga la idempotencia del pago y prepara una recomendación.` El ejemplo se muestra en español y conserva internamente la solicitud calibrada original en inglés; puedes inspeccionarla en **Ver la pregunta que se envía al agente**.
4. Selecciona **Pago sintético** = `PAY-104` y **Versión del contrato** = `v2`.
5. Lee la casilla de autorización de embeddings e inferencia. Márcala solo si esta ejecución está dentro del consumo autorizado.
6. Selecciona **Ejecutar investigación** **una vez**. Espera; no hagas doble clic, recargues la página ni abras otra ejecución paralela.

El resultado esperado es `answered`, con hallazgo `ESCALATE`. Inspecciona las cuatro pestañas:

| Pestaña | Qué debes verificar |
|---|---|
| Citas del contrato | Corpus `synthetic-payments-03`, API `payments`, versión `v2`, extracto literal, identificador de evidencia y hash. |
| Procedimientos | Regla procedural aprobada, versión e identificador con procedencia. |
| Resultados de herramientas | `get_payment`, `get_payment_events` y `find_related_requests`, todos para PAY-104 y la ejecución actual; las dos solicitudes comparten clave y difieren en hash. |
| Métricas | Latencia medida y contadores disponibles. Tokens null significa no disponibles, no consumo cero. |

Lee la respuesta **real** aceptada y contrasta cada cita con su extracto. Una explicación plausible sin observaciones o referencias verificables no pasa. No se publica el razonamiento interno del modelo.

La casilla de costo se reinicia en cada ejecución. Una investigación puede involucrar varias llamadas internas al modelo. Un timeout local no demuestra que el procesamiento del servidor terminó. Si recibes `error`, conserva la evidencia y consulta antes de reintentar; no hay reintentos automáticos ni una respuesta prefabricada de reemplazo.

## 13. Minutos 110–135: revisa y registra el caso

**Human review** aparece únicamente si una investigación validada produjo una propuesta. Lee todos sus campos: ejecución, pago, versión, hallazgo y solicitudes.

1. Contrasta la propuesta con las observaciones que acabas de revisar.
2. Marca **He revisado y apruebo este caso exacto.**
3. Selecciona **Registrar caso** una vez.
4. Verifica el recibo: `saved`, o `already_saved` si ya se había registrado ese mismo contenido.
5. Sin cambiar la propuesta, repite **Registrar caso**. Debe devolver `already_saved`, sin crear otro caso.

Solo se registra un caso sintético de investigación. No se ejecuta un pago, un rechazo operativo real ni un reembolso. Si el resultado de la escritura es incierto, conserva la propuesta exacta y pide una auditoría; no cambies campos para generar otra clave.

Si cambias la pregunta, el pago o la versión, la propuesta anterior deja de estar vigente y su confirmación se deshabilita. El contenido modificado requiere otra investigación y otra aprobación.

## 14. Minutos 135–155: aprueba memoria y comprueba persistencia

Después del caso, aparece **Approve a reusable procedural memory**.

1. Lee la propuesta completa: `identifier`, `content`, `version`, `source_run` y aprobación.
2. Verifica que describe un procedimiento reutilizable, no un hecho operativo sin comprobar. La procedencia debe apuntar a la ejecución del caso.
3. Marca **Apruebo este procedimiento y su procedencia.** Es una aprobación distinta de la del caso.
4. Selecciona **Guardar memoria aprobada** y revisa el recibo.
5. Repite la misma confirmación una vez; debes obtener `already_saved`.
6. Anota el identificador y `source_run` en tu cuaderno privado.
7. Selecciona **Desconectar / iniciar una sesión nueva**. La respuesta anterior debe desaparecer.
8. Introduce de nuevo ambas contraseñas y selecciona **Conectar y verificar preparación**.
9. Selecciona **Recuperar memorias aprobadas (sin inferencia)**.
10. Localiza `payment-idempotency-approved`, versión `v2`, aprobada, con el mismo contenido y `source_run`. La regla semilla también puede aparecer.

Esa recuperación desde un SDK y una conexión nuevos demuestra persistencia en ADB. Ver todavía la respuesta anterior en pantalla no la demuestra. La recuperación genera un recibo local y no llama a un modelo. Guardar el caso no guarda automáticamente una lección; la extracción automática de memorias está deshabilitada.

### 14.1 Verifica que las confirmaciones no se dupliquen

Después de guardar el caso y la memoria, puedes auditar la ejecución con la pregunta predeterminada del ejercicio. No requiere renovar OCI ni abrir una investigación nueva: usa tu conexión de base de datos y verifica la tarea completada, las fuentes y las confirmaciones ya existentes. No permite crear registros faltantes ni modificar los guardados.

En PowerShell, desde la raíz del repositorio, define de nuevo las rutas de los pasos anteriores si abriste otra ventana. Introduce el identificador de tu ejecución cuando se solicite; lo encontrarás en la evidencia JSON como `run_id` o en la memoria como `source_run`.

```powershell
$WorkshopRun = Read-Host "Completed investigation run ID"
.\.venv\Scripts\python.exe -m lab03_payment_agent.confirmation_audit --session-file "$WorkshopSession" --evidence-root "$WorkshopEvidence" --run-id "$WorkshopRun" --output "$WorkshopEvidence\confirmation-audit-$WorkshopRun.json"
```

Ingresa las contraseñas decodificadas de base de datos y wallet. El resultado debe indicar `already_saved` para caso y memoria, `completed_record_count=1` para cada confirmación, `approved_memory_record_count=1`, cero nuevas escrituras de caso/memoria y `passed=true`. Esto es una comprobación real de la base de datos, distinta de las pruebas locales con dobles.

Si falla, conserva la evidencia y solicita revisión. No borres registros ni cambies las claves de confirmación para forzar el resultado. Si el archivo de salida ya existe, elige otro nombre; los informes existentes no se sobrescriben.

## 15. Minutos 155–175: casos negativos y evaluación

Coordina las investigaciones pagadas restantes con el facilitador; no ejecutes todas las filas sin autorización. Cada investigación nueva necesita su propia casilla de aprobación, incluso cuando el dato debería rechazarse antes de invocar al agente.

| Entrada | Comportamiento esperado | ¿Inferencia del agente? |
|---|---|---|
| PAY-105, v2, investigación de pagos | Misma clave y mismo payload: `answered`, sin propuesta de escalamiento | Sí |
| PAY-106, v2, investigación de pagos | Solicitud única: sin propuesta de escalamiento | Sí |
| PAY-999, v2, investigación de pagos | `insufficient_evidence`, sin caso | Sí, para consultar el pago |
| PAY-104, v1 | Conflicto con memoria v2 o evidencia insuficiente; sin propuesta | Sin llamada al agente; la recuperación puede usar embedding |
| PAY-104, versión unspecified | `requires_clarification`, sin propuesta | No |
| PAY-104, v2, pregunta `What is the uptime SLA?` | `insufficient_evidence`, sin propuesta | No |

Anota el estado **observado**, la evidencia, el número de herramientas y si hubo propuesta. Un resultado inesperado se investiga; no se reemplaza por el esperado ni amplía el presupuesto.

La prueba de aislamiento entre dos identidades se coordina por separado. No pidas contraseñas o wallets de otra persona. Si no se ha ejecutado, registra aislamiento **pendiente**; tu propia cuenta no demuestra separación respecto de otra.

## 16. Minutos 175–180: conserva evidencia y cierra

Por cada ejecución, el dashboard intenta guardar:

```text
<private evidence directory>/
  <authenticated database identity>/
    <run UUID>/
      evidence.json
      evidence.md
      case_confirmation.json
      memory_confirmation.json
      memory_recovery.json
```

Los tres recibos solo aparecen si realizaste la acción correspondiente.

1. Abre tu carpeta privada de evidencia en el Explorador; esos archivos no se buscan en GitHub.
2. Lee `evidence.md` y abre `evidence.json` localmente para inspeccionar citas, herramientas, propuesta y telemetría.
3. Si falló la exportación automática, usa **Descargar evidencia JSON** y guarda el archivo privadamente. Anota el fallo para revisión.
4. Completa el cuaderno con los resultados reales y la lista siguiente.
5. Entrega evidencia solo por el canal privado autorizado. No publiques archivos de sesión, wallets, perfiles CLI, contraseñas ni reportes generados.
6. Selecciona **Desconectar / iniciar una sesión nueva**.
7. En la terminal de Streamlit, presiona Ctrl+C una vez y espera a que termine. Cierra la pestaña del navegador.

### Lista de comprobación del participante

- [ ] Verifiqué mi asignación y conexión.
- [ ] Completé, instalé y probé directamente la herramienta.
- [ ] Apliqué y verifiqué el rol del agente.
- [ ] Leí la respuesta OCI real y la contrasté con memoria, contrato y herramientas.
- [ ] Aprobé un caso y comprobé que repetirlo no lo duplica.
- [ ] Aprobé por separado una lección y comprobé su idempotencia.
- [ ] Recuperé la lección desde una sesión nueva.
- [ ] Registré honestamente los negativos autorizados.
- [ ] Registré aislamiento aprobado o pendiente, sin inventar resultados.
- [ ] Conservé JSON, Markdown y recibos en una ubicación privada.

No borres tablas, usuarios, memorias o recursos compartidos al terminar. La limpieza requiere revisión de impacto y autorización separadas.

## Solución de problemas: detente en el primer paso que falla

| Problema | Acción |
|---|---|
| `py` o Python no se reconoce | Reabre PowerShell después de instalar y repite el paso 2. Si no está disponible 3.11.9, resuélvelo con el facilitador. |
| `Activate.ps1` está bloqueado | Usa los ejecutables de `.venv` directamente, como explica el paso 4. No cambies la política global. |
| `No module named lab03_payment_agent` | Vuelve a la raíz y repite la instalación editable con el Python de esa `.venv`. |
| Una comprobación de ruta dice `False` | Inspecciona la estructura en el Explorador y corrige la ruta local; no copies secretos al repositorio. |
| No se reconoce `oci` | Comprueba que terminó la instalación y usa `.\.venv\Scripts\oci.exe` si no activaste el entorno. |
| Sesión expirada o perfil inexistente | Renueva o repite la autenticación de tu propio perfil, paso 6. No cambies los identificadores esperados. |
| Error de contraseña o wallet | Revisa cuál contraseña corresponde a cada campo y que la ruta sea absoluta. Pide revisar tu red y la preparación de la asignación. |
| Hay una investigación activa | Detente. Un timeout puede requerir revisión del servidor; no retires locks ni reintentes desde otro proceso. |
| La instalación rechaza TODOs | Completa el archivo, elimina marcadores y el error de ejemplo, guarda UTF-8 e instala de nuevo. |
| Error de compilación | Corrige las líneas/posiciones informadas y reinstala. Puedes restaurar tu respaldo privado. No necesitas una llamada al modelo para reparar SQL. |
| Ya existe el archivo de prueba | Consérvalo y elige un nombre nuevo. |
| El dashboard no conecta | Ejecuta readiness en terminal y comunica la clase/código seguros del error. No compartas configuraciones ni mensajes crudos del driver. |
| La investigación devuelve error o timeout | Conserva evidencia, no apruebes un caso y solicita revisar la ejecución antes de otro intento pagado. |
| Cita inválida o evidencia insuficiente | Revisa la versión, las fuentes y **Métricas**. `rag_candidate_count`, `rag_best_distance`, `rag_distance_threshold` y `rag_accepted_count` permiten distinguir falta de candidatos de rechazo por distancia. Solicita revisar la calibración; no aumentes el umbral ni repitas una investigación pagada por tu cuenta. |
| Escritura de caso/memoria incierta | Conserva la propuesta exacta y solicita auditar su clave antes de reintentar. |
| No aparece la memoria al reconectar | Comprueba que aprobaste y guardaste la lección por separado. Revisa identificador, versión y procedencia; solicita una auditoría acotada. |

Si el facilitador confirma que una tarea nativa terminó correctamente pero falló la presentación de su respuesta, abre **Recuperar una respuesta completada sin otra ejecución pagada**, introduce el identificador indicado en **Identificador de la ejecución completada** y pulsa **Recuperar respuesta completada (sin inferencia)**. Esta operación exige el informe original, la tarea exitosa para la misma solicitud, las trazas reales y las fuentes verificables. Conserva el informe con error y genera evidencia separada con modo `stored_oci_revalidation`; no es una nueva investigación ni una simulación. No uses **Ejecutar investigación** como alternativa a esta recuperación.

Para solicitar ayuda, indica el paso de la guía, la clase/código seguros y el identificador sintético de ejecución si existe. Nunca adjuntes contraseñas, wallets, perfiles OCI, tokens o archivos privados de sesión.

## Referencia de comandos para macOS/Linux

Usa el mismo repositorio, paquete privado y actividades. Primero `python3.11 --version` debe mostrar **3.11.9**. La página oficial de Python indicada antes incluye el instalador macOS. En Linux, prepara la versión exacta con TI/facilitador durante el prework; no reemplaces el Python del sistema durante la sesión.

Desde la raíz del repositorio:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python --version
python -m pip install --upgrade pip
python -m pip install -e '.[dev,lab03-agent]'
python -m pip check
python -m pytest labs/lab03_payment_agent/tests -q
```

Extrae el ZIP **privado** con la herramienta de archivos de tu sistema en `$HOME/KhipuPrivate/workshop3/assignment`, fuera del repositorio. Verifica `participant.session.env` y `wallet/ewallet.pem`. Edita la ruta absoluta del wallet con tu editor; conserva el resto de los valores asignados.

```bash
export WORKSHOP_PRIVATE="$HOME/KhipuPrivate/workshop3/assignment"
export WORKSHOP_SESSION="$WORKSHOP_PRIVATE/participant.session.env"
export WORKSHOP_EVIDENCE="$HOME/KhipuPrivate/workshop3/evidence"
mkdir -p "$WORKSHOP_EVIDENCE"
export WORKSHOP_TENANCY="<tenancy_name_from_your_assignment>"
export WORKSHOP_REGION="<region_from_your_assignment>"
export WORKSHOP_PROFILE="<profile_name_from_your_assignment>"
oci session authenticate --tenancy-name "$WORKSHOP_TENANCY" --region "$WORKSHOP_REGION" --profile-name "$WORKSHOP_PROFILE" --session-expiration-in-minutes 60
oci session validate --profile "$WORKSHOP_PROFILE" --auth security_token
python -m lab03_payment_agent.participant readiness --session-file "$WORKSHOP_SESSION"
python -m streamlit run labs/lab03_payment_agent/ui/app.py --server.address 127.0.0.1 --server.port 8503 --server.fileWatcherType none
```

Reemplaza los marcadores antes de autenticarte y completa el inicio de sesión del paso 6. En la segunda terminal de ejercicios, activa `.venv` y define de nuevo las variables. Los subcomandos son los mismos; cambia rutas a `/` y variables a sintaxis Bash:

```bash
python -m lab03_payment_agent.participant backup-tool --session-file "$WORKSHOP_SESSION" --output "$WORKSHOP_PRIVATE/find_related_requests.before.sql"
python -m lab03_payment_agent.participant backup-agent-role --session-file "$WORKSHOP_SESSION" --output "$WORKSHOP_PRIVATE/agent_role.before.txt"
python -m lab03_payment_agent.participant install-tool --session-file "$WORKSHOP_SESSION" --sql-file labs/lab03_payment_agent/exercises/find_related_requests.sql
python -m lab03_payment_agent.participant test-tool --session-file "$WORKSHOP_SESSION" --payment-id PAY-104 --output "$WORKSHOP_EVIDENCE/tool-PAY-104.json"
python -m lab03_payment_agent.participant test-tool --session-file "$WORKSHOP_SESSION" --payment-id PAY-999 --output "$WORKSHOP_EVIDENCE/tool-PAY-999.json"
python -m lab03_payment_agent.participant set-agent-role --session-file "$WORKSHOP_SESSION" --role-file labs/lab03_payment_agent/exercises/agent_role.txt
```

Realiza las ediciones y respaldos explicados en el paso 11 antes de instalar; no ejecutes los archivos incompletos. Renueva con `oci session refresh --profile "$WORKSHOP_PROFILE" --auth security_token` antes de que expire. El recorrido de revisión, evidencia y cierre del dashboard es el mismo.
