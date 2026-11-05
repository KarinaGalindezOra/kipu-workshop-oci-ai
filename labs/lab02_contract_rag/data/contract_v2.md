# Contrato de API de desembolsos v2

Versión del contrato: v2

## Endpoint de estado de liquidación

Los clientes actualizan el estado de liquidación con `PUT /v2/disbursements/{disbursement_id}/status`. El cuerpo de la solicitud usa `status` con uno de estos valores: `PROCESSING`, `SETTLED` o `REJECTED`.

## Idempotencia

Cada actualización de estado debe incluir el header `Idempotency-Key`. Reutilizar una clave con un cuerpo de solicitud diferente devuelve `409 IDEMPOTENCY_MISMATCH`.

## Respuesta

Una actualización de estado exitosa devuelve `200 OK` con `disbursement_id`, `status`, `status_changed_at` y `contract_version` igual a `v2`.

## Migración desde v1

El endpoint de v1 y el campo `payment_status` no son aceptados por v2. Los clientes deben llamar al endpoint de estado de liquidación de v2, renombrar `payment_status` a `status` y mapear `PAID` a `SETTLED`, `PENDING` a `PROCESSING` y `FAILED` a `REJECTED`.

## Manejo de errores

Un desembolso desconocido devuelve `404 DISBURSEMENT_NOT_FOUND`. Un estado no válido devuelve `422 INVALID_STATUS`.
