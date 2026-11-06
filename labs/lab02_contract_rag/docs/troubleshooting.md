# Resolución de problemas para participantes

| Situación | Qué hacer |
|---|---|
| Python no es 3.11 | Detente y solicita apoyo antes de instalar dependencias. |
| El entorno virtual no está activo | Activa `.venv` y vuelve a ejecutar el comando. |
| El dashboard no inicia | Confirma la instalación y la sesión privada. Si `8502` ya está ocupado por otro dashboard local, ciérralo o usa `--port 8503` y abre `http://127.0.0.1:8503`. |
| La consulta informa que la calibración no coincide con el espacio de embeddings | No ejecutes la consulta. Después de una ingesta OCI exitosa, ejecuta `python labs/lab02_contract_rag/scripts/calibrate_participant.py --confirm-live-inference`. Este paso usa preguntas sintéticas de desarrollo y escribe una calibración privada compatible. |
| La traza falla en `adb_connection_acquire` antes de embeddings o chat | No registres la ejecución como una respuesta del modelo. Cierra el dashboard para liberar su pool local, vuelve a cargar tu sesión privada y ejecuta `python labs/lab02_contract_rag/scripts/validate_environment.py --check-db`. Si el estado no es `passed`, informa únicamente el código seguro a la facilitación. |
| Error de wallet o conexión ADB | Verifica localmente la ruta entregada. No compartas archivos wallet ni mensajes completos de error. |
| `ORA-01017` | Vuelve a ingresar la contraseña asignada de ADB. No cambies schema ni tabla. |
| `HTTP_401` de OCI | Sigue el procedimiento privado de reautenticación entregado por la facilitación. No copies tokens ni perfiles de otras personas. |
| La pregunta no tiene versión | El resultado correcto es `needs_clarification`; selecciona una versión antes de continuar. |
| No hay respaldo en el contrato | El resultado correcto es `insufficient_evidence`; no inventes una respuesta. |
| Una operación OCI falla | Conserva el estado observado y avisa a la facilitación. No uses una respuesta local, simulada o de otra persona como reemplazo. |

## Reglas de seguridad

- No compartas contraseñas, tokens, wallets, archivos de sesión ni trazas completas de error.
- No uses credenciales, reportes ni dashboard de otra persona.
- No modifiques tu schema, tabla, modelo ni región para intentar corregir un fallo.
- El dashboard escucha solo en `127.0.0.1`; no lo expongas a Internet.

## Qué informar al pedir ayuda

Indica el paso de esta guía que estabas ejecutando, el nombre seguro de la etapa mostrada por el dashboard y la hora aproximada. No envíes secretos ni contenido de archivos privados.
