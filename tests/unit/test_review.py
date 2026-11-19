"""Pruebas para el flujo de revisión humana."""

from voxitech.coding.coding import CodingStore
from voxitech.coding.review import CodingReview


def test_propose_model_suggestion():
    """El modelo sugiere un código en estado 'proposed'."""
    store = CodingStore()
    review = CodingReview(store)
    coding = review.propose_model_suggestion(
        unit_id="unit-1",
        code_id="code-1",
        code="GEN_MUJER",
        quote_literal="Las mujeres son fundamentales",
    )
    assert coding.status == "proposed"
    assert coding.assigned_by == "model_suggested"
    assert coding.reviewed_by is None


def test_add_manual_coding_auto_review():
    """Codificación manual va a 'under_review' por defecto."""
    store = CodingStore()
    review = CodingReview(store)
    coding = review.add_manual_coding(
        unit_id="unit-1",
        code_id="code-1",
        code="GEN_MUJER",
        codificador="investigador-1",
    )
    assert coding.status == "under_review"
    assert coding.assigned_by == "human"


def test_add_manual_coding_no_auto_review():
    """Codificación manual se queda en 'proposed' si auto_submit_review=False."""
    store = CodingStore()
    review = CodingReview(store)
    coding = review.add_manual_coding(
        unit_id="unit-1",
        code_id="code-1",
        code="GEN_MUJER",
        codificador="investigador-1",
        auto_submit_review=False,
    )
    assert coding.status == "proposed"


def test_pending_review():
    """Retorna codificaciones pendientes de revisión."""
    store = CodingStore()
    review = CodingReview(store)
    review.propose_model_suggestion(unit_id="u1", code_id="c1", code="A")
    review.add_manual_coding(unit_id="u2", code_id="c2", code="B", codificador="inv", auto_submit_review=True)
    review.add_manual_coding(unit_id="u3", code_id="c3", code="C", codificador="inv", auto_submit_review=False)

    pending = review.pending_review()
    assert len(pending) == 3


def test_review_coding_flow():
    """Flujo completo: propuesta -> revisión -> aprobada."""
    store = CodingStore()
    review = CodingReview(store)
    coding = review.propose_model_suggestion(unit_id="u1", code_id="c1", code="GEN_MUJER")
    assert coding.status == "proposed"

    updated = review.review_coding(coding.coding_id, "approve", "investigador-1", "OK")
    assert updated.status == "approved"
    assert updated.reviewed_by == "investigador-1"


def test_approved_and_rejected_lists():
    """Listas de aprobadas y rechazadas."""
    store = CodingStore()
    review = CodingReview(store)
    c1 = review.propose_model_suggestion(unit_id="u1", code_id="c1", code="A")
    c2 = review.propose_model_suggestion(unit_id="u2", code_id="c2", code="B")

    review.review_coding(c1.coding_id, "approve", "inv", "ok")
    review.review_coding(c2.coding_id, "reject", "inv", "no")

    assert len(review.approved()) == 1
    assert len(review.rejected()) == 1
    assert review.approved()[0].coding_id == c1.coding_id
    assert review.rejected()[0].coding_id == c2.coding_id
