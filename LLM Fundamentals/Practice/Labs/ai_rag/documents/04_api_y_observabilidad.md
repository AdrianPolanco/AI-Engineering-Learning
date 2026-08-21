# APIs HTTP y Observabilidad

## Diseño de una API

Una API HTTP expone recursos y operaciones mediante endpoints. El diseño debe priorizar contratos claros, semántica HTTP correcta y respuestas consistentes.

Por ejemplo:

GET /users/42

puede recuperar el usuario 42.

POST /users

puede crear un nuevo usuario.

PATCH /users/42

puede modificar parcialmente un usuario.

DELETE /users/42

puede eliminarlo.

## Códigos de estado

200 OK indica una operación exitosa con respuesta.

201 Created indica que se creó un recurso. Cuando es apropiado, la respuesta puede incluir una referencia al nuevo recurso.

204 No Content indica éxito sin contenido de respuesta.

400 Bad Request se utiliza cuando la solicitud no puede procesarse como una solicitud válida.

401 Unauthorized indica que falta autenticación válida o que las credenciales no permiten identificar al cliente.

403 Forbidden indica que el cliente está autenticado pero no tiene autorización para realizar la operación.

404 Not Found indica que el recurso solicitado no existe o no está disponible para ese contexto.

409 Conflict es apropiado cuando la solicitud entra en conflicto con el estado actual del recurso, por ejemplo al intentar registrar un email que debe ser único.

422 Unprocessable Content puede utilizarse cuando la sintaxis de la solicitud es válida pero su contenido no cumple reglas semánticas o de validación, dependiendo del contrato de la API.

500 Internal Server Error representa un error inesperado del servidor.

## Validación

La validación de entrada debe ocurrir antes de ejecutar operaciones de negocio costosas. Los errores de validación deberían devolver una estructura consistente para que los clientes puedan identificar qué campos son inválidos.

Una respuesta de error estructurada puede incluir un título, código de estado, detalle, identificador de trazabilidad y errores específicos por campo.

## Problem Details

RFC 9457 define un formato estándar para representar detalles de problemas HTTP. Problem Details ayuda a evitar que cada endpoint invente una estructura diferente para los errores.

El servidor puede incluir información como type, title, status, detail e instance.

Los detalles internos de excepciones no deberían exponerse directamente al cliente en producción.

## Excepciones

Las excepciones representan situaciones que interrumpen el flujo normal de ejecución. Un exception handler global puede convertir excepciones no controladas en respuestas HTTP consistentes.

No todas las condiciones de negocio necesitan convertirse en excepciones. Si un resultado esperado del dominio es "usuario no encontrado", el diseño puede representar ese resultado explícitamente y traducirlo a 404.

Las excepciones son especialmente útiles para errores inesperados o condiciones que realmente rompen el flujo normal.

## Logging

Los logs deberían contener suficiente contexto para diagnosticar problemas sin almacenar información sensible innecesaria.

El logging estructurado permite consultar propiedades específicas, por ejemplo:

- TraceId
- RequestId
- UserId cuando sea apropiado
- Endpoint
- StatusCode
- Duration
- ExceptionType

Un mensaje de log útil describe qué ocurrió y proporciona contexto para investigarlo.

## Métricas

Las métricas representan mediciones agregadas del comportamiento del sistema.

Ejemplos:

- tasa de solicitudes por segundo;
- latencia;
- porcentaje de errores;
- consumo de CPU;
- memoria utilizada;
- conexiones activas;
- longitud de una cola.

Una métrica como p95 latency indica que el 95% de las solicitudes tuvo una latencia igual o menor al valor observado. El p99 permite observar una cola aún más extrema.

## Tracing

Una traza representa el recorrido de una operación a través de uno o varios componentes.

Una solicitud HTTP puede generar un span en la API, otro span al consultar PostgreSQL y otro al llamar a un servicio externo.

El trace context permite correlacionar estos spans.

## OpenTelemetry

OpenTelemetry proporciona APIs, SDKs y mecanismos de instrumentación para producir telemetría.

Las señales principales son traces, metrics y logs.

Una arquitectura puede enviar la telemetría a un OpenTelemetry Collector, que posteriormente la procesa y exporta a diferentes backends.

Ejemplo:

Application -> OpenTelemetry Collector -> Backend de observabilidad

## Correlación

Cuando una solicitud atraviesa múltiples servicios, un identificador de trazabilidad permite conectar eventos relacionados.

Sin correlación, investigar un error distribuido puede convertirse en buscar una aguja en un pajar mientras cinco servicios producen miles de líneas de logs.

## Principio de diseño

La observabilidad no consiste en almacenar todos los datos posibles. Consiste en recopilar señales suficientes para responder preguntas operativas: qué falló, dónde falló, cuándo ocurrió, cuánto afecta y cuál fue el recorrido de la solicitud.
