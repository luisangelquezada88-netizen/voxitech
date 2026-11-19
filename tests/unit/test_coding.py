"""Pruebas para el almacén de codificaciones."""

import uuid

from voxitech.coding.coding import CodingStore, CODING_STATUSES


def test_add_and_get_coding():
    """Agrega y recupera una codificación."""
    store = CodingStore()
    coding = store.add(
        unit_id="unit-1",
        code_id="code-1",
        code="GEN_MUJER",
        assigned_by="human",
        status="approved",
        quote_literal="Las mujeres son importantes",
    )
    assert coding.coding_id is not None
    assert coding.unit_id == "unit-1"
    assert coding.code == "GEN_MUJER"
    assert coding.status == "approved"

    recovered = store.get(coding.coding_id)
    assert recovered is not None
    assert recovered.coding_id == coding.coding_id


def test_get_by_unit():
    """Retorna todas las codificaciones de una unidad."""
    store = CodingStore()
    store.add(unit_id="unit-1", code_id="c1", code="GEN_MUJER", assigned_by="human")
    store.add(unit_id="unit-1", code_id="c2", code="FAM_VAL", assigned_by="human")
    store.add(unit_id="unit-2", code_id="c3", code="GEN_MUJER", assigned_by="human")

    codings = store.get_by_unit("unit-1")
    assert len(codings) == 2
    codes = {c.code for c in codings}
    assert codes == {"GEN_MUJER", "FAM_VAL"}


def test_get_by_status():
    """Filtra codificaciones por estado."""
    store = CodingStore()
    store.add(unit_id="u1", code_id="c1", code="A", assigned_by="human", status="proposed")
    store.add(unit_id="u2", code_id="c2", code="B", assigned_by="human", status="approved")
    store.add(unit_id="u3", code_id="c3", code="C", assigned_by="human", status="rejected")

    assert len(store.get_by_status("proposed")) == 1
    assert len(store.get_by_status("approved")) == 1
    assert len(store.get_by_status("rejected")) == 1


def test_review_approve():
    """Aprueba una codificación propuesta."""
    store = CodingStore()
    coding = store.add(unit_id="u1", code_id="c1", code="A", assigned_by="model_suggested", status="proposed")
    updated = store.review(coding.coding_id, "approve", "investigador-1", "Bien codificado")
    assert updated is not None
    assert updated.status == "approved"
    assert updated.reviewed_by == "investigador-1"
    assert updated.reviewed_at is not None


def test_review_reject():
    """Rechaza una codificación propuesta."""
    store = CodingStore()
    coding = store.add(unit_id="u1", code_id="c1", code="A", assigned_by="model_suggested", status="proposed")
    updated = store.review(coding.coding_id, "reject", "investigador-1", "No aplica")
    assert updated.status == "rejected"


def test_review_invalid_decision():
    """Decisión inválida lanza ValueError."""
    store = CodingStore()
    coding = store.add(unit_id="u1", code_id="c1", code="A", assigned_by="human", status="proposed")
    try:
        store.review(coding.coding_id, "maybe", "inv")
        assert False, "Debía lanzar ValueError"
    except ValueError:
        pass


def test_review_nonexistent():
    """Revisar codificación inexistente retorna None."""
    store = CodingStore()
    result = store.review(uuid.uuid4().hex, "approve", "inv")
    assert result is None


def test_set_under_review():
    """Envía una codificación a revisión humana."""
    store = CodingStore()
    coding = store.add(unit_id="u1", code_id="c1", code="A", assigned_by="human", status="proposed")
    updated = store.set_under_review(coding.coding_id)
    assert updated.status == "under_review"


def test_to_dataframe():
    """Exporta a DataFrame de pandas."""
    store = CodingStore()
    store.add(unit_id="u1", code_id="c1", code="GEN_MUJER", assigned_by="human", status="approved")
    df = store.to_dataframe()
    assert "coding_id" in df.columns
    assert "unit_id" in df.columns
    assert "code" in df.columns
    assert "status" in df.columns
    assert len(df) == 1


def test_coding_statuses():
    """Estados válidos definidos."""
    assert "proposed" in CODING_STATUSES
    assert "under_review" in CODING_STATUSES
    assert "approved" in CODING_STATUSES
    assert "rejected" in CODING_STATUSES
