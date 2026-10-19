import pytest
from pydantic import ValidationError
from app.schemas import IngestRequest, QueryRequest

def test_note_requires_content():
    with pytest.raises(ValueError):
        IngestRequest(type="note").validate_payload()

def test_url_requires_url():
    with pytest.raises(ValueError):
        IngestRequest(type="url").validate_payload()

def test_question_minimum_length():
    with pytest.raises(ValidationError):
        QueryRequest(question="hi")
