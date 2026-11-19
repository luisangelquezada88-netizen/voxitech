"""Pruebas para el analizador de discurso."""

import pandas as pd
from voxitech.analysis.analyzer import DiscourseAnalyzer


def _make_mentions() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"unit_id": "u1", "document_id": "d1", "theme": "genero_y_sexo", "term": "woman", "frequency": 5, "density_per_1k_words": 2.5},
            {"unit_id": "u2", "document_id": "d1", "theme": "genero_y_sexo", "term": "men", "frequency": 3, "density_per_1k_words": 1.5},
            {"unit_id": "u3", "document_id": "d1", "theme": "familia_y_parentalidad", "term": "family", "frequency": 4, "density_per_1k_words": 2.0},
        ]
    )


def _make_units() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"unit_id": "u1", "document_id": "d1", "date": "2025-01-20", "word_count": 100},
            {"unit_id": "u2", "document_id": "d1", "date": "2025-02-05", "word_count": 200},
            {"unit_id": "u3", "document_id": "d1", "date": "2025-03-18", "word_count": 150},
        ]
    )


def _make_coding() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"coding_id": "c1", "unit_id": "u1", "status": "approved"},
            {"coding_id": "c2", "unit_id": "u2", "status": "rejected"},
            {"coding_id": "c3", "unit_id": "u3", "status": "approved"},
        ]
    )


def test_theme_frequency():
    analyzer = DiscourseAnalyzer()
    summary = analyzer.theme_frequency(_make_mentions())
    assert len(summary) == 2
    gen_row = summary[summary["theme"] == "genero_y_sexo"].iloc[0]
    assert gen_row["total_mentions"] == 8  # 5 + 3
    assert gen_row["total_units"] == 2


def test_theme_density():
    analyzer = DiscourseAnalyzer()
    summary = analyzer.theme_density(_make_mentions())
    assert len(summary) == 2
    gen_row = summary[summary["theme"] == "genero_y_sexo"].iloc[0]
    assert abs(gen_row["avg_density_per_1k"] - 2.0) < 0.001  # (2.5+1.5)/2


def test_plot_theme_frequency(tmp_path):
    analyzer = DiscourseAnalyzer(outputs_root=tmp_path)
    path = analyzer.plot_theme_frequency(_make_mentions(), filename="test_freq.png")
    assert path.exists()
    assert path.suffix == ".png"


def test_plot_theme_density(tmp_path):
    analyzer = DiscourseAnalyzer(outputs_root=tmp_path)
    path = analyzer.plot_theme_density(_make_mentions(), filename="test_dens.png")
    assert path.exists()


def test_plot_mentions_over_time(tmp_path):
    analyzer = DiscourseAnalyzer(outputs_root=tmp_path)
    path = analyzer.plot_mentions_over_time(_make_mentions(), _make_units(), filename="test_time.png")
    assert path.exists()


def test_plot_coding_status(tmp_path):
    analyzer = DiscourseAnalyzer(outputs_root=tmp_path)
    path = analyzer.plot_coding_status(_make_coding(), filename="test_coding.png")
    assert path.exists()


def test_corpus_stats():
    analyzer = DiscourseAnalyzer()
    stats = analyzer.corpus_stats(_make_units(), _make_mentions())
    assert stats["total_units"] == 3
    assert stats["total_words"] == 450
    assert stats["total_mentions"] == 12
    assert stats["themes_detected"] == 2
    assert stats["units_with_mentions"] == 3


def test_empty_mentions():
    analyzer = DiscourseAnalyzer()
    empty = pd.DataFrame(columns=["theme", "frequency", "unit_id"])
    assert analyzer.theme_frequency(empty).empty
    assert analyzer.theme_density(empty).empty
