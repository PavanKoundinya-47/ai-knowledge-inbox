import pytest
from app.services.chunking import chunk_text

def test_empty_text():
    assert chunk_text("   ") == []

def test_chunks_cover_long_text():
    text = " ".join(f"word{i}" for i in range(120))
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert "word0" in chunks[0]
    assert "word119" in chunks[-1]

def test_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("hello", chunk_size=10, overlap=10)
