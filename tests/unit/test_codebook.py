"""Pruebas para el cargador de libros de códigos."""

from voxitech.coding.codebook import CodebookLoader, Code


def test_load_codebook():
    """Carga el libro de códigos v1.0.0."""
    loader = CodebookLoader()
    config = loader.load("config/codebooks/trump_gender_v1.yaml")
    assert config.id == "trump_gender_v1"
    assert config.version == "1.0.0"
    assert config.language == "en"
    assert len(config.codes) > 0


def test_get_code_by_code():
    """Busca un código por su identificador corto."""
    loader = CodebookLoader()
    config = loader.load("config/codebooks/trump_gender_v1.yaml")
    code = loader.get_code_by_code(config, "GEN_MUJER")
    assert code is not None
    assert code.code == "GEN_MUJER"
    assert code.level == 1


def test_get_level1_and_level2_codes():
    """Retorna códigos separados por nivel."""
    loader = CodebookLoader()
    config = loader.load("config/codebooks/trump_gender_v1.yaml")
    l1 = loader.get_level1_codes(config)
    l2 = loader.get_level2_codes(config)
    assert len(l1) > 0
    assert len(l2) > 0
    for c in l1:
        assert c.level == 1
    for c in l2:
        assert c.level == 2


def test_get_children():
    """Retorna códigos hijos de un padre."""
    loader = CodebookLoader()
    config = loader.load("config/codebooks/trump_gender_v1.yaml")
    # Buscar un código nivel 1 que tenga hijos nivel 2
    l1_codes = loader.get_level1_codes(config)
    found_parent = False
    for c in l1_codes:
        children = loader.get_children(config, c.code_id)
        if children:
            found_parent = True
            for child in children:
                assert child.parent_code_id == c.code_id
                assert child.level == 2
            break
    assert found_parent, "Se esperaba al menos un código nivel 1 con hijos nivel 2"


def test_code_dataclass_defaults():
    """Verifica valores por defecto de Code."""
    code = Code(
        code_id="test-1",
        codebook_id="cb-1",
        parent_code_id=None,
        code="TEST",
        label="Test label",
        definition="Test definition",
    )
    assert code.examples == []
    assert code.inclusion_criteria == []
    assert code.exclusion_criteria == []
    assert code.level == 1
    assert code.memo is None
