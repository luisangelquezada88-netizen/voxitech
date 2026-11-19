"""Pruebas para identificadores determinísticos UUID5."""

from voxitech.utils.ids import deterministic_uuid, document_id_from_url, unit_id_from_document
import uuid


def test_deterministic_uuid_same_input_same_output():
    """Misma entrada produce mismo UUID."""
    u1 = deterministic_uuid(uuid.NAMESPACE_URL, "https://example.com")
    u2 = deterministic_uuid(uuid.NAMESPACE_URL, "https://example.com")
    assert u1 == u2


def test_deterministic_uuid_different_input_different_output():
    """Entradas diferentes producen UUIDs diferentes."""
    u1 = deterministic_uuid(uuid.NAMESPACE_URL, "https://example.com/a")
    u2 = deterministic_uuid(uuid.NAMESPACE_URL, "https://example.com/b")
    assert u1 != u2


def test_document_id_from_url():
    """document_id_from_url genera UUID válido."""
    uid = document_id_from_url("https://whitehouse.gov/test")
    assert uuid.UUID(uid)  # no lanza excepción si es UUID válido


def test_unit_id_from_document():
    """unit_id_from_document genera UUID válido y determinístico."""
    u1 = unit_id_from_document("doc-123", 0)
    u2 = unit_id_from_document("doc-123", 0)
    assert u1 == u2
    assert uuid.UUID(u1)
    # Diferente índice produce diferente UUID
    u3 = unit_id_from_document("doc-123", 1)
    assert u1 != u3