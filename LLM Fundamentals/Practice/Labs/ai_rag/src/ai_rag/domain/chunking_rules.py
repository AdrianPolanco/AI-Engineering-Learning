from dataclasses import dataclass

@dataclass(frozen=True)
class ChunkingRules:
    separators: tuple[str, ...]