"""Pruebas para cargador de diccionarios temáticos."""

from voxitech.topic_detection.dictionary import DictionaryLoader


def test_load_dictionary():
    """Carga el diccionario actualizado v1.1.0."""
    loader = DictionaryLoader()
    config = loader.load("config/dictionaries/en/genero_familia_v1.yaml")
    assert config.id == "genero_familia_en_v1"
    assert config.version == "1.1.0"
    assert config.language == "en"
    assert len(config.themes) > 0
    theme_ids = [t.id for t in config.themes]
    assert "genero_y_sexo" in theme_ids
    assert "familia_y_parentalidad" in theme_ids
    assert "feminismo_e_igualdad" in theme_ids


def test_get_terms_by_theme():
    """Retorna términos de un tema específico."""
    loader = DictionaryLoader()
    config = loader.load("config/dictionaries/en/genero_familia_v1.yaml")
    terms = loader.get_terms_by_theme(config, "personas_trans")
    assert "transgender" in terms
    assert "trans woman" in terms


def test_get_all_theme_ids():
    """Retorna todos los IDs de tema."""
    loader = DictionaryLoader()
    config = loader.load("config/dictionaries/en/genero_familia_v1.yaml")
    ids = loader.get_all_theme_ids(config)
    assert len(ids) == len(config.themes)