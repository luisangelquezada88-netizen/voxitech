"""Pruebas para utilidades de hash SHA-256."""

from voxitech.utils.hashing import sha256_bytes, sha256_file, sha256_text
import tempfile
from pathlib import Path


def test_sha256_text_deterministic():
    """El hash de un texto debe ser determinístico."""
    h1 = sha256_text("hola mundo")
    h2 = sha256_text("hola mundo")
    assert h1 == h2
    assert len(h1) == 64


def test_sha256_text_different_inputs():
    """Textos diferentes producen hashes diferentes."""
    assert sha256_text("a") != sha256_text("b")


def test_sha256_bytes():
    """sha256_bytes funciona con bytes."""
    h = sha256_bytes(b"test")
    assert len(h) == 64


def test_sha256_file():
    """sha256_file lee un archivo desde disco."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        f.write(b"contenido de prueba")
        tmp_path = f.name

    try:
        h = sha256_file(tmp_path)
        assert len(h) == 64
        # El hash del archivo debe coincidir con el hash del texto
        from voxitech.utils.hashing import sha256_text
        assert h == sha256_text("contenido de prueba")
    finally:
        Path(tmp_path).unlink(missing_ok=True)