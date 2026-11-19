"""Pruebas para el motor de coincidencias temáticas."""

from voxitech.topic_detection.dictionary import (
    DictionaryConfig,
    DictionaryTheme,
)
from voxitech.topic_detection.matcher import DictionaryMatcher


def _make_dictionary() -> DictionaryConfig:
    return DictionaryConfig(
        id="test_dict",
        version="1.0.0",
        language="en",
        project_id="test_project",
        description="Diccionario de prueba",
        match_mode="exact",
        case_sensitive=False,
        whole_word=True,
        themes=[
            DictionaryTheme(
                id="genero",
                label="Género",
                terms=["woman", "women", "man", "men"],
                exclusion_terms=[],
            ),
            DictionaryTheme(
                id="familia",
                label="Familia",
                terms=["family", "families"],
                exclusion_terms=[],
            ),
        ],
    )


def test_match_unit_exact():
    """Detecta coincidencias exactas en una unidad."""
    matcher = DictionaryMatcher(_make_dictionary())
    mentions = matcher.match_unit(
        unit_id="unit-1",
        document_id="doc-1",
        text="The woman and the man spoke about women and men rights.",
        word_count=11,
    )
    themes = {m.theme for m in mentions}
    assert "genero" in themes
    terms = {m.term for m in mentions if m.theme == "genero"}
    assert "woman" in terms
    assert "man" in terms
    assert "women" in terms
    assert "men" in terms


def test_match_unit_case_insensitive():
    """La coincidencia no distingue mayúsculas por defecto."""
    matcher = DictionaryMatcher(_make_dictionary())
    mentions = matcher.match_unit(
        unit_id="unit-1",
        document_id="doc-1",
        text="WOMAN and Man",
        word_count=3,
    )
    assert len(mentions) >= 2


def test_match_unit_no_match():
    """Sin coincidencias retorna lista vacía."""
    matcher = DictionaryMatcher(_make_dictionary())
    mentions = matcher.match_unit(
        unit_id="unit-1",
        document_id="doc-1",
        text="The weather is nice today.",
        word_count=5,
    )
    assert mentions == []


def test_density_calculation():
    """La densidad se calcula correctamente por 1.000 palabras."""
    matcher = DictionaryMatcher(_make_dictionary())
    # 1000 palabras, "woman" aparece 2 veces -> densidad 2.0
    text = "woman " + "other " * 999
    mentions = matcher.match_unit(
        unit_id="unit-1",
        document_id="doc-1",
        text=text,
        word_count=1000,
    )
    woman_mentions = [m for m in mentions if m.term == "woman"]
    assert len(woman_mentions) == 1
    assert woman_mentions[0].frequency == 1
    assert woman_mentions[0].density_per_1k_words == 1.0


def test_context_snippet():
    """Extrae contexto alrededor de la coincidencia."""
    matcher = DictionaryMatcher(_make_dictionary())
    mentions = matcher.match_unit(
        unit_id="unit-1",
        document_id="doc-1",
        text="The woman spoke passionately about policy.",
        word_count=6,
    )
    woman_mentions = [m for m in mentions if m.term == "woman"]
    assert len(woman_mentions) == 1
    assert "woman" in woman_mentions[0].context_snippet