"""Generadores de identificadores determinísticos (UUID5)."""

from __future__ import annotations

import uuid

NAMESPACE_URL = uuid.UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")  # DNS namespace
NAMESPACE_OPAQUE = uuid.UUID("6ba7b812-9dad-11d1-80b4-00c04fd430c8")  # URL namespace


def deterministic_uuid(namespace: uuid.UUID, key: str) -> str:
    """Genera un UUID5 determinístico a partir de un namespace y una clave estable."""
    return str(uuid.uuid5(namespace, key))


def document_id_from_url(url: str) -> str:
    """ID determinístico para un documento a partir de su URL."""
    return deterministic_uuid(NAMESPACE_URL, url)


def unit_id_from_document(document_id: str, unit_index: int) -> str:
    """ID determinístico para una unidad de análisis dentro de un documento."""
    return deterministic_uuid(NAMESPACE_OPAQUE, f"{document_id}:{unit_index}")