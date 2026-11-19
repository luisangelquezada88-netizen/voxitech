"""Pruebas de lógica del fetcher sin peticiones de red reales."""

from voxitech.extraction.fetcher import Fetcher


def test_fetcher_initialization():
    """El fetcher se inicializa con los parámetros dados."""
    f = Fetcher(
        user_agent="TestAgent/1.0",
        rate_limit_rps=2.0,
        respect_robots_txt=True,
        timeout=15,
        max_retries=2,
        backoff_factor=1.5,
    )
    assert f.user_agent == "TestAgent/1.0"
    assert f.rate_limit_rps == 2.0
    assert f.respect_robots_txt is True
    assert f.timeout == 15
    assert f.max_retries == 2
    assert f.backoff_factor == 1.5


def test_fetcher_defaults():
    """Los valores por defecto son razonables."""
    f = Fetcher()
    assert f.user_agent == "VoxiTech Lab AI research (contacto: investigador@example.com)"
    assert f.rate_limit_rps == 1.0
    assert f.respect_robots_txt is True
    assert f.timeout == 30
    assert f.max_retries == 3
    assert f.backoff_factor == 2.0