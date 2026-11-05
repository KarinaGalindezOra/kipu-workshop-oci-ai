# Complemento para participantes en macOS y Linux

Primero completa los pasos 0, 1 y 2 de la [Guía del participante](participant_step_by_step.md). Este documento solo aclara las diferencias de macOS y Linux.

## Requisitos locales

- Python 3.11 disponible como `python3.11`.
- Git, si elegiste la alternativa de clonación.
- Un navegador moderno para abrir el dashboard local.
- Tu wallet y archivo privado de sesión entregados por el canal aprobado.

Mantén wallet y archivo de sesión fuera del repositorio. El archivo de sesión no debe contener una contraseña, token, clave privada ni secreto. Cuando sea posible, limita el acceso de lectura del wallet a tu propia cuenta local.

## Activa el entorno virtual

Desde la raíz del repositorio:

```bash
source .venv/bin/activate
```

Cada vez que abras una terminal nueva durante el workshop, vuelve a ejecutar ese comando antes de usar Python.

## Carga la sesión privada

No copies el archivo de sesión dentro del repositorio. Indica su ubicación privada en los comandos del participante:

```bash
python labs/lab02_contract_rag/scripts/validate_environment.py \
  --session-file /private/path/lab02-participant.env \
  --check-db
```

## Abre el dashboard

```bash
python labs/lab02_contract_rag/scripts/run_dashboard.py \
  --session-file /private/path/lab02-participant.env \
  --port 8502
```

Abre `http://127.0.0.1:8502`. El proceso debe permanecer abierto en esa terminal mientras utilizas el dashboard.

## Errores frecuentes

- `python3.11: command not found`: instala Python 3.11 o solicita apoyo antes de continuar.
- `HTTP_401` al consultar: vuelve a autenticar el perfil OCI asignado mediante el procedimiento privado indicado por la facilitación.
- `ORA-01017`: vuelve a ingresar la contraseña asignada de ADB; no cambies schema ni tabla.
- Error de wallet: valida localmente la ruta y el alias de servicio. No compartas el wallet ni el cuerpo del error.
- El dashboard no inicia: confirma que `.venv` está activado, que Python es 3.11, que la ruta del archivo de sesión es correcta y que el puerto 8502 está disponible.
