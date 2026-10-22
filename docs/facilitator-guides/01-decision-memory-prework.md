# Prework operativo — Workshop 1: memoria de decisiones y economía de tokens

## Propósito

Dejar cada trial de equipo en condición **go** antes de la sesión. Este documento prepara recursos y accesos; no autoriza crear recursos, modificar IAM, descargar wallets ni ejecutar inferencias sin las aprobaciones correspondientes.

La unidad operativa es un trial por equipo. La facilitadora conserva su tenant actual para ensayo técnico y no comparte sus credenciales con participantes.

## Ruta lineal: de un tenant trial nuevo a un participante de prueba

Esta es la ruta que debes seguir cuando el tenant trial simula el tenant de un cliente. Para el primer ensayo usa `T01` como equipo y `P01` como participante. `T01` y `P01` son códigos del laboratorio elegidos por ti; no son usuarios OCI ni identificadores que se obtengan desde la consola.

### Fase 0. Abrir y registrar los datos del tenant

**Dónde:** OCI Console del tenant nuevo.

1. En la esquina superior derecha, anota la región home del trial. Es la región que se configurará en Terraform.
2. Abre el menú principal y busca **Tenancy Details**. Copia el identificador del tenancy solamente en tu archivo privado de Terraform; no lo pegues en documentación, chat ni repositorio.
3. Decide dónde se creará el compartment del workshop:
   - Para una simulación simple, usa el tenancy root como padre. En ese caso el identificador del tenancy será también el valor de `parent_compartment_id`.
   - Si el tenant ya tiene un compartment padre aprobado, abre **Identity & Security > Compartments** y copia su identificador como `parent_compartment_id`.
4. Busca **Limits, Quotas and Usage** en la consola y confirma que ADB 26ai puede desplegarse en la región elegida. Confirma también que el modelo on-demand seleccionado está disponible en esa región.

No ejecutes Terraform hasta tener región, tenancy, parent compartment, presupuesto y modelo confirmados.

### Fase 1. Preparar Terraform localmente

**Dónde:** PowerShell en tu laptop.

```powershell
$workshopRoot = "<absolute-path-to-kipu-workshop-oci-ai>"
Set-Location "$workshopRoot\terraform\environments\trial-team"

terraform version
oci --version
oci session validate

Copy-Item .\terraform.tfvars.example .\terraform.tfvars
notepad .\terraform.tfvars
```

En `terraform.tfvars`, completa solo los valores del tenant nuevo. Para un tenant sin un compartment de workshop previo, conserva `create_workshop_compartment = true` y usa el parent confirmado en la fase 0:

```hcl
region                = "<tenant-home-region>"
tenancy_ocid          = "<tenant-identifier>"
parent_compartment_id = "<tenant-identifier-or-approved-parent-compartment>"
team_code             = "T01"

enable_autonomous_database = false
enable_object_storage      = false
enable_iam_policies        = false
```

Mantén este archivo local: contiene identificadores del tenant y está excluido de Git.

### Fase 2. Crear únicamente el compartment del workshop

**Dónde:** PowerShell. Esta fase no crea ADB.

```powershell
terraform fmt -recursive
terraform init
terraform validate
terraform plan -var-file="terraform.tfvars"
```

Revisa el plan. Debe proponer solo un recurso `oci_identity_compartment`. Si muestra ADB, bucket o IAM policy, detente y corrige el archivo antes de continuar.

Cuando el plan sea correcto, ejecútalo tú:

```powershell
terraform apply -var-file="terraform.tfvars"
terraform output workshop_compartment_name
terraform output workshop_compartment_id
```

**Verificación en Console:** busca **Compartments**, selecciona el compartment recién creado y confirma que está `Active`. No cambies aún a la consola de ADB: la base todavía no existe.

### Fase 3. Crear ADB con un segundo plan revisable

**Dónde:** PowerShell, en el mismo directorio Terraform.

1. Edita solo el archivo local `terraform.tfvars` y cambia:

```hcl
enable_autonomous_database = true
```

2. Solicita la contraseña de administrador en memoria. No la escribas en `terraform.tfvars`, comandos, historial ni archivos:

```powershell
$adbPassword = Read-Host -AsSecureString
$env:TF_VAR_autonomous_admin_password = [System.Net.NetworkCredential]::new('', $adbPassword).Password
terraform plan -var-file="terraform.tfvars"
```

3. Revisa que el plan agregue exactamente una `oci_database_autonomous_database` dentro del compartment `T01`, con versión `26ai`, mTLS habilitado y el tamaño aprobado. ADB 26ai requiere un mínimo de 2 ECPU; si la región exige un mínimo mayor, ajusta el valor en el archivo privado y vuelve a revisar el plan. Si el plan no coincide, no lo apliques.

4. Si coincide con lo aprobado, ejecuta:

```powershell
terraform apply -var-file="terraform.tfvars"
$env:TF_VAR_autonomous_admin_password = $null
Remove-Variable adbPassword
terraform output autonomous_database_id
```

**Verificación en Console:** busca **Autonomous Database**, selecciona el compartment del workshop y espera estado `Available`. La ADB se crea por Terraform; la consola se usa solo para observarla y descargar el wallet.

### Fase 4. Descargar el wallet privado

**Dónde:** OCI Console, detalle de la ADB recién creada.

Selecciona **Database Connection** y descarga un wallet de instancia. Define su contraseña cuando la consola la solicite y descomprime el archivo completo en un directorio privado, corto y sin espacios fuera del repositorio, por ejemplo `C:\KhipuPrivate\wallet_T01`. No copies el wallet a `wallet/`, Git, un ZIP de código ni el dashboard.

La ruta configurada debe ser la carpeta que contiene directamente `tnsnames.ora`, no el archivo ZIP ni una carpeta padre con otro nivel de subcarpetas. Antes de continuar, valida la ruta en PowerShell:

```powershell
Test-Path -LiteralPath "C:\KhipuPrivate\wallet_T01\tnsnames.ora"
```

El resultado obligatorio es `True`. Comprueba además que la carpeta contiene el wallet completo, no solo `tnsnames.ora`:

```powershell
@("tnsnames.ora", "sqlnet.ora", "cwallet.sso", "ewallet.p12") | ForEach-Object {
    "$($_): $(Test-Path -LiteralPath "C:\KhipuPrivate\wallet_T01\$_")"
}
```

Los cuatro resultados deben ser `True`. Si falta alguno, vuelve a descargar el wallet de instancia y usa **Extract All** sobre el ZIP antes de configurar `LAB01_WALLET_DIR`. Si existe una subcarpeta adicional creada por el extractor, apunta `LAB01_WALLET_DIR` a la carpeta interior que contiene directamente esos cuatro archivos.

Anota el nombre del servicio de conexión del wallet; será el valor de `LAB01_DB_DSN` en las sesiones de owner y participante.

### Fase 5. Continuar con los componentes del laboratorio

La frase anterior "secciones 3 a 8" no es una acción ni requiere abrir otro documento. Completa las cinco tareas siguientes, descritas más abajo en la sección **Secuencia de preparación**:

1. Crear owner y usuario de aplicación `P01`.
2. Ejecutar bootstrap del Memory Store una vez como owner.
3. Otorgar acceso de runtime al usuario `P01`.
4. Preparar archivo de sesión privado para owner y otro para `P01`.
5. Ejecutar preflight, un ejercicio real de memoria sin inferencia y una corrida live como `P01`.

Para la simulación individual puedes utilizar tu propia identidad OCI para la inferencia únicamente si ya tiene el permiso de modelo aprobado. La cuenta de base de datos sigue siendo el usuario temporal de aplicación `P01`; no uses `ADMIN` ni el memory owner como participante.

## Entregables de prework

- Un Autonomous Database 26ai operativo por equipo.
- Un Agent Memory Store precreado por equipo, con un schema owner dedicado.
- Un usuario temporal de aplicación y wallet privado por participante.
- Acceso OCI individual para cada participante al modelo on-demand aprobado.
- Grupo IAM de participantes, políticas mínimas aprobadas y membresía validada por participante.
- Un archivo de sesión privado por participante, basado en `labs/lab01_agent_memory/config/participant-session.ps1.example`.
- Un ensayo exitoso desde una identidad de aplicación no administrativa.

## Información que debe confirmarse antes de empezar

| Dato | Responsable | Criterio |
| --- | --- | --- |
| Código de equipo y lista de participantes | Facilitación | Un código `TNN` y un código `PNN` único por persona. |
| Región y compartment aprobados | Administrador OCI | La región tiene ADB 26ai y el modelo on-demand disponible. |
| Presupuesto para ADB e inferencia | Patrocinador / administrador | Aprobación explícita para ADB y dos solicitudes por participante, más el ensayo. |
| Modelo de chat | Administrador OCI | Modelo on-demand aprobado y con telemetría `usage`. |
| Identidades OCI individuales | Participantes / IAM | Cada persona puede autenticarse sin usar una sesión compartida. |

Registra el estado, no contraseñas ni valores sensibles, en `lab01-participant-roster.csv.example` copiado a un directorio privado.

## Secuencia de preparación

### 1. Validar el tenant sin cambiar recursos

Con una identidad de facilitación autorizada, valida la sesión OCI, la región y el acceso al compartment. Revisa también cuota, crédito y disponibilidad de ADB 26ai y del modelo antes de programar la sesión.

```powershell
oci --version
oci session validate
oci iam region list --output table
```

**Salida esperada:** región elegida, presupuesto y modelo aprobados. Si alguno falla, no continúes con aprovisionamiento de participantes.

### 2. Preparar la fundación del equipo

Si el equipo ya tiene un compartment y ADB aprobados, registra su uso en el roster y continúa al paso 3. Si no los tiene, usa el perfil Terraform de [`terraform/environments/trial-team`](../../terraform/environments/trial-team/README.md).

El primer plan debe mantener ADB, Object Storage e IAM policy deshabilitados. La creación de ADB y cualquier cambio IAM requieren revisión y aprobación explícitas del plan antes de `terraform apply`.

**Salida esperada:** un compartment exclusivo del equipo y una ADB 26ai operativa, con mTLS habilitado. Descarga el wallet únicamente por el canal privado aprobado; no lo incorpores a Terraform ni al repositorio.

### 3. Inicializar el propietario de memoria y los usuarios temporales

#### 3.1 Comprobar el cliente SQL y conectarse como administrador

En PowerShell, desde el directorio raíz del repositorio, verifica primero que SQLcl está disponible:

```powershell
sql -version
```

Si PowerShell no reconoce `sql`, sigue esta ruta para Windows. Es la ruta más simple: instala Java 21 LTS con Windows Package Manager y usa el ZIP oficial de SQLcl sin cambiar el PATH global de Windows.

##### Instalar Java 21 LTS

Primero verifica si Windows Package Manager está disponible:

```powershell
winget --version
```

Si responde una versión, instala Microsoft Build of OpenJDK 21:

```powershell
winget install Microsoft.OpenJDK.21
```

Acepta los términos y la elevación de Windows solo si corresponden a tu equipo. Al terminar, cierra PowerShell, abre una nueva ventana y valida:

```powershell
java -version
```

Debe indicar Java 21. Si `winget` no existe o la instalación falla, descarga e instala el JDK 21 de [Microsoft Build of OpenJDK](https://learn.microsoft.com/en-us/java/openjdk/download) mediante su instalador gráfico; luego abre una nueva ventana de PowerShell y vuelve a ejecutar `java -version`.

##### Instalar SQLcl

Con Java 21 confirmado, descarga el ZIP desde la [página oficial de Oracle SQLcl](https://www.oracle.com/database/sqldeveloper/technologies/sqlcl/). En el Explorador de archivos, selecciona el ZIP, elige **Extract All** y extráelo en `C:\Tools`. El resultado esperado es este archivo:

```text
C:\Tools\sqlcl\bin\sql.exe
```

En una nueva ventana PowerShell, valida SQLcl y habilítalo solo para esa ventana:

```powershell
& "C:\Tools\sqlcl\bin\sql.exe" -version
$env:Path = "C:\Tools\sqlcl\bin;$env:Path"
sql -version
```

Si cierras esa ventana de PowerShell, la modificación de `PATH` se pierde. Para recuperar solo
el comando `sql` en una nueva ventana, repite únicamente:

```powershell
$env:Path = "C:\Tools\sqlcl\bin;$env:Path"
```

Esto no recupera las variables del laboratorio. Cuando una tarea necesite wallet, DSN o usuario de
aplicación, vuelve a cargar también el archivo privado de sesión con `. $participantSession`.

Si elegiste otra carpeta, ajusta la ruta. SQLcl actual requiere Java 17 o 21; este procedimiento usa Java 21 LTS. No ejecutes los scripts de bootstrap desde el participante.

Si SQLcl está disponible, configura el wallet solo para esta ventana, ubícate en la raíz del repositorio y abre la conexión administrativa. Usa el alias de TNS que termina en `_tp` y la contraseña de administrador creada al desplegar ADB:

```powershell
$workshopRoot = "<absolute-path-to-kipu-workshop-oci-ai>"
Set-Location $workshopRoot
$env:TNS_ADMIN = "<absolute-path-to-private-wallet-directory>"
sql ADMIN@<TNS-name-ending-in-_tp>
```

SQLcl solicitará la contraseña de `ADMIN` sin mostrarla. Cuando el prompt cambie a `SQL>`, permanece en esa misma sesión para los comandos siguientes.

#### 3.2 Crear los usuarios de base de datos

Conéctate a ADB como administrador autorizado y ejecuta los scripts del repositorio una sola vez para el owner y una vez por participante:

```sql
@platform/bootstrap/02_create_agent_memory_owner.sql T01
@platform/bootstrap/03_create_agent_memory_application_user.sql T01 P01
```

Repite el segundo comando por cada `PNN`. Las contraseñas se ingresan interactivamente y se transfieren por un canal privado aprobado. Nunca se incluyen en archivos de configuración, argumentos, consola compartida ni dashboard.

Antes de salir de la sesión de `ADMIN`, valida que ambos usuarios requeridos existen y están habilitados. Para el ensayo de `T01` / `P01`, ejecuta:

```sql
SELECT username, account_status
FROM dba_users
WHERE username IN ('OAM_T01_OWNER', 'OAM_T01_P01')
ORDER BY username;
```

La consulta debe devolver los dos usuarios con estado `OPEN`. Si falta `OAM_T01_P01`, ejecuta de nuevo solo `03_create_agent_memory_application_user.sql T01 P01`; es idempotente y solicitará localmente la contraseña del participante.

#### Contraseñas: qué prompt usa cada una

Durante el prework existen credenciales distintas. No son intercambiables:

| Prompt o conexión | Contraseña requerida |
| --- | --- |
| `sql ADMIN@...` | Contraseña de administrador de ADB definida durante el despliegue Terraform. |
| Script `02_create_agent_memory_owner.sql` | Nueva contraseña de base de datos para `OAM_T01_OWNER`. |
| `sql OAM_T01_OWNER@...` o bootstrap del store | Contraseña de base de datos de `OAM_T01_OWNER`, no la de `ADMIN` ni la del wallet. |
| Script `03_create_agent_memory_application_user.sql` o runner participante | Contraseña de base de datos de `OAM_T01_P01`. |
| Bootstrap o runner Python | Contraseña con que se descargó el wallet, cuando el script la solicite como `Wallet password`. |

Si SQLcl devuelve `ORA-01017` para el memory owner, primero valida como `ADMIN` que el usuario exista y esté `OPEN`; no restablezcas una contraseña sin confirmar el usuario y el contexto del prompt. Si ya confirmaste ambos y autorizaste el restablecimiento, todavía conectado como `ADMIN`, ejecuta:

```sql
@platform/bootstrap/06_reset_agent_memory_owner_password.sql T01
```

Define una nueva contraseña para `OAM_T01_OWNER` (sin comillas ni `&`), guárdala únicamente en el canal privado aprobado y valida enseguida, desde PowerShell, con `sql "OAM_T01_OWNER@$env:LAB01_DB_DSN"`. No repitas `02_create_agent_memory_owner.sql`: ese script es idempotente y no cambia una contraseña existente.

**Salida esperada:** owner de memoria y un usuario temporal de aplicación por participante.

### 4. Crear el Memory Store una sola vez

Después de terminar la sección 3.2, escribe `exit` en SQLcl para volver a PowerShell. El bootstrap es un comando Python: **no lo ejecutes dentro del prompt `SQL>`**.

En PowerShell, desde la raíz del repositorio, carga estas referencias no secretas del memory owner. Reemplaza solamente la ruta del wallet y el alias `_tp` por los valores de tu tenant:

```powershell
$env:LAB01_WALLET_DIR = "<absolute-path-to-private-wallet-directory>"
$env:LAB01_DB_DSN = "<TNS-name-ending-in-_tp>"
$env:LAB01_MEMORY_SCHEMA_OWNER = "OAM_T01_OWNER"
$env:LAB01_MEMORY_OWNER_DB_USER = "OAM_T01_OWNER"
$env:LAB01_MEMORY_STORE_ID = "OAMT01"
```

No incluyas contraseñas en esas variables: el script las solicitará localmente y de forma oculta. Antes de ejecutar el bootstrap, confirma que la ruta configurada contiene el archivo requerido:

```powershell
Test-Path -LiteralPath "$env:LAB01_WALLET_DIR\tnsnames.ora"
```

El resultado debe ser `True`.

Antes de validar, elimina espacios accidentales al inicio o al final del alias. Después valida, sin imprimir valores sensibles, que el alias configurado exista en el wallet:

```powershell
$env:LAB01_DB_DSN = $env:LAB01_DB_DSN.Trim()
$dsnPattern = "^\s*" + [regex]::Escape($env:LAB01_DB_DSN) + "\s*="
if (Select-String -LiteralPath "$env:LAB01_WALLET_DIR\tnsnames.ora" -Pattern $dsnPattern -Quiet) {
    Write-Host "LAB01_OWNER_DSN_READY True"
} else {
    throw "LAB01_OWNER_DSN_READY False. Use a TNS alias from this wallet."
}
```

Si la validación falla, no ejecutes el bootstrap: corrige `LAB01_DB_DSN` con el alias `_tp` del mismo wallet. Si pasa, confirma también en OCI Console que la ADB está en estado `Available` antes de continuar.

Ahora ejecuta el bootstrap con el código de equipo correcto:

```powershell
.\.venv\Scripts\python.exe .\labs\lab01_agent_memory\scripts\bootstrap_team_memory.py --team-code T01
```

Escribe `BOOTSTRAP` solo después de verificar ADB, team code y store. Este es el único paso que usa `SchemaPolicy.CREATE_IF_NECESSARY`. No lo repitas desde cuentas participantes.

**Salida esperada:** store existente y scope de control sintético inicializado.

### 5. Otorgar solo acceso de runtime

**Precondición obligatoria:** la validación de la sección 3.2 debe mostrar `OAM_T01_OWNER` y `OAM_T01_P01` con estado `OPEN`. Si el usuario de participante no aparece, vuelve a la sección 3.2 y ejecuta el script `03_create_agent_memory_application_user.sql`; no intentes ejecutar este grant hasta que el usuario exista.

Este paso se ejecuta como el memory owner, no como `ADMIN` ni como el participante. Desde PowerShell, con las variables de la sección 4 aún cargadas, abre SQLcl:

```powershell
sql "OAM_T01_OWNER@$env:LAB01_DB_DSN"
```

Ingresa la contraseña de base de datos de `OAM_T01_OWNER`. Cuando aparezca el prompt `SQL>`, ejecuta el grant por cada usuario temporal. El segundo parámetro es el identificador lógico del Memory Store (para este equipo, `OAMT01`), no el nombre del schema:

```sql
@platform/bootstrap/04_grant_agent_memory_runtime_access.sql OAM_T01_P01 OAMT01
```

La salida esperada es `AGENT_MEMORY_RUNTIME_ACCESS_READY OAM_T01_P01 TABLES=...`. Después escribe `exit` para volver a PowerShell. Repite únicamente el comando SQL para cada participante adicional, con su usuario `OAM_T01_PNN`.

No concedas `ADMIN`, privilegios `CREATE` ni permisos de administración del store. El runner participante usa `SchemaPolicy.REQUIRE_EXISTING`.

**Salida esperada:** cada usuario puede usar el store existente, pero no crear ni administrar recursos de memoria.

### 6. Reducir privilegios de instalación del owner (cierre de hardening)

Este paso **no bloquea el ensayo funcional** de `P01`. Déjalo para después de que el preflight y la corrida live del ensayo hayan terminado correctamente; así el owner conserva capacidad de corrección mientras se valida el despliegue. Antes de la sesión con participantes, y una vez que el store y los grants de todos estén confirmados, elimina los dos privilegios de instalación que el owner ya no necesita. Desde PowerShell, conéctate de nuevo como `ADMIN`:

```powershell
sql "ADMIN@$env:LAB01_DB_DSN"
```

En `SQL>`, ejecuta:

```sql
@platform/bootstrap/05_revoke_agent_memory_setup_privileges.sql OAM_T01_OWNER
```

La salida esperada es `AGENT_MEMORY_SETUP_PRIVILEGES_REVOKED OAM_T01_OWNER`. Después escribe `exit`. No ejecutes este paso antes del bootstrap. Su aplicación no afecta a los participantes ni a sus grants existentes, pero una futura reinstalación o recreación del store requeriría que un administrador vuelva a conceder esos privilegios al owner.

### 7. Preparar OCI Generative AI por identidad individual

Este paso configura **autorización OCI para la inferencia**; no tiene relación con la contraseña `ADMIN` de ADB, el usuario `OAM_T01_P01` ni el wallet.

#### Ensayo individual de la facilitadora

Si ejecutarás el ensayo con tu propia identidad OCI y esa identidad ya es administradora del tenancy o ya puede invocar modelos on-demand de OCI Generative AI, **no crees ni modifiques una política IAM en este momento**. Registra que usarás esa identidad de ensayo y continúa a la sección 8. La corrida live de la sección 10 será la validación real, porque realiza exactamente las dos llamadas autorizadas al modelo.

#### Workshop con participantes no administradores

Antes de la sesión, un administrador IAM debe crear o reutilizar un grupo de participantes y concederle, tras la aprobación de seguridad correspondiente, el permiso mínimo para el compartment del workshop. El patrón de política es:

```text
allow group <workshop-participants-group> to use generative-ai-chat in compartment <workshop-compartment>
allow group <workshop-participants-group> to inspect generative-ai-model in tenancy
```

Asigna a cada participante a ese grupo, pero no concedas `manage generative-ai-family`, permisos de administración de ADB ni sesiones compartidas. El runner usa un modelo de chat **Cohere** on-demand aprobado para Lab 1 porque está implementado con `CohereChatRequest`; no configures un modelo de otra familia sin adaptar y probar el cliente de inferencia.

#### Lista obligatoria de IAM antes de entregar el workshop

| Responsable | Acción | Evidencia sin secretos |
| --- | --- | --- |
| Administrador IAM | Crear o reutilizar el grupo de participantes. | Nombre del grupo registrado en el roster privado. |
| Administrador IAM | Revisar y aplicar las dos políticas mínimas aprobadas. | Política visible en Console, limitada al compartment del workshop para `generative-ai-chat`. |
| Administrador IAM | Agregar a cada participante a ese grupo. | Cada identidad marcada como `IAM ready` en el roster. |
| Facilitadora | Confirmar región y modelo Cohere on-demand antes de distribuir sesiones. | Modelo y región aprobados, sin ejecutar prompts adicionales. |
| Participante | Crear su propia sesión OCI de la sección 8 y ejecutar el preflight. | `LAB01_OCI_IDENTITY_CHECK True` y `LAB01_PREFLIGHT_COMPLETE`. |

Los participantes no necesitan acceso a “todos los servicios”. Para Lab 1 solo requieren: su identidad OCI con permiso de chat, su usuario temporal `OAM_TNN_PNN`, el wallet privado entregado y el archivo de sesión. No requieren acceso a OCI Console para administrar ADB, Agent Memory, IAM, Terraform ni recursos del resto del equipo.

La comprobación sin inferencia consiste en confirmar que la identidad individual puede iniciar sesión OCI y visualizar el modelo Cohere aprobado en la misma región. No envíes prompts de prueba adicionales: el ensayo final usa exactamente dos solicitudes reales.

**Salida esperada:** un modelo on-demand aprobado, disponible en la región y autorizado para cada identidad OCI individual.

### 8. Preparar la sesión OCI y el archivo privado del participante

Cada participante debe autenticar su propia identidad OCI. No se comparten perfiles, archivos de configuración, tokens ni sesiones de navegador. En su laptop, crea un directorio privado y genera una sesión OCI para el perfil que usará en el laboratorio:

```powershell
New-Item -ItemType Directory -Force "C:\KhipuPrivate\oci" | Out-Null
$ociSessionConfig = "C:\KhipuPrivate\oci\p01-config"
$env:BROWSER = "C:\Program Files\Google\Chrome\Application\chrome.exe"
oci session authenticate `
  --config-location $ociSessionConfig `
  --profile-name LAB01_P01 `
  --region "<tenant-home-region>"
```

Este es el flujo **con navegador**. Abre Chrome con el inicio de sesión de OCI; completa la autenticación con la identidad individual del participante, vuelve a PowerShell y espera la finalización del comando. El comando crea una clave privada y un token de sesión locales dentro del directorio privado: no los copies, publiques ni subas al repositorio. Después valida la sesión sin mostrar su contenido:

```powershell
oci session validate --config-file $ociSessionConfig --profile LAB01_P01 --auth security_token
```

Los tokens de sesión expiran. Ejecuta esta preparación poco antes del preflight y vuelve a autenticarte o refresca la sesión autorizada si la validación deja de ser válida durante la jornada. No copies una sesión entre laptops.

> No uses `--no-browser` para crear por primera vez una sesión desde una laptop de participante. Ese modo requiere una autenticación previa por API key o por un token de sesión aún válido. Si el perfil anterior expiró, crea una nueva sesión con navegador en una ruta privada nueva, actualiza `OCI_CONFIG_FILE` en el archivo de sesión y conserva el perfil anterior sin modificarlo.

Ahora crea el archivo de sesión de **P01** fuera del repositorio:

```powershell
New-Item -ItemType Directory -Force "C:\KhipuPrivate\sessions" | Out-Null
$participantSession = "C:\KhipuPrivate\sessions\T01-P01-session.ps1"
Copy-Item .\labs\lab01_agent_memory\config\participant-session.ps1.example $participantSession
notepad $participantSession
```

En ese archivo, reemplaza los marcadores por las referencias no secretas de `P01`:

| Variable | Valor para el ensayo `T01` / `P01` |
| --- | --- |
| `OCI_CONFIG_FILE` | Ruta de `$ociSessionConfig`. |
| `OCI_CONFIG_PROFILE` | `LAB01_P01`. |
| `OCI_COMPARTMENT_ID` | Identificador privado del compartment del workshop `T01`. |
| `LAB01_CHAT_MODEL_ID` | Identificador del modelo Cohere chat on-demand aprobado. |
| `LAB01_WALLET_DIR` | Directorio privado que contiene directamente los cuatro archivos del wallet. |
| `LAB01_DB_USER` | `OAM_T01_P01`. |
| `LAB01_DB_DSN` | Alias `_tp` del mismo wallet, sin espacios al inicio o final. |
| `LAB01_MEMORY_SCHEMA_OWNER` | `OAM_T01_OWNER`. |
| `LAB01_MEMORY_STORE_ID` | `OAMT01`. |

No agregues contraseñas, wallet ZIP, claves privadas ni tokens a ese archivo. El launcher solicitará la contraseña del usuario `OAM_T01_P01` y la contraseña del wallet en la terminal.

### 9. Entregar el paquete privado por participante

Por canal privado, cada participante recibe:

- Acceso al repositorio o ZIP de código sin secretos.
- Directorio wallet y su contraseña, entregados separadamente.
- Usuario temporal de ADB y su contraseña, entregados separadamente.
- Archivo de sesión privado basado en `participant-session.ps1.example`.
- Códigos `TNN` y `PNN`.

El archivo de sesión contiene rutas y referencias de configuración, no contraseñas. No debe guardarse dentro del repositorio. El launcher solicita las contraseñas localmente cuando las necesita.

### 10. Ensayo y declaración go/no-go

Una persona de ensayo, usando un usuario de aplicación y una identidad OCI no administrativa, ejecuta primero:

```powershell
$participantSession = "C:\KhipuPrivate\sessions\T01-P01-session.ps1"
powershell -ExecutionPolicy Bypass -File .\labs\lab01_agent_memory\scripts\run_participant_live.ps1 `
  -TeamCode T01 `
  -ParticipantCode P01 `
  -SessionFile $participantSession `
  -Preflight
```

No copies literalmente la notación `<private-session-file>` en PowerShell. Es solo una convención de documentación; PowerShell interpreta `<` como un operador. Usa la ruta real o la variable `$participantSession` anterior.

Luego ejecuta el ejercicio real de memoria, que no llama al modelo:

```powershell
powershell -ExecutionPolicy Bypass -File .\labs\lab01_agent_memory\scripts\run_participant_live.ps1 `
  -TeamCode T01 `
  -ParticipantCode P01 `
  -SessionFile $participantSession `
  -MemoryExercise payment-idempotency
```

Confirma `LAB01_MEMORY_EXERCISE_READY`, `PERSISTENCE_CONFIRMED True`, `ISOLATION_PASS True` y
`NO_OCI_INFERENCE True`. Después realiza una sola corrida live desde el mismo launcher. Esa
etapa consume dos solicitudes on-demand con datos sintéticos.

```powershell
powershell -ExecutionPolicy Bypass -File .\labs\lab01_agent_memory\scripts\run_participant_live.ps1 `
  -TeamCode T01 `
  -ParticipantCode P01 `
  -SessionFile "C:\KhipuPrivate\sessions\T01-P01-session.ps1"
```

Cuando el launcher solicite credenciales, ingresa la contraseña del usuario `OAM_T01_P01` y la contraseña del wallet. La ejecución live hace exactamente dos llamadas de inferencia OCI. Al terminar, inicia el dashboard y carga el JSON generado:

```powershell
.\.venv\Scripts\python.exe -m streamlit run .\labs\lab01_agent_memory\ui\app.py
```

Para el ensayo `T01` / `P01`, el archivo de evidencia queda en `artifacts\lab01\t01\p01\oci-inference-evidence.json`.

Declara **go** únicamente si se cumple todo:

- `LAB01_PREFLIGHT_COMPLETE`
- `PERSISTENCE_CONFIRMED True`
- `ISOLATION_PASS True`
- `TOKEN_QUALITY_PASS True`
- `optimized_prompt_tokens < baseline_prompt_tokens`
- JSON de evidencia visible en el dashboard local.

## Go/no-go el día anterior

| Control | Go | No-go / respuesta |
| --- | --- | --- |
| ADB y Memory Store | Owner y store existentes; app user validado | Corregir bootstrap o grants con owner; nunca con `ADMIN` participante. |
| Wallet | Ruta privada y servicio de conexión correctos | Redistribuir por canal privado. |
| OCI | Sesión individual y modelo autorizados | Corregir identidad/política aprobada; no compartir sesión. |
| Runner | Preflight completo sin inferencia | Corregir configuración local antes de la sesión. |
| Evidencia | Dos respuestas completas, calidad e input reduction | Revisar modelo/bundle antes del workshop; no usar métricas estimadas como resultado real. |

## Limpieza posterior

Al cierre, conserva solo los JSON de evidencia sin secretos según la política acordada. La revocación de usuarios temporales, eliminación de wallets y destrucción de ADB/compartment son acciones separadas, potencialmente destructivas y requieren aprobación explícita.
