"""Utilidades de hash SHA-256 para archivos y textos."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256_file(path: str | Path) -> str:
    """Calcula el SHA-256 de un archivo en disco."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str, encoding: str = "utf-8") -> str:
    """Calcula el SHA-256 de un texto."""
    return hashlib.sha256(text.encode(encoding)).hexdigest()


def sha256_bytes(data: bytes) -> str:
    """Calcula el SHA-256 de un blob de bytes."""
    return hashlib.sha256(data).hexdigest()