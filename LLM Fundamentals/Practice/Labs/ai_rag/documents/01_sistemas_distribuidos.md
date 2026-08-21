# Sistemas Distribuidos: Fundamentos

## Definición

Un sistema distribuido está compuesto por múltiples procesos o nodos independientes que cooperan mediante una red para ofrecer una capacidad común. A diferencia de una aplicación monolítica ejecutada en un único proceso, los componentes pueden fallar, comunicarse con latencia variable y observar estados diferentes.

## Propiedades importantes

### Latencia de red

Una llamada entre servicios no equivale a una llamada a una función local. Puede existir latencia, pérdida de paquetes, timeouts o interrupciones. Por eso una comunicación entre servicios debe asumir que la red puede fallar.

### Fallos parciales

En un sistema distribuido, un componente puede estar funcionando mientras otro está caído. El sistema completo debe decidir qué hacer cuando una dependencia no responde.

### Consistencia

La consistencia describe qué tan sincronizadas están las observaciones de los datos entre diferentes nodos. La consistencia fuerte facilita el razonamiento, pero puede aumentar el costo de coordinación.

### Disponibilidad

La disponibilidad representa la capacidad del sistema de responder a solicitudes. Una arquitectura puede sacrificar parte de la consistencia inmediata para mantener operaciones disponibles durante ciertos fallos.

## Comunicación síncrona y asíncrona

La comunicación síncrona normalmente utiliza HTTP o gRPC y hace que el consumidor espere una respuesta. Es adecuada cuando necesita conocer inmediatamente el resultado.

La comunicación asíncrona utiliza mecanismos como colas o streams de eventos. El productor publica un mensaje y el consumidor lo procesa posteriormente. Esto desacopla temporalmente los componentes.

## Idempotencia

Una operación idempotente puede ejecutarse varias veces sin producir un efecto final diferente al de ejecutarla una sola vez. La idempotencia es especialmente importante cuando existen reintentos.

Por ejemplo, un endpoint que procesa un pago no debería cobrar dos veces solamente porque el cliente reintentó una solicitud después de un timeout. Una clave de idempotencia puede asociar una solicitud lógica con un resultado ya procesado.

## Timeouts y reintentos

Todo cliente que dependa de una red debería tener límites de tiempo razonables. Un timeout evita esperar indefinidamente.

Los reintentos no deben aplicarse indiscriminadamente. Reintentar una operación de lectura puede ser relativamente seguro si es idempotente. Reintentar una operación que modifica datos puede duplicar efectos si no existe protección.

Un patrón común es utilizar exponential backoff, aumentando progresivamente el intervalo entre intentos.

## Circuit breaker

Un circuit breaker evita continuar enviando solicitudes a una dependencia que está fallando repetidamente. Puede pasar por estados como Closed, Open y Half-Open.

En estado Closed las solicitudes fluyen normalmente. En Open las llamadas se rechazan rápidamente. En Half-Open se permiten algunas solicitudes de prueba para determinar si la dependencia se recuperó.

## Observabilidad

Los sistemas distribuidos requieren logs, métricas y trazas. Una métrica puede indicar que la latencia aumentó, un log puede explicar un error concreto y una traza puede mostrar cómo una solicitud recorrió múltiples servicios.

OpenTelemetry permite instrumentar aplicaciones para producir señales de observabilidad de forma estandarizada.

## Principio de diseño

Un buen diseño distribuido no intenta eliminar todos los fallos. Intenta hacer que los fallos sean detectables, limitados y recuperables.
