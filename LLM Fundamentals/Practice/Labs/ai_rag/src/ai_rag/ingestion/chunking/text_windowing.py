HEADING_JOINER = ' > '
HEADING_BODY_SEPARATOR = '\n\n'


def build_heading_prefix(heading_path: tuple[str, ...]) -> str:
    if not heading_path:
        return ''
    return f'{HEADING_JOINER.join(heading_path)}{HEADING_BODY_SEPARATOR}'


def split_fragments(text: str, separators: tuple[str, ...], budget: int) -> list[str]:
    # Content-preserving: ''.join(split_fragments(text, separators, budget)) == text.
    if not text:
        return []
    if len(text) <= budget:
        return [text]
    if not separators:
        # Se agotó la lista de separadores sin llegar a '': último recurso, trocear a tamaño fijo.
        return [text[i : i + budget] for i in range(0, len(text), budget)]

    separator, *remaining = separators
    pieces = list(text) if separator == '' else _split_keeping_separator(text, separator)

    fragments: list[str] = []
    for piece in pieces:
        if len(piece) <= budget:
            fragments.append(piece)
        else:
            fragments.extend(split_fragments(piece, remaining, budget))
    return fragments


def _split_keeping_separator(text: str, separator: str) -> list[str]:
    # El separador se conserva pegado al final de cada trozo (salvo el último), de modo que
    # ''.join(...) reconstruye el texto exactamente.
    parts = text.split(separator)
    pieces = [f'{part}{separator}' for part in parts[:-1]]
    pieces.append(parts[-1])
    return pieces


def merge_windows(fragments: list[str], budget: int, effective_overlap: int) -> list[list[str]]:
    windows: list[list[str]] = []
    current: list[str] = []
    current_len = 0

    for fragment in fragments:
        fragment_len = len(fragment)
        while current and current_len + fragment_len > budget:
            windows.append(current)
            current = seed_overlap(current, effective_overlap)
            current_len = sum(len(piece) for piece in current)
        current.append(fragment)
        current_len += fragment_len

    if current:
        windows.append(current)
    return windows


def seed_overlap(window: list[str], effective_overlap: int) -> list[str]:
    if effective_overlap <= 0:
        return []

    suffix: list[str] = []
    suffix_len = 0
    for fragment in reversed(window):
        if suffix_len + len(fragment) > effective_overlap:
            break
        suffix.insert(0, fragment)
        suffix_len += len(fragment)

    # Sufijo propio: garantiza que la siguiente ventana siempre avanza.
    if len(suffix) == len(window):
        suffix = suffix[1:]
    return suffix
