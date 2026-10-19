def chunk_text(text: str, chunk_size: int = 1800, overlap: int = 250) -> list[str]:
    """Simple character-based chunks with overlap."""
    cleaned = " ".join(text.split())
    if not cleaned:
        return []
    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("chunk_size must be positive and overlap smaller than chunk_size")
    chunks, start = [], 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        if end < len(cleaned):
            boundary = cleaned.rfind(" ", start + int(chunk_size * .7), end)
            if boundary > start:
                end = boundary
        part = cleaned[start:end].strip()
        if part:
            chunks.append(part)
        if end >= len(cleaned):
            break
        start = max(end - overlap, start + 1)
    return chunks
