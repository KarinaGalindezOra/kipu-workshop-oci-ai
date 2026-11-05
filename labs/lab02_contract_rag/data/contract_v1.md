# Contrato de API de desembolsos v1

Versión del contrato: v1

## Endpoint de actualización de estado

Los clientes actualizan un desembolso con `PATCH /v1/disbursements/{disbursement_id}`. El cuerpo de la solicitud usa `payment_status` con uno de estos valores: `PENDING`, `PAID` o `FAILED`.

## Idempotencia

Cada actualización de estado debe incluir el header `X-Idempotency-Key`. Reutilizar una clave con un cuerpo de solicitud diferente devuelve `409 IDEMPOTENCY_CONFLICT`.

## Respuesta

Una actualización de estado exitosa devuelve `200 OK` con `disbursement_id`, `payment_status` y `updated_at`.

## Manejo de errores

Un desembolso desconocido devuelve `404 DISBURSEMENT_NOT_FOUND`. Un estado no válido devuelve `422 INVALID_PAYMENT_STATUS`.
