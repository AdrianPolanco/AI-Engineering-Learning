# SPEC 01 — RecursiveChunkingStrategy

> **Status:** Implemented
> **Depends on:** —
> **Date:** 2026-09-05
> **Objective:** Implement `RecursiveChunkingStrategy`, a character-budget chunking strategy that splits each `DocumentBlock` by a descending list of separators supplied per extension by a concrete `ChunkingRuleProvider`, as an alternative to `SentenceChunkingStrategy`.

## Why this spec exists

The repository already contains the seams for this feature but none of the behavior:
`RecursiveChunkerConfig` exists without validation, `RecursiveChunkingStrategy` is a stub whose
`chunk()` calls the abstract base and returns `None`, and `ChunkingRules` / `ChunkingRuleProvider`
exist with no implementation. This spec closes all of them at once and fixes the semantics of a
character-based recursive split so that two invariants become testable: **no chunk exceeds
`chunk_size`** and **no source text is lost**.

It also diverges deliberately from `SentenceChunkingStrategy` on one point: this strategy consumes
`DocumentBlock.heading_path` (populated by `MdPreProcessor`) and prepends it to each chunk's text as
a breadcrumb, so markdown chunks carry their structural context into retrieval.

## Scope

**In:**

- Validation for `RecursiveChunkerConfig` in `src/ai_rag/domain/chunk_config.py`, mirroring the
  `SentenceChunkerConfig` style (module-level message constants + `__post_init__` raising `ValueError`).
- A shared `_build_chunk_metadata` helper and the `UNSUPPORTED_CONFIG_MESSAGE` constant lifted into
  `ChunkingStrategy` (`src/ai_rag/ingestion/chunking/chunking_strategy.py`), with
  `SentenceChunkingStrategy` updated to use them. Behavior-preserving, its own commit.
- A concrete `ExtensionChunkingRuleProvider` in
  `src/ai_rag/ingestion/chunking/rule_providers/extension_chunking_rule_provider.py`, mapping each
  `DocumentExtension` to a `ChunkingRules`.
- The full implementation of `RecursiveChunkingStrategy` in
  `src/ai_rag/ingestion/chunking/strategies/recursive_chunking.py`.
- Heading breadcrumb prefixing of chunk text from `DocumentBlock.heading_path`.
- Tests for all of the above under `tests/`.
- Updating the "Current state" paragraph of `CLAUDE.md`, which still describes
  `src/ai_rag/ingestion/chunker.py` as an empty stub.

**Out of scope (for future specs):**

- Any factory or registry wiring `DocumentExtension` → pre-processor / strategy. Callers keep
  building `Chunker(preprocessor, strategy)` by hand.
- Token-based chunk sizing with a HuggingFace tokenizer.
- Adding `heading_path` as a field on `ChunkMetadata` — that changes the `Chunk` JSON shape in
  `CONTRACTS.md`.
- Adding `get_config` to the `ChunkingStrategy` ABC.
- Any change to `Chunker`, `DocumentLoader`, the pre-processors, or the `vector_store` / `retrieval`
  / `generation` / `rag` layers that do not exist yet.

## Data model

No new domain object. Two existing ones change or get used for the first time.

`RecursiveChunkerConfig` gains validation (values are in **characters**):

```python
MIN_CHUNK_SIZE_MESSAGE = 'chunk_size must be at least 1'
MIN_CHUNK_OVERLAP_MESSAGE = 'chunk_overlap must not be negative'
OVERLAP_NOT_LESS_THAN_SIZE_MESSAGE = 'chunk_overlap must be less than chunk_size'

@dataclass(frozen=True)
class RecursiveChunkerConfig:
    chunk_size: int       # >= 1
    chunk_overlap: int    # >= 0 and < chunk_size
```

`ChunkingRules.separators` is used for the first time. Order is descending in structural weight; the
empty string is the documented last resort that splits into single characters:

```python
# ExtensionChunkingRuleProvider
DocumentExtension.MARKDOWN -> ChunkingRules(('\n\n', '\n- ', '\n', '. ', ' ', ''))
DocumentExtension.TXT      -> ChunkingRules(('\n\n', '\n', '. ', ' ', ''))
```

Heading prefix format, as module constants of the strategy:

```python
HEADING_JOINER = ' > '
HEADING_BODY_SEPARATOR = '\n\n'
# heading_path ('Vacaciones', 'Solicitud') -> 'Vacaciones > Solicitud\n\n'
```

`Chunk` and `ChunkMetadata` are unchanged. Chunk ids and indices follow
`SentenceChunkingStrategy` exactly: `f'{document_id}-chunk-{index}'`, `index` starting at `1` and
running continuously across all blocks of the document.

### Algorithm contract

For each `DocumentBlock` of the document, in order:

1. Build `prefix` from `heading_path` (empty tuple → empty prefix).
2. `budget = chunk_size - len(prefix)`. If `budget < 1`, drop the prefix and use the full
   `chunk_size` as budget.
3. Split `block.text` into fragments, each of length `<= budget`, by walking the separator list:
   split on the current separator keeping it attached to the end of each piece, keep pieces that fit,
   recurse with the remaining separators on those that do not. `''` splits into single characters. If
   the list is exhausted without `''`, fall back to fixed-width slicing of `budget` characters. The
   split is content-preserving: `''.join(fragments) == block.text`.
4. Merge fragments greedily into windows while the accumulated length stays `<= budget`.
5. After emitting a window, seed the next one with the **longest proper suffix** of that window whose
   combined length is `<= effective_overlap`, where `effective_overlap = min(chunk_overlap, budget - 1)`.
   Requiring a *proper* suffix guarantees forward progress.
6. Chunk text is `prefix + ''.join(window).strip()`. A window whose body strips to empty emits no chunk.

## Implementation plan

1. **Config validation.** Add the three message constants and `__post_init__` to
   `RecursiveChunkerConfig` in `src/ai_rag/domain/chunk_config.py`. Extend
   `tests/domain/test_chunk_config.py` with parametrized rejection cases and an acceptance case,
   mirroring the existing `SentenceChunkerConfig` tests. Verify: `uv run pytest tests/domain`.

2. **Extract the shared projection.** Move the `ChunkMetadata` projection into `ChunkingStrategy` as
   a protected static helper and move `UNSUPPORTED_CONFIG_MESSAGE` next to it; update
   `SentenceChunkingStrategy` to use both. No behavior change — commit separately from step 4, and
   `tests/chunkers/strategies/test_sentence_chunking.py` must pass **unmodified**.
   Verify: `uv run pytest`.

3. **Rule provider.** Add `ExtensionChunkingRuleProvider` under
   `src/ai_rag/ingestion/chunking/rule_providers/`, mirroring the `pre_processor.py` (ABC) +
   `pre_processors/` (implementations) layout already in the repo. A module-level mapping constant
   holds the rules; an unknown extension raises `NotImplementedError` with a formatted message
   constant. Add `tests/chunkers/rule_providers/test_extension_chunking_rule_provider.py`.

4. **Strategy — split and merge.** Implement `RecursiveChunkingStrategy.__init__(config, rule_provider)`,
   `set_config` (raising `TypeError` for a non-`RecursiveChunkerConfig`), `get_config`, and the
   private split/merge helpers per the algorithm contract, ignoring `heading_path` for now.
   Resolve the extension with `DocumentExtension(document.metadata.document_extension)`.
   Add `tests/chunkers/strategies/test_recursive_chunking.py` covering size, overlap, no-text-lost,
   metadata projection, a deterministic expected-texts case, and config rejection.

5. **Strategy — heading prefix.** Add the breadcrumb prefix, the reduced budget, and the degenerate
   fallback. Extend the test file with the markdown-prefix, txt-no-prefix and oversized-prefix cases.

6. **Docs.** Update the "Current state" paragraph in `CLAUDE.md` to reflect the implemented chunking
   layer. `CONTRACTS.md` needs no change — no domain shape moves.

## Acceptance criteria

- [ ] `RecursiveChunkerConfig(0, 0)`, `(10, -1)`, `(10, 10)` and `(10, 20)` each raise `ValueError`
      with the matching message constant.
- [ ] `uv run pytest` passes, and `tests/chunkers/strategies/test_sentence_chunking.py` is byte-identical
      to its current version.
- [ ] `ExtensionChunkingRuleProvider().get_rules(DocumentExtension.MARKDOWN)` and `.get_rules(DocumentExtension.TXT)`
      each return a `ChunkingRules` whose last separator is `''`.
- [ ] For every config in `{(200, 50), (120, 30), (60, 10)}` and both a TXT and an MD document, every
      returned chunk satisfies `len(chunk.text) <= config.chunk_size`.
- [ ] A block containing a single unbreakable 500-character token still produces chunks that all
      satisfy `len(chunk.text) <= chunk_size`.
- [ ] Every word of the source block appears, in source order, across the returned chunks.
- [ ] For two consecutive chunks of the same block, the second chunk's body starts with a non-empty
      suffix of the first chunk's body of length `<= chunk_overlap`, whenever the first chunk was
      built from more than one fragment.
- [ ] Chunks from an `MdPreProcessor` block with `heading_path=('Vacaciones', 'Solicitud')` all start
      with `'Vacaciones > Solicitud\n\n'`.
- [ ] Chunks from a `TxtPreProcessor` block (empty `heading_path`) carry no prefix.
- [ ] With `chunk_size` smaller than the heading prefix, chunks are emitted without a prefix and still
      satisfy `len(chunk.text) <= chunk_size`.
- [ ] Chunk `id`, `index` and every `ChunkMetadata` field are projected exactly as
      `SentenceChunkingStrategy` projects them, with `index` starting at `1` and continuous across blocks.
- [ ] `RecursiveChunkingStrategy.set_config(SentenceChunkerConfig(4, 2))` raises `TypeError`.
- [ ] No chunk has empty or whitespace-only text.

## Decisions

- **Yes:** a concrete `ChunkingRuleProvider` injected into the strategy. The ABC and `ChunkingRules`
  already exist in the repo for this; anything else leaves them as dead code.
- **No:** separators as module constants or as a `RecursiveChunkerConfig` field. Same reason.
- **Yes:** `chunk_size` in **characters**. No dependency, deterministic, trivially assertable.
- **No:** token counting via `transformers`. It couples ingestion to a tokenizer and makes tests
  model-dependent. It can be a later spec now that the strategy exists.
- **Yes:** overlap built from whole trailing fragments, never mid-unit. Overlap is therefore
  `<= chunk_overlap`, not exactly it. This mirrors how `SentenceChunkingStrategy` overlaps whole sentences.
- **No:** an exact `previous[-chunk_overlap:]` character slice. It cuts words in half.
- **Yes:** `''` as the last separator, splitting into characters. It makes "no chunk exceeds
  `chunk_size`" a real guarantee rather than a best effort.
- **No:** emitting oversized chunks when no separator fits. It breaks the size guarantee, which
  ultimately stands in for the embedding model's input limit.
- **Yes:** validation on `RecursiveChunkerConfig`. Without `chunk_overlap < chunk_size` the merge
  loop cannot guarantee progress.
- **Yes:** heading breadcrumb `'A > B\n\n'` prepended to chunk text. Cheap in characters and readable
  in a prompt.
- **No:** re-emitting ATX headings (`# A`, `## B`). It costs more characters and puts back markup the
  pre-processor deliberately stripped.
- **Yes:** the prefix counts against `chunk_size` via a reduced budget, so the size invariant holds
  on prefixed chunks too.
- **Yes:** graceful degradation when the prefix does not fit — emit the chunk unprefixed. A single
  pathological heading must not abort an ingestion run.
- **No:** truncating the prefix to fit. It adds a second arbitrary tuning knob.
- **Yes:** `TypeError` for a wrong config type, matching the refactored `SentenceChunkingStrategy`.
  The current stub raises `NotImplementedError`; that is corrected.
- **No:** adding `get_config` to the `ChunkingStrategy` ABC. Broader refactor, separate spec.
- **Yes:** extracting the shared metadata projection into the base class as its own commit, before
  the new strategy lands — the `CLAUDE.md` rule is to not mix refactors with behavioral changes.

## Risks

| Risk | Mitigation |
| --- | --- |
| A large heading prefix leaves `budget < chunk_overlap`, so the overlap suffix swallows the whole window and the merge loop never advances. | `effective_overlap = min(chunk_overlap, budget - 1)` and the requirement that the seed be a *proper* suffix of the emitted window. |
| `document_extension` is typed `str` on `PreProcessedDocumentMetadata` but the pre-processors store a `DocumentExtension`. | Normalize with `DocumentExtension(document.metadata.document_extension)`; `DocumentExtension` is a `StrEnum`, so both forms resolve. |
| Step 2 touches working, tested code. | It is behavior-preserving and lands in its own commit; `test_sentence_chunking.py` must pass unmodified. |
| The `''` separator produces one fragment per character on pathological input. | Only reached after every other separator fails, and the merge phase immediately regroups them up to `budget`. |

## What is **not** in this spec

- The `DocumentExtension` → pre-processor / strategy factory.
- Token-based chunk sizing.
- `heading_path` as a `ChunkMetadata` field.
- `get_config` on the `ChunkingStrategy` ABC.
- Anything in `vector_store/`, `retrieval/`, `generation/` or `rag/`.

Each one of those, if it lands, goes in its own spec.
