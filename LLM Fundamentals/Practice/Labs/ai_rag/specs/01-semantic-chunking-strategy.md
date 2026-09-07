# SPEC 01 — SemanticChunkingStrategy

> **Status:** Approved
> **Depends on:** —
> **Date:** 2026-09-05
> **Objective:** Implement `SemanticChunkingStrategy`, a chunking strategy that groups sentences by cosine-distance breakpoints from an injected `SentenceEmbedder` (satisfied by `EmbeddingService`) and enforces `chunk_size`/`chunk_overlap` limits on the resulting groups, as a third alternative alongside `RecursiveChunkingStrategy` and `SentenceChunkingStrategy`.

## Why this spec exists

This is the first chunking strategy that depends on embeddings rather than pure text splitting.
`EmbeddingService` currently has a bug (`get_model_info()` calls a method that does not exist on
`SentenceTransformer`) and no seam for injecting a fake in tests, so both are fixed here as part of
making it usable by a strategy. It also generalizes `RecursiveChunkingStrategy`'s size/overlap
windowing logic — which this strategy needs a second time, inside each semantic group — into a
shared module instead of duplicating it, and it deliberately treats a detected semantic boundary as
a hard chunk boundary: groups are never merged back together to fill `chunk_size`, only bridged by
the configured overlap.

## Scope

**In:**

- `SemanticChunkerConfig` in `src/ai_rag/domain/chunk_config.py`, validated like
  `RecursiveChunkerConfig` plus a bounded `breakpoint_percentile_threshold`.
- A `SentenceEmbedder` `Protocol` in `src/ai_rag/embeddings/sentence_embedder.py`
  (`embed_many` + `similarity`), re-exported from `src/ai_rag/embeddings/__init__.py`.
- Fixing `EmbeddingService.get_model_info()` (`get_embedding_dimension` → `get_sentence_embedding_dimension`)
  and adding `EmbeddingService.similarity(a, b) -> float` (cosine similarity), so `EmbeddingService`
  satisfies `SentenceEmbedder` structurally.
- Extracting the size/overlap windowing helpers currently private to `RecursiveChunkingStrategy`
  (`_build_prefix`, `_split_fragments`, `_merge_windows`, `_seed_overlap`) into a shared module
  `src/ai_rag/ingestion/chunking/text_windowing.py`, with `RecursiveChunkingStrategy` refactored to
  use them. Behavior-preserving, its own commit.
- The full implementation of `SemanticChunkingStrategy` in
  `src/ai_rag/ingestion/chunking/strategies/semantic_chunking.py`.
- Tests for all of the above under `tests/`.

**Out of scope (for future specs):**

- Any factory or registry wiring `DocumentExtension` (or any other criterion) to a chunking
  strategy — same open item left by spec 01 for `RecursiveChunkingStrategy`.
- A shared sentence-splitting helper between `SentenceChunkingStrategy` and
  `SemanticChunkingStrategy`. Each keeps its own private split, matching the existing pattern.
- Token-based chunk sizing.
- Adding `heading_path` as a field on `ChunkMetadata`.
- Adding `get_config` to the `ChunkingStrategy` ABC.
- Using `EmbeddingService.similarity` or `SemanticChunkingStrategy` anywhere in retrieval/search.
- Any change to `Chunker`, `DocumentLoader`, the pre-processors, or the `vector_store` / `retrieval`
  / `generation` / `rag` layers that do not exist yet.

## Data model

New `SemanticChunkerConfig` (values in **characters**, threshold in percentile points):

```python
MIN_CHUNK_SIZE_MESSAGE = 'chunk_size must be at least 1'
MIN_CHUNK_OVERLAP_MESSAGE = 'chunk_overlap must not be negative'
OVERLAP_NOT_LESS_THAN_SIZE_MESSAGE = 'chunk_overlap must be less than chunk_size'
INVALID_BREAKPOINT_PERCENTILE_MESSAGE = 'breakpoint_percentile_threshold must be between 0 and 100'

@dataclass(frozen=True)
class SemanticChunkerConfig:
    chunk_size: int                                # >= 1
    chunk_overlap: int                             # >= 0 and < chunk_size
    breakpoint_percentile_threshold: float = 95.0  # 0..100
```

New `SentenceEmbedder` `Protocol` (`src/ai_rag/embeddings/sentence_embedder.py`) — the seam that
lets tests inject a fake instead of a real `SentenceTransformer`:

```python
class SentenceEmbedder(Protocol):
    def embed_many(self, texts: list[str]) -> np.ndarray: ...
    def similarity(self, a: np.ndarray, b: np.ndarray) -> float: ...
```

`EmbeddingService` gains `similarity` and satisfies `SentenceEmbedder` structurally (no inheritance
needed):

```python
def similarity(self, a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
```

`text_windowing.py` (new module, extracted from `recursive_chunking.py`, no behavior change):

```python
HEADING_JOINER = ' > '
HEADING_BODY_SEPARATOR = '\n\n'

def build_heading_prefix(heading_path: tuple[str, ...]) -> str: ...
def split_fragments(text: str, separators: tuple[str, ...], budget: int) -> list[str]: ...
def merge_windows(fragments: list[str], budget: int, effective_overlap: int) -> list[list[str]]: ...
def seed_overlap(window: list[str], effective_overlap: int) -> list[str]: ...
```

`Chunk` and `ChunkMetadata` are unchanged. Chunk ids and indices follow the existing convention:
`f'{document_id}-chunk-{index}'`, `index` starting at `1` and continuous across all blocks.

### Algorithm contract

For each `DocumentBlock` of the document, in order:

1. Split `block.text` into sentence fragments the same way `SentenceChunkingStrategy` does
   (split on `'.'`, strip, re-append `'.'`), keeping the trailing separator attached to each piece
   (`'. '` for every sentence but the last, `'.'` for the last) so fragments are content-preserving
   when re-joined.
2. If there are 0 or 1 sentences, there is a single semantic group — no distance to compute.
   Otherwise: embed the stripped sentence texts with `embedder.embed_many(...)`, compute
   `distance[i] = 1 - embedder.similarity(embedding[i], embedding[i + 1])` for each consecutive
   pair, and set `threshold = numpy.percentile(distance, config.breakpoint_percentile_threshold)`.
   A semantic boundary falls right after sentence `i` whenever `distance[i] > threshold`. This
   partitions the sentence fragments into contiguous groups.
3. For each group, in order: expand any single sentence fragment longer than `budget`
   (`chunk_size` minus heading prefix, same reduced-budget rule as `RecursiveChunkingStrategy`) via
   `text_windowing.split_fragments(sentence, (' ', ''), budget)`, then merge the group's fragments
   into windows with `text_windowing.merge_windows(fragments, budget, effective_overlap)`. This
   enforces `chunk_size`/`chunk_overlap` **within** the group exactly as `RecursiveChunkingStrategy` does.
4. Except for the first group, seed the first window of the group with
   `text_windowing.seed_overlap(last_window_of_previous_group, effective_overlap)` prepended to its
   fragments, before joining to text. This carries the configured overlap **across** a semantic
   boundary too, instead of every group starting cold.
5. Chunk text is `prefix + ''.join(window).strip()`, same prefix/budget rule (and the same
   oversized-prefix degradation) as `RecursiveChunkingStrategy`. A window whose body strips to
   empty emits no chunk.

## Implementation plan

1. **Config validation.** Add `SemanticChunkerConfig` with its four message constants and
   `__post_init__` to `src/ai_rag/domain/chunk_config.py`, mirroring `RecursiveChunkerConfig`'s
   style plus the `breakpoint_percentile_threshold` bound check. Add parametrized rejection and
   acceptance cases to `tests/domain/test_chunk_config.py`.
   Verify: `uv run pytest tests/domain`.

2. **Extract the shared windowing helpers.** Move `_build_prefix` (public `build_heading_prefix`),
   `_split_fragments` (public `split_fragments`), `_merge_windows` (public `merge_windows`) and
   `_seed_overlap` (public `seed_overlap`) out of `recursive_chunking.py` into
   `src/ai_rag/ingestion/chunking/text_windowing.py`. Update `RecursiveChunkingStrategy` to import
   them. No behavior change — its own commit. `tests/chunkers/strategies/test_recursive_chunking.py`
   must still pass, with only its `HEADING_BODY_SEPARATOR` import path updated to `text_windowing`.
   Verify: `uv run pytest`.

3. **EmbeddingService fixes.** In `src/ai_rag/embeddings/embedding_service.py`, fix
   `get_model_info()` to call `get_sentence_embedding_dimension()`, and add
   `similarity(a: np.ndarray, b: np.ndarray) -> float` (cosine similarity). Add
   `tests/embeddings/test_embedding_service.py`, monkeypatching `SentenceTransformer` with a
   lightweight fake so the suite never downloads a real model. Cover: `get_model_info()` returns
   the fake's dimension without raising; `similarity` returns `1.0` for identical vectors.
   Verify: `uv run pytest tests/embeddings`.

4. **SentenceEmbedder protocol.** Add `src/ai_rag/embeddings/sentence_embedder.py` with the
   `SentenceEmbedder` `Protocol` (`embed_many`, `similarity`). Export it from
   `src/ai_rag/embeddings/__init__.py` alongside `EmbeddingService`.

5. **SemanticChunkingStrategy.** Implement
   `src/ai_rag/ingestion/chunking/strategies/semantic_chunking.py` per the algorithm contract:
   `__init__(config: SemanticChunkerConfig, embedder: SentenceEmbedder)`, `set_config` (raising
   `TypeError` for any other config type), `get_config`, the private sentence split, breakpoint
   detection, and per-group windowing built on `text_windowing`. Update
   `ChunkingStrategy.set_config`'s type hints (`chunking_strategy.py`) to include
   `SemanticChunkerConfig`.

6. **Tests.** Add `tests/chunkers/strategies/test_semantic_chunking.py` with a small `FakeEmbedder`
   (implements `SentenceEmbedder`, returns hand-picked vectors so specific sentence pairs are
   deliberately close or far apart). Cover: chunks respect `chunk_size`; consecutive chunks share
   up to `chunk_overlap` characters, including across a forced semantic boundary; no sentence is
   lost or reordered; the boundary lands where the fake's vectors are farthest apart; markdown
   heading prefix and its oversized-prefix degradation, mirroring `RecursiveChunkingStrategy`'s
   tests; `set_config` rejects `RecursiveChunkerConfig`/`SentenceChunkerConfig`.
   Verify: `uv run pytest`.

## Acceptance criteria

- [ ] `SemanticChunkerConfig(0, 0)`, `(10, -1)`, `(10, 10)`, `(10, 20)` and
      `(10, 2, breakpoint_percentile_threshold=101)` each raise `ValueError` with the matching
      message constant.
- [ ] `EmbeddingService.get_model_info()` no longer raises `AttributeError` — it calls
      `get_sentence_embedding_dimension()`.
- [ ] `EmbeddingService.similarity(v, v)` returns `1.0` for any non-zero vector `v`.
- [ ] `EmbeddingService` satisfies the `SentenceEmbedder` `Protocol` structurally (no inheritance).
- [ ] `uv run pytest` passes, and `tests/chunkers/strategies/test_sentence_chunking.py` is
      byte-identical to its current version.
- [ ] For a `FakeEmbedder` with two clusters of close vectors, `SemanticChunkingStrategy` places
      the chunk boundary exactly between the two clusters.
- [ ] For every produced chunk, `len(chunk.text) <= config.chunk_size`.
- [ ] For two consecutive chunks of the same block, the second chunk's body starts with a
      non-empty suffix of the first chunk's body of length `<= config.chunk_overlap`, whenever the
      first chunk was built from more than one sentence fragment — including when the two chunks
      fall on opposite sides of a semantic boundary.
- [ ] Every sentence of the source block appears, in source order, across the returned chunks.
- [ ] Chunks from a block with `heading_path=('Vacaciones', 'Solicitud')` all start with
      `'Vacaciones > Solicitud\n\n'`, and degrade to no prefix when it does not fit in `chunk_size`.
- [ ] `SemanticChunkingStrategy.set_config(RecursiveChunkerConfig(10, 2))` and
      `set_config(SentenceChunkerConfig(4, 2))` both raise `TypeError`.
- [ ] No chunk has empty or whitespace-only text.
- [ ] No test in the suite downloads or loads a real `SentenceTransformer` model.

## Decisions

- **Yes:** sentence-level analysis (split on `'.'`, same as `SentenceChunkingStrategy`). It is the
  standard unit for semantic chunking and reuses an already-validated split pattern instead of
  inventing a new one.
- **No:** analyzing whole `DocumentBlock`s. Too coarse — a block can span an entire section.
- **Yes:** percentile-of-distance breakpoint detection (`breakpoint_percentile_threshold`, default
  `95.0`), over a fixed similarity threshold. It adapts to each document's own distribution instead
  of a hand-tuned number that would need recalibration per domain.
- **Yes:** `chunk_size`/`chunk_overlap` in **characters**, matching `RecursiveChunkerConfig`. Gives
  real control over the resulting chunk size and stays comparable across strategies.
- **Yes:** fixing `EmbeddingService.get_model_info()`'s `get_embedding_dimension` bug here. The
  file is already being touched to add `similarity`; leaving a known `AttributeError` in place
  would be worse than fixing it in the same change.
- **Yes:** `similarity(a, b)` lives on `EmbeddingService`, not inlined in the strategy. It is a
  general embedding-space operation that retrieval will also need later.
- **Yes:** a `SentenceEmbedder` `Protocol` + a `FakeEmbedder` in tests, instead of exercising a
  real `SentenceTransformer`. Keeps `SemanticChunkingStrategy`'s tests fast and deterministic; the
  real model's behavior is not what these tests are meant to verify.
- **Yes:** processing per `DocumentBlock`, not the whole document concatenated. Consistent with
  `RecursiveChunkingStrategy`/`SentenceChunkingStrategy`; does not blur the boundary between two
  markdown sections that already have distinct `heading_path`s.
- **No:** a shared sentence-splitting helper across `SentenceChunkingStrategy` and
  `SemanticChunkingStrategy`. The repo's existing pattern is that each strategy owns its own
  splitting unit; extracting it now would be a separate, narrower refactor than this spec's scope.
- **Yes:** extracting `text_windowing.py` out of `RecursiveChunkingStrategy`. Its size/overlap
  windowing logic was about to be needed a second time (within each semantic group); duplicating
  it again would triplicate already-fiddly logic.
- **Yes:** overlap carried across a semantic boundary via an explicit `seed_overlap` prepend
  between groups, rather than generalizing `merge_windows` with a "forced break" parameter. Keeps
  `merge_windows` unchanged and easy to reason about; the cross-group seam is a single explicit
  step instead of a signature change to already-tested code.
- **No:** merging small semantic groups together to fill `chunk_size`. That would erase the point
  of detecting a breakpoint — a group boundary is a hard chunk boundary, only bridged by the
  configured overlap.
- **No:** the extension→strategy factory/registry. Same open item as spec 01 for
  `RecursiveChunkingStrategy` — still pending, decided together with all three strategies at once.

## Risks

| Risk | Mitigation |
| --- | --- |
| `numpy.percentile` over 0 or 1 distances (a block with <= 2 sentences) is degenerate. | Blocks with 0 or 1 sentence skip distance/percentile entirely and form a single semantic group. |
| A real `SentenceTransformer` download makes tests slow and network-dependent. | `SentenceEmbedder` `Protocol` + `FakeEmbedder` for the strategy's tests; `SentenceTransformer` monkeypatched with a lightweight fake for `EmbeddingService`'s own tests. |
| A single sentence longer than `budget` (heading-adjusted `chunk_size`) needs the same fixed-width fallback as `RecursiveChunkingStrategy`. | Reuses `text_windowing.split_fragments` unchanged, including its `''`-separator fixed-width fallback. |
| Cosine similarity is undefined for a zero vector (division by zero). | Out of scope: real `SentenceTransformer` embeddings are not zero vectors in practice; not guarded explicitly in this spec. |

## What is **not** in this spec

- The `DocumentExtension` (or any other criterion) → strategy factory/registry.
- A shared sentence-splitting helper between `SentenceChunkingStrategy` and
  `SemanticChunkingStrategy`.
- Token-based chunk sizing.
- `heading_path` as a `ChunkMetadata` field.
- `get_config` on the `ChunkingStrategy` ABC.
- Using `EmbeddingService.similarity` or `SemanticChunkingStrategy` anywhere in retrieval/search.
- Anything in `vector_store/`, `retrieval/`, `generation/` or `rag/`.

Each one of those, if it lands, goes in its own spec.
