# PostgreSQL y Modelado de Datos

## Modelo relacional

Una base de datos relacional representa información mediante tablas compuestas por filas y columnas. Las relaciones entre entidades se expresan mediante claves primarias y foráneas.

Una clave primaria identifica de manera única una fila. Una clave foránea representa una referencia hacia otra entidad.

## Normalización

La normalización reduce la duplicación innecesaria de datos y ayuda a mantener la integridad.

En un diseño normalizado, información que pertenece a una entidad independiente suele almacenarse en su propia tabla. Por ejemplo, un sistema de comercio electrónico puede separar Customer, Order y Product en lugar de repetir toda la información del cliente dentro de cada pedido.

La normalización excesiva tampoco es automáticamente buena. Puede producir demasiadas operaciones de JOIN y complicar determinadas consultas. El diseño debe responder a los patrones reales de acceso.

## Índices

Un índice permite encontrar registros sin recorrer necesariamente toda la tabla. PostgreSQL ofrece diferentes tipos de índices, entre ellos B-tree, Hash, GIN y GiST.

B-tree es el índice general más utilizado y funciona bien para igualdad, rangos y ordenamiento.

GIN es útil para determinados tipos de búsquedas sobre valores compuestos, como arrays, JSONB o búsqueda de texto según el caso.

Un índice tiene un costo: ocupa almacenamiento y debe mantenerse cuando los datos cambian. Crear índices indiscriminadamente puede empeorar INSERT, UPDATE y DELETE.

## Transacciones

Una transacción agrupa operaciones que deben comportarse como una unidad lógica. Las propiedades ACID son Atomicidad, Consistencia, Aislamiento y Durabilidad.

Atomicidad significa que las operaciones de una transacción se confirman juntas o se revierten.

Durabilidad significa que una transacción confirmada debe sobrevivir a fallos según las garantías de almacenamiento configuradas.

## Niveles de aislamiento

El aislamiento controla qué efectos de otras transacciones pueden observarse.

Read Committed es el nivel predeterminado habitual de PostgreSQL y permite que una transacción observe cambios confirmados antes de cada sentencia.

Repeatable Read proporciona una vista consistente durante la transacción.

Serializable ofrece las garantías más fuertes, pero puede provocar conflictos que requieran reintentar transacciones.

## Concurrencia

Dos solicitudes pueden intentar modificar la misma información simultáneamente. El sistema debe utilizar mecanismos apropiados para preservar invariantes.

Por ejemplo, si una cuenta bancaria tiene un saldo de 100 y dos operaciones intentan retirar 80 simultáneamente, una implementación ingenua puede producir un resultado incorrecto. Las transacciones y los mecanismos de bloqueo ayudan a evitar estas condiciones de carrera.

## JSONB

PostgreSQL soporta JSONB para almacenar documentos JSON de forma binaria y consultable. JSONB es útil cuando existe información semiestructurada que no encaja bien en columnas tradicionales.

Sin embargo, utilizar JSONB para absolutamente todo elimina muchas ventajas del modelo relacional. Los datos fundamentales del dominio suelen beneficiarse de columnas tipadas y restricciones explícitas.

## Migraciones

Una migración representa un cambio controlado en el esquema. Las migraciones deberían ser versionadas y reproducibles.

En sistemas en producción, cambiar una columna o eliminar datos puede requerir estrategias compatibles con versiones anteriores de la aplicación. Un despliegue puede necesitar primero agregar una estructura nueva, migrar datos y posteriormente eliminar la estructura antigua.

## Principio de diseño

El esquema debe diseñarse a partir de las reglas del dominio y los patrones de acceso. Una base de datos no es simplemente un lugar donde guardar objetos serializados; también impone restricciones, ofrece concurrencia y protege la integridad de los datos.
