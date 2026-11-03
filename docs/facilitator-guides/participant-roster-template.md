# Matriz privada de asignación de participantes — Workshop 1

> Este documento es operativo y privado. No lo publiques en GitHub ni agregues contraseñas, OCIDs, tokens, contenido de wallets o evidencia de participantes.

## Propósito

Controlar la preparación individual sin mezclar identidades OCI, usuarios ADB, sesiones ni evidencia. Un código de participante representa un alcance lógico individual: `t01:pNN`.

| Código | Nombre | Correo de invitación | Identidad OCI confirmada | Grupo IAM asignado | Usuario ADB temporal | Sesión OCI validada | Preflight | Entrega privada | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P01 | Asignado durante la validación | Privado | Sí | Sí | Configurado | Validada | Aprobado | Completada | Validación end-to-end aprobada |
| P02 | Ana Lucía Cáceres | Privado | Habilitada; activación solicitada | Sí | Creado; runtime listo | Pendiente | Pendiente | Credenciales y paquete privado enviados | Esperando activación y preflight individual |
| P03 | Emilio Davis | Privado | Habilitada; activación solicitada | Sí | Creado; runtime listo | Pendiente | Pendiente | Credenciales y paquete privado enviados | Esperando activación y preflight individual |
| P04 | Juan Horta | Privado | Habilitada; activación solicitada | Sí | Creado; runtime listo | Pendiente | Pendiente | Credenciales y paquete privado enviados | Esperando activación y preflight individual |
| P05 | Alejandro Vidal | Privado | Habilitada; activación solicitada | Sí | Creado; runtime listo | Pendiente | Pendiente | Credenciales y paquete privado enviados | Esperando activación y preflight individual |
| P06 | Álvaro Millalén | Privado | Habilitada; activación solicitada | Sí | Creado; runtime listo | Pendiente | Pendiente | Credenciales y paquete privado enviados | Esperando activación y preflight individual |
| P07 | Iván Pliouchtchai | Privado | Habilitada; activación solicitada | Sí | Creado; runtime listo | Pendiente | Pendiente | Credenciales y paquete privado enviados | Esperando activación y preflight individual |
| P08 | Andrés Farías | Privado | Habilitada; activación solicitada | Sí | Creado; runtime listo | Pendiente | Pendiente | Credenciales y paquete privado enviados | Esperando activación y preflight individual |
| P09 | Flor Díaz | Privado | Habilitada; activación solicitada | Sí | Creado; runtime listo | Pendiente | Pendiente | Credenciales y paquete privado enviados | Esperando activación y preflight individual |
| P10 | Karina Galindez | Privado | Activada; acceso a Console confirmado | Sí | Creado; runtime listo | Validada | Aprobado | Preparada localmente; no entregada | Validación end-to-end aprobada desde clon limpio |

## Reglas de asignación

1. Cada persona recibe un código único (`P02`, `P03`, etc.); no se reutiliza durante el workshop.
2. Las identidades OCI P02–P09 ya existen en el *identity domain* del tenant `khipuaimemory`, pertenecen al grupo IAM aprobado y recibieron la solicitud de activación oficial. La entrega anticipada de paquetes y credenciales no incluye tokens ni una sesión OCI autenticada: cada persona todavía debe activar su identidad y crear su propia sesión OCI.
3. La persona se autentica con su propia identidad OCI. La facilitadora no genera ni comparte tokens de seguridad de otra persona.
4. Cada código recibe un usuario temporal ADB distinto y un scope individual `t01:pNN`.
5. El archivo de sesión privado solo contiene configuración local; se distribuye por un canal privado después de asignar la identidad y el usuario ADB.
6. La wallet puede provenir de la misma ADB, pero debe distribuirse únicamente por el canal privado aprobado. Nunca se agrega al repositorio público.
7. El preflight es obligatorio antes de comenzar la ejecución real. Un resultado aprobado no sustituye el preflight de otra laptop o identidad.

## Estructura privada preparada

Para P02 a P10 se prepararon carpetas privadas en `C:\KhipuPrivate\participants\<participant-code>\`:

```text
session\
wallet\
onboarding\
```

Para P02–P10, `onboarding\database-password.dpapi` existe y contiene una contraseña temporal
cifrada mediante DPAPI, accesible solamente con el perfil Windows de facilitación que la creó. No
abrir, copiar ni publicar esos archivos. Los paquetes P02–P09 contienen el wallet y el archivo
final de sesión sin contraseñas. El 30 de octubre de 2026 se entregaron individualmente por correo,
separados del mensaje de credenciales y sin incluir tokens OCI.

## Comunicación inicial

El 30 de octubre de 2026 se envió un correo individual a P02–P09 con copia a la facilitadora. El
mensaje incluyó tenant, región, códigos asignados, repositorio público, guía inicial y solicitud de
confirmación de acceso a OCI. No incluyó wallets, contraseñas, tokens, OCIDs ni archivos privados.

Ese mismo día, después de aprobación explícita, se enviaron dos mensajes privados adicionales a
cada persona P02–P09: uno con sus credenciales ADB y del wallet, y otro con el paquete ZIP asignado.
Se confirmó en Outlook el envío de ocho mensajes de credenciales y ocho mensajes con paquete. La
entrega no sustituye la activación OCI ni el preflight obligatorio desde cada laptop.
