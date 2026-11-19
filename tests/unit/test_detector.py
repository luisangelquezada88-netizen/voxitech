"""Pruebas para el detector temático."""

import pandas as pd
from voxitech.topic_detection.detector import TopicDetector


def test_detector_load_and_detect():
    """Carga el diccionario real y detecta en unidades de prueba."""
    detector = TopicDetector("config/dictionaries/en/genero_familia_v1.yaml")
    assert detector.dictionary is not None
    assert detector.matcher is not None

    units = pd.DataFrame(
        [
            {
                "unit_id": "u1",
                "document_id": "d1",
                "text": "We will protect women's sports and keep men out of women's locker rooms. Biological reality matters.",
                "word_count": 19,
            },
            {
                "unit_id": "u2",
                "document_id": "d1",
                "text": "The traditional family is the foundation of our nation. Mothers and fathers raise sons and daughters.",
                "word_count": 16,
            },
            {
                "unit_id": "u3",
                "document_id": "d1",
                "text": "The weather is nice today for a walk in the park.",
                "word_count": 11,
            },
        ]
    )

    mentions = detector.detect_on_units(units)
    assert len(mentions) > 0
    themes = set(mentions["theme"])
    # u1 tiene mujer/hombre/cuerpo; u2 tiene familia
    assert "cuerpo_y_reproduccion" in themes or "genero_y_sexo" in themes
    assert "familia_y_parentalidad" in themes

    # u3 no debería tener menciones
    u3_mentions = mentions[mentions["unit_id"] == "u3"]
    assert len(u3_mentions) == 0


def test_theme_summary():
    """Resumen por tema calcula correctamente."""
    detector = TopicDetector("config/dictionaries/en/genero_familia_v1.yaml")
    units = pd.DataFrame(
        [
            {
                "unit_id": "u1",
                "document_id": "d1",
                "text": "Women and men and women again.",
                "word_count": 5,
            }
        ]
    )
    mentions = detector.detect_on_units(units)
    summary = detector.get_theme_summary(mentions)
    assert "genero_y_sexo" in summary["theme"].values
    row = summary[summary["theme"] == "genero_y_sexo"].iloc[0]
    assert row["total_mentions"] >= 2  # women aparece 2 veces, men 1


def test_prioritized_units():
    """Unidades prioritarias para codificación humana."""
    detector = TopicDetector("config/dictionaries/en/genero_familia_v1.yaml")
    units = pd.DataFrame(
        [
            {
                "unit_id": "u1",
                "document_id": "d1",
                "unit_index": 0,
                "text": "Women and men and gender ideology and family values.",
                "word_count": 8,
                "document_type": "executive_order",
                "date": "2025-01-20",
                "speaker": "Donald J. Trump",
            },
            {
                "unit_id": "u2",
                "document_id": "d1",
                "unit_index": 1,
                "text": "The weather is nice.",
                "word_count": 4,
                "document_type": "executive_order",
                "date": "2025-01-20",
                "speaker": "Donald J. Trump",
            },
        ]
    )
    mentions = detector.detect_on_units(units)
    prioritized = detector.get_prioritized_units(mentions, units, top_n=10)
    assert len(prioritized) == 1  # solo u1 tiene menciones
    assert prioritized.iloc[0]["unit_id"] == "u1"