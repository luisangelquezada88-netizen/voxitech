"""Pruebas para deduplicación de documentos."""

from voxitech.ingestion.dedup import DedupChecker


def test_dedup_by_url():
    """Detecta duplicado por URL."""
    checker = DedupChecker(keys=["url"], strategy="keep_first")
    candidate = {"url": "https://example.com/doc1", "content_hash": "abc", "title": "T", "date": "2025-01-01", "speaker": "S"}
    existing = [{"document_id": "doc-1", "url": "https://example.com/doc1", "content_hash": "xyz", "title": "Otro", "date": "2025-02-02", "speaker": "Otro"}]
    result = checker.check(candidate, existing)
    assert result.is_duplicate is True
    assert result.reason == "duplicate_url"
    assert result.existing_document_id == "doc-1"


def test_dedup_by_content_hash():
    """Detecta duplicado por hash de contenido."""
    checker = DedupChecker(keys=["content_hash"], strategy="keep_first")
    candidate = {"url": "https://example.com/doc2", "content_hash": "hash-123", "title": "T", "date": "2025-01-01", "speaker": "S"}
    existing = [{"document_id": "doc-1", "url": "https://example.com/diferente", "content_hash": "hash-123", "title": "Otro", "date": "2025-02-02", "speaker": "Otro"}]
    result = checker.check(candidate, existing)
    assert result.is_duplicate is True
    assert result.reason == "duplicate_content_hash"


def test_dedup_by_title_date_speaker():
    """Detecta duplicado por título+fecha+orador."""
    checker = DedupChecker(keys=["title_date_speaker"], strategy="keep_first")
    candidate = {"url": "https://example.com/doc3", "content_hash": "h1", "title": "Mi Discurso", "date": "2025-01-20", "speaker": "Donald J. Trump"}
    existing = [{"document_id": "doc-1", "url": "https://example.com/otro", "content_hash": "h2", "title": "mi discurso", "date": "2025-01-20", "speaker": "donald j. trump"}]
    result = checker.check(candidate, existing)
    assert result.is_duplicate is True
    assert result.reason == "duplicate_title_date_speaker"


def test_dedup_no_duplicate():
    """No detecta duplicado cuando no hay coincidencia."""
    checker = DedupChecker(keys=["url", "content_hash", "title_date_speaker"], strategy="keep_first")
    candidate = {"url": "https://example.com/nuevo", "content_hash": "hash-nuevo", "title": "Nuevo Título", "date": "2025-03-01", "speaker": "Nuevo Orador"}
    existing = [{"document_id": "doc-1", "url": "https://example.com/viejo", "content_hash": "hash-viejo", "title": "Viejo", "date": "2025-01-01", "speaker": "Viejo"}]
    result = checker.check(candidate, existing)
    assert result.is_duplicate is False
    assert result.reason is None