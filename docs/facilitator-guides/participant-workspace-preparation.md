# Preparación segura de espacios privados de participantes

## Alcance

Este procedimiento crea únicamente directorios privados y una copia con placeholders del archivo de sesión. No crea identidades OCI, usuarios ADB, wallets, contraseñas, tokens ni recursos en OCI.

El script se debe ejecutar desde la raíz privada del proyecto:

```powershell
.\scripts\private\prepare-participant-workspace.ps1 -ParticipantCode P02
```

El modo predeterminado es de validación: informa si los directorios y el template existen, sin escribir nada.

Cuando el código del participante esté confirmado, crea el espacio privado y el archivo pendiente:

```powershell
.\scripts\private\prepare-participant-workspace.ps1 -ParticipantCode P02 -Initialize
```

Resultado esperado:

```text
C:\KhipuPrivate\participants\P02\
  session\T01-P02-session.ps1.pending
  wallet\
  onboarding\
```

`T01-P02-session.ps1.pending` no es ejecutable: conserva placeholders y debe completarse solamente después de que la facilitadora haya confirmado la identidad OCI, confirmado que el usuario temporal ADB tiene los grants de runtime requeridos y elegido el canal privado para la wallet.

> Estado de esta preparación en el tenant actual: los usuarios ADB `P02` a `P09` y sus grants
> de runtime ya fueron aprovisionados por lote. Las identidades OCI P02–P09 se habilitaron, se
> agregaron al grupo IAM aprobado y recibieron su solicitud oficial de activación. La confirmación
> del enlace y la sesión OCI local siguen pendientes para cada persona. Los paquetes
> privados P02–P09 ya fueron materializados y validados estructuralmente: contienen el wallet y el
> archivo final de sesión sin contraseñas ni placeholders, y fueron enviados individualmente junto
> con un mensaje separado de credenciales. P10 completó
> activación de identidad, usuario ADB, grants de runtime, sesión OCI, preflight y corrida real
> desde un clon limpio. Su wallet y archivo privado de sesión permanecen en el directorio de
> facilitación y la evidencia segura confirmó persistencia, aislamiento y economía de contexto.

## Materializar el paquete privado después de los grants

Después de confirmar identidad, usuario ADB y grants de runtime, la facilitadora puede copiar el
wallet existente y crear el archivo final de sesión sin secretos. Esta acción es privada, se hace
una vez por código y no modifica OCI ni ADB:

```powershell
.\scripts\private\materialize-participant-package.ps1 `
  -ParticipantCode P10 `
  -TeamCode T01 `
  -FacilitatorSession "C:\KhipuPrivate\sessions\T01-P01-session.ps1" `
  -TenancyName "<workshop-tenancy-name>"
```

El script se detiene si ya existe un archivo de sesión final o si el directorio de wallet contiene
material previo; así evita reemplazos accidentales. Su salida esperada es:

```text
PARTICIPANT_PACKAGE_READY P10
PARTICIPANT_PACKAGE_WALLET_COPIED P10
PARTICIPANT_PACKAGE_SESSION_READY P10
```

El archivo final solo define rutas, perfil esperado, modelo, scope y datos de conexión no secretos.
El participante aún debe crear su propia sesión OCI mediante `oci session authenticate`; no se
incluyen tokens ni contraseñas en el paquete.

## Materialización P02–P09 — completada

Los paquetes P02–P09 fueron generados de forma individual. Para cada código se validó:

- archivo final de sesión presente;
- archivos requeridos del wallet presentes;
- variables de configuración requeridas presentes;
- ausencia de placeholders en el archivo final;
- contraseña ADB protegida mediante DPAPI presente.

Esta validación no autentica la identidad OCI de la persona ni sustituye su preflight. Los paquetes
se enviaron individualmente el 30 de octubre de 2026 después de aprobación explícita; no contienen
tokens OCI y solo funcionan después de que cada persona active su identidad y cree su propia sesión.

## Secuencia posterior a recibir el correo

1. Registrar en la matriz privada que la persona completó el enlace de activación OCI.
2. Verificar que la identidad OCI pertenece al grupo IAM aprobado. No reenviar invitaciones sin
   revisar el estado individual y contar con autorización.
3. Confirmar que el usuario temporal ADB existe y tiene los grants de runtime. Si no se preparó
   previamente por lote, crearlo y aplicar los grants de runtime.
4. Completar el archivo de sesión privado; no guardar la contraseña de ADB ni del wallet dentro de él.
5. Copiar la wallet al directorio privado y entregar ambos materiales por el canal aprobado.
6. Pedir al participante autenticarse con su propia identidad OCI y ejecutar preflight.

La automatización de los pasos 2 y 3 requiere acciones de IAM y ADB. Se mantiene fuera de este script para que no se creen accesos reales sin una lista de participantes confirmada y una autorización explícita.
