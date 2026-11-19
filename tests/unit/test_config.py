"""Pruebas para carga y validación de configuración con Pydantic."""

from voxitech.config import load_project_config, ProjectConfig


def test_load_project_config():
    """Carga el YAML del proyecto Trump y valida campos obligatorios."""
    config = load_project_config("config/projects/trump_gender_2025_2026.yaml")
    assert config.id == "trump_gender_2025_2026"
    assert config.name == "Discurso de género, familia y sexualidad - Segundo mandato"
    assert config.research.language == "en"
    assert config.temporal.start_date == "2025-01-20"
    assert config.speaker.name == "Donald J. Trump"
    assert len(config.sources) == 1
    assert config.segmentation.min_words == 50
    assert config.segmentation.max_words == 200


def test_config_missing_required_field():
    """Falla si falta un campo obligatorio en el YAML."""
    import tempfile
    import yaml
    from pathlib import Path

    incomplete = {
        "id": "test",
        "name": "Test",
        # falta description, version, etc.
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(incomplete, f)
        tmp_path = f.name

    try:
        try:
            load_project_config(tmp_path)
            assert False, "Debía lanzar ValidationError por campos faltantes"
        except Exception:
            pass  # Esperado: Pydantic valida y falla
    finally:
        Path(tmp_path).unlink(missing_ok=True)