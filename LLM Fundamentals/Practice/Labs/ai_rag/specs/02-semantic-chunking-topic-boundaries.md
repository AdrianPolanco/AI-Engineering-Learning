# SPEC 02 — Semantic chunking por frontera temática (reescritura)

> **Status:** Implemented
> **Depends on:** SPEC 01
> **Date:** 2026-09-05
> **Objective:** Reescribir `SemanticChunkingStrategy` para que cada chunk sea un grupo de frases delimitado únicamente por una frontera semántica detectada, usando `max_chunk_size` solo como tope de seguridad y fusionando temas por debajo de `min_chunk_size`, en vez de trocear cada tema por tamaño de caracteres como hace hoy.

## Why this spec exists

Spec 01 implementó `SemanticChunkingStrategy` detectando fronteras semánticas por percentil de
distancia coseno entre frases — eso funciona correctamente. Pero, dentro de cada grupo detectado,
vuelve a aplicar el ventaneo por tamaño de `RecursiveChunkingStrategy` (`merge_windows`/
`split_fragments`, incluido su fallback de trocear por palabra y luego por carácter). Con
`labs/lab_3_1_faiss.py` usando `SemanticChunkerConfig(5, 2)` (5 **caracteres**, arrastrado del
patrón usado para `SentenceChunkerConfig`, que sí cuenta frases), ese ventaneo degrada cada tema en
chunks de una palabra o menos — justo el síntoma reportado. Incluso con un `chunk_size` razonable,
el diseño actual sigue re-fragmentando un tema coherente en varias ventanas desconectadas, lo cual
contradice el propósito de un chunker "semántico": agrupar por tema, no por tamaño. Este spec
redefine el contrato: un chunk es un tema completo delimitado solo por la frontera detectada; el
tamaño deja de ser un objetivo de ventaneo y pasa a ser una salvaguarda para temas patológicamente
largos.

## Scope

**In:**

- Reescritura de `SemanticChunkerConfig` en `src/ai_rag/domain/chunk_config.py`: nuevos campos
  `max_chunk_size`, `min_chunk_size`, `overlap_size`, `breakpoint_percentile_threshold` (default
  `95.0`, sin cambios), con su validación.
- Reescritura del algoritmo de `SemanticChunkingStrategy` en
  `src/ai_rag/ingestion/chunking/strategies/semantic_chunking.py` según el contrato de abajo.
- Reutilización sin cambios de `src/ai_rag/ingestion/chunking/text_windowing.py`
  (`split_fragments`, `merge_windows`, `seed_overlap`, `build_heading_prefix`), invocando
  `merge_windows`/`split_fragments` solo cuando: (a) una frase individual supera `max_chunk_size`
  por sí sola, o (b) un tema ya fusionado supera `max_chunk_size` en conjunto.
- Corrección de `labs/lab_3_1_faiss.py`: su `SemanticChunkerConfig(5, 2)` pasa a usar los nuevos
  campos con valores razonables.
- Reescritura de `tests/domain/test_chunk_config.py` (casos de `SemanticChunkerConfig`) y de
  `tests/chunkers/strategies/test_semantic_chunking.py` para el nuevo contrato.

**Out of scope (for future specs):**

- El factory/registro `DocumentExtension` → estrategia (mismo pendiente que spec 01).
- Un splitter de frases compartido entre `SentenceChunkingStrategy` y `SemanticChunkingStrategy`.
- Chunking basado en tokens.
- Añadir `heading_path` a `ChunkMetadata`.
- Añadir `get_config` al ABC `ChunkingStrategy`.
- Cambiar el método de detección de frontera (sigue siendo percentil de distancia coseno frase a
  frase; no se introduce ventana deslizante ni umbral fijo).
- Cualquier cambio a `EmbeddingService`, `SentenceEmbedder`, `RecursiveChunkingStrategy`,
  `SentenceChunkingStrategy` o a las firmas/comportamiento de `text_windowing.py`.
- Cualquier cosa en `vector_store/`, `retrieval/`, `generation/` o `rag/`.

## Data model

`SemanticChunkerConfig` reemplaza sus campos actuales (`chunk_size`, `chunk_overlap`) — cambio
incompatible respecto a spec 01:

```python
MIN_MAX_CHUNK_SIZE_MESSAGE = 'max_chunk_size must be at least 1'
MIN_MIN_CHUNK_SIZE_MESSAGE = 'min_chunk_size must be at least 1'
MIN_CHUNK_SIZE_NOT_LESS_THAN_MAX_MESSAGE = 'min_chunk_size must be less than max_chunk_size'
MIN_OVERLAP_SIZE_MESSAGE = 'overlap_size must not be negative'
OVERLAP_NOT_LESS_THAN_MAX_MESSAGE = 'overlap_size must be less than max_chunk_size'
INVALID_BREAKPOINT_PERCENTILE_MESSAGE = 'breakpoint_percentile_threshold must be between 0 and 100'

@dataclass(frozen=True)
class SemanticChunkerConfig:
    max_chunk_size: int                            # >= 1; tope de seguridad, no objetivo de ventaneo
    min_chunk_size: int                            # >= 1 y < max_chunk_size; umbral de fusión de temas
    overlap_size: int                              # >= 0 y < max_chunk_size
    breakpoint_percentile_threshold: float = 95.0  # 0..100, igual que en spec 01
```

Valores por defecto recomendados para uso real (caracteres): `max_chunk_size=1200`,
`min_chunk_size=200`, `overlap_size=100`.

`Chunk`, `ChunkMetadata`, `text_windowing.py` y el `SentenceEmbedder` `Protocol` no cambian.

### Algorithm contract

Para cada `DocumentBlock` del documento, en orden:

1. **Split de frases.** Igual que spec 01: separar `block.text` por `'.'`, strip, reanexar el
   separador (contenido preservado al re-unir).
2. **Detección de frontera.** Igual que spec 01: con 0 o 1 frase, un único grupo crudo. Si no,
   `embedder.embed_many(...)`, `distance[i] = 1 - similarity(embedding[i], embedding[i+1])`,
   `threshold = numpy.percentile(distance, breakpoint_percentile_threshold)`; hay frontera tras la
   frase `i` cuando `distance[i] > threshold`. Esto particiona las frases en grupos crudos
   contiguos.
3. **Fusión de temas diminutos (nuevo).** Recorrer los grupos crudos de izquierda a derecha,
   acumulando grupos consecutivos en un "tema" mientras su longitud total de contenido sea menor
   que `min_chunk_size` y exista un grupo siguiente. Si el tema final del bloque sigue por debajo
   de `min_chunk_size` tras esto y ya existe un tema anterior cerrado, se fusiona hacia atrás con
   ese tema anterior (única excepción: fusión hacia atrás solo para el último tema del bloque). Un
   bloque con un único grupo crudo no se ve afectado por este paso.
4. **Emisión por tema.** Para cada tema resultante, en orden:
   - Si la longitud total de su contenido cabe en el `budget` (`max_chunk_size` menos el prefijo de
     heading, mismo cálculo y misma degradación de spec 01 cuando el prefijo no cabe), el tema
     entero es una única ventana — `merge_windows`/`split_fragments` **no** se invocan.
   - Si el tema supera el `budget`: expandir cualquier frase individual más larga que el `budget`
     vía `text_windowing.split_fragments(sentence, (' ', ''), budget)` (fallback sin cambios),
     luego partir las frases del tema en ventanas de tamaño acotado con
     `text_windowing.merge_windows(fragments, budget, effective_overlap)` — igual que spec 01 hacía
     por cada grupo, pero ahora solo se dispara cuando el tema desborda el tope.
5. **Overlap entre chunks.** Salvo la primera ventana del primer tema del bloque, cada ventana se
   antepone con `text_windowing.seed_overlap(ventana_anterior, effective_overlap)` — igual mecanismo
   que spec 01, ahora usado tanto entre temas distintos como entre los trozos de un mismo tema
   partido por el tope de tamaño.
6. **Texto del chunk** = `prefix + ''.join(window).strip()`, misma regla de degradación de prefijo
   sobredimensionado que spec 01. Una ventana cuyo cuerpo quede vacío no emite chunk.

## Implementation plan

1. **Config rewrite.** Reemplazar los campos de `SemanticChunkerConfig` en
   `src/ai_rag/domain/chunk_config.py` por `max_chunk_size`/`min_chunk_size`/`overlap_size`/
   `breakpoint_percentile_threshold`, con sus seis constantes de mensaje y `__post_init__`.
   Reescribir los casos de `SemanticChunkerConfig` en `tests/domain/test_chunk_config.py`
   (rechazo y aceptación parametrizados) para los nuevos campos.
   Verify: `uv run pytest tests/domain`.

2. **Fusión de temas diminutos.** En `semantic_chunking.py`, añadir el paso de fusión (paso 3 del
   contrato) tras la detección de fronteras: acumula grupos crudos consecutivos hasta alcanzar
   `min_chunk_size`, con la excepción de fusión hacia atrás para el último tema del bloque.

3. **Emisión condicional por tema.** Reemplazar el ventaneo incondicional actual (`merge_windows`
   siempre) por la emisión condicional del paso 4 del contrato: un único chunk cuando el tema cabe
   en el `budget`, ventaneo por tamaño solo cuando lo desborda. El puente de overlap entre chunks
   (paso 5) se mantiene para ambos casos.

4. **Lab script.** Corregir `labs/lab_3_1_faiss.py`: cambiar
   `SemanticChunkerConfig(5, 2)` por los nuevos campos con valores no absurdos (p. ej.
   `max_chunk_size=1200, min_chunk_size=200, overlap_size=100`).

5. **Tests.** Reescribir `tests/chunkers/strategies/test_semantic_chunking.py` para el nuevo
   contrato. Cubrir: el documento de dos clusters (igual que spec 01) produce exactamente 2 chunks,
   uno por cluster, sin ventanear cada uno por tamaño; un tema cuyo contenido combinado supera
   `max_chunk_size` sí se parte en varias ventanas de tamaño acotado con overlap entre ellas; dos
   grupos crudos adyacentes por debajo de `min_chunk_size` se funden en un solo chunk; un grupo
   crudo final diminuto se funde hacia atrás con el tema anterior; una frase individual más larga
   que `max_chunk_size` sigue degradando a palabra/carácter; ningún chunk queda vacío o solo con
   espacios; ninguna frase se pierde o reordena; prefijo de heading markdown y su degradación por
   sobredimensión se mantienen; `set_config` sigue rechazando `RecursiveChunkerConfig`/
   `SentenceChunkerConfig`.
   Verify: `uv run pytest`.

## Acceptance criteria

- [x] `SemanticChunkerConfig(0, 1, 0)`, `(10, 0, 0)`, `(10, 10, 0)`, `(10, 5, 10)`, `(10, 5, -1)` y
      `(10, 5, 2, breakpoint_percentile_threshold=101)` cada uno lanza `ValueError` con la
      constante de mensaje correspondiente.
- [x] Para el documento de dos clusters (`FakeEmbedder`, igual que spec 01) con `max_chunk_size`
      suficiente para contener cada cluster entero, `SemanticChunkingStrategy` devuelve exactamente
      2 chunks — uno por cluster — no uno por frase ni uno por palabra.
- [x] Cada uno de esos 2 chunks contiene todas las frases de su cluster sin partir por tamaño.
- [x] El segundo chunk empieza con la última frase del primer cluster (overlap puenteando la
      frontera entre temas).
- [x] Un tema cuyas frases combinadas superan `max_chunk_size` se parte en varios chunks, cada uno
      `<= max_chunk_size`, y los consecutivos comparten un overlap `<= overlap_size`.
- [x] Dos grupos crudos adyacentes cuyo contenido combinado está por debajo de `min_chunk_size` se
      emiten como un único chunk, no como dos.
- [x] Un grupo crudo diminuto al final de un bloque se funde con el tema anterior en vez de quedar
      como chunk propio.
- [x] Una frase individual más larga que `max_chunk_size` (ajustado por el prefijo) sigue
      degradando a división por palabra y luego por carácter, igual que `RecursiveChunkingStrategy`.
- [x] Todas las frases del bloque original aparecen, en el orden de origen, a lo largo de los
      chunks devueltos.
- [x] Ningún chunk tiene texto vacío o solo espacios.
- [x] Chunks de un bloque con `heading_path=('Vacaciones', 'Solicitud')` empiezan con
      `'Vacaciones > Solicitud\n\n'`, degradando a sin prefijo cuando no cabe en `max_chunk_size`.
- [x] `SemanticChunkingStrategy.set_config(RecursiveChunkerConfig(10, 2))` y
      `set_config(SentenceChunkerConfig(4, 2))` siguen lanzando `TypeError`.
- [x] `labs/lab_3_1_faiss.py` ya no instancia `SemanticChunkerConfig` con valores de 5 caracteres;
      usa los nuevos campos con valores que no fragmentan por palabra.
- [x] `uv run pytest` pasa completo.

## Decisions

- **Yes:** reescribir `SemanticChunkingStrategy` in-place, rompiendo el contrato de spec 01. El
  nombre y propósito del chunker es agrupar por tema; el diseño anterior no lo cumplía.
- **No:** crear una estrategia paralela (`TopicChunkingStrategy`). Dejaría conviviendo dos
  "semantic chunkers", uno de ellos roto.
- **Yes:** `max_chunk_size` como tope de seguridad (soft cap), no como objetivo de ventaneo. Un
  tema por debajo del tope es siempre un único chunk, sin importar su tamaño.
- **No:** dejar temas sin tope alguno. Un único tema de varias páginas produciría un chunk de
  tamaño ilimitado, malo para embeddings y para retrieval.
- **Yes:** fusionar grupos por debajo de `min_chunk_size` con el grupo siguiente. Evita el extremo
  opuesto: chunks de una frase de pocas palabras cada uno.
- **Yes:** excepción de fusión hacia atrás para el último grupo del bloque. Sin ella, un bloque
  podría terminar en un chunk final minúsculo sin ningún "siguiente" con quien fusionarse.
- **Yes:** mantener la detección de frontera por percentil de distancia coseno. Ya funciona (spec
  01 la verifica); el problema reportado no era la detección, sino qué se hacía después de
  detectarla.
- **Yes:** renombrar `chunk_size`/`chunk_overlap` a `max_chunk_size`/`min_chunk_size`/
  `overlap_size`. Nombres distintos dejan explícito que ya no es ventaneo estricto, evitando repetir
  la confusión que causó este bug (`SemanticChunkerConfig(5, 2)` tratado como si `5` fueran frases,
  cuando el campo son caracteres).
- **Yes:** unidad en caracteres (no en número de frases) para `max_chunk_size`/`min_chunk_size`/
  `overlap_size`. Consistente con `RecursiveChunkerConfig`/`chunk_size` actual y con el resto del
  pipeline.
- **Yes:** reutilizar `text_windowing.merge_windows`/`split_fragments`/`seed_overlap` sin cambiar
  sus firmas, invocándolos solo cuando un tema fusionado supera `max_chunk_size` o una frase
  individual lo supera por sí sola. Reduce el diff y conserva lógica ya probada por spec 01.
- **Yes:** el overlap sigue existiendo, pero solo como puente entre chunks consecutivos — entre
  temas distintos, y entre los trozos de un mismo tema partido por el tope de tamaño. No hay
  ventaneo interno incondicional que lo necesite de otra forma.
- **Yes:** corregir `labs/lab_3_1_faiss.py` en este mismo spec. Es el script que reprodujo el bug
  reportado; dejarlo con valores absurdos invitaría a repetir la misma confusión.
- **No:** cambiar el método de detección de frontera (percentil) por un umbral fijo o una ventana
  deslizante de varias frases. Fuera de alcance — no es el problema reportado.

## Risks

| Risk | Mitigation |
| --- | --- |
| Un bloque muy corto cabe entero por debajo de `min_chunk_size` y de `max_chunk_size` a la vez. | Con un único grupo crudo no hay fusión que hacer; el bloque entero es un único chunk, igual que hoy con documentos de una sola frase. |
| Fusionar hacia adelante puede encadenar varios grupos pequeños en un tema desproporcionadamente grande frente a sus vecinos. | Aceptado por diseño: `min_chunk_size` es un umbral de corte, no un objetivo de tamaño; la fusión se detiene en cuanto se alcanza. |
| `merge_windows`/`split_fragments` pasan de invocarse siempre a invocarse condicionalmente, añadiendo ramas nuevas al código. | Cubierto explícitamente en el plan de tests: caso de tema que cabe entero vs. caso de tema que desborda el tope. |
| Los tests y la config de spec 01 para `SemanticChunkerConfig`/`SemanticChunkingStrategy` dejan de compilar (campos renombrados). | Se reescriben en los pasos 1 y 5 del plan de implementación; no quedan tests usando `chunk_size`/`chunk_overlap` para esta config. |

## What is **not** in this spec

- El factory/registro `DocumentExtension` (u otro criterio) → estrategia de chunking.
- Un sentence-splitter compartido entre `SentenceChunkingStrategy` y `SemanticChunkingStrategy`.
- Chunking basado en tokens.
- `heading_path` como campo de `ChunkMetadata`.
- `get_config` en el ABC `ChunkingStrategy`.
- Cambiar el método de detección de frontera semántica (el percentil se mantiene).
- Cambios a `EmbeddingService`, `SentenceEmbedder`, `RecursiveChunkingStrategy`,
  `SentenceChunkingStrategy` o a `text_windowing.py`.
- Cualquier cosa en `vector_store/`, `retrieval/`, `generation/` o `rag/`.

Each one of those, if it lands, goes in its own spec.
