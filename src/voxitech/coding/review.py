"""Flujo de revisión humana de codificaciones asistidas por modelo."""

from __future__ import annotations

from typing import Any

from voxitech.coding.coding import CodingStore
from voxitech.utils.logging import get_logger

logger = get_logger()


class CodingReview:
    """Gestiona el flujo de revisión humana obligatoria para codificaciones."""

    def __init__(self, store: CodingStore) -> None:
        self.store = store

    def propose_model_suggestion(
        self,
        unit_id: str,
        code_id: str,
        code: str,
        quote_literal: str | None = None,
        discourse_frame: str | None = None,
        actors: list[str] | None = None,
        oppositions: list[str] | None = None,
        legitimization: str | None = None,
        interpretation: str | None = None,
        notes: str | None = None,
    ) -> Any:
        """Un modelo de lenguaje sugiere un código para una unidad.

        El código queda en estado 'proposed' y DEBE ser revisado por un humano
        antes de poder aprobarse.
        """
        coding = self.store.add(
            unit_id=unit_id,
            code_id=code_id,
            code=code,
            assigned_by="model_suggested",
            status="proposed",
            quote_literal=quote_literal,
            discourse_frame=discourse_frame,
            actors=actors,
            oppositions=oppositions,
            legitimization=legitimization,
            interpretation=interpretation,
            notes=notes,
        )
        logger.info(
            "Modelo sugirió código {code} para unidad {unit} (pendiente revisión humana)",
            code=code,
            unit=unit_id[:8],
        )
        return coding

    def add_manual_coding(
        self,
        unit_id: str,
        code_id: str,
        code: str,
        codificador: str,
        quote_literal: str | None = None,
        discourse_frame: str | None = None,
        actors: list[str] | None = None,
        oppositions: list[str] | None = None,
        legitimization: str | None = None,
        interpretation: str | None = None,
        notes: str | None = None,
        auto_submit_review: bool = True,
    ) -> Any:
        """Un investigador añade una codificación manual.

        Si auto_submit_review es True, la codificación se envía directamente
        a 'under_review' para ser validada por otro investigador (doble codificación)
        o por el mismo investigador en una segunda pasada.
        """
        status = "under_review" if auto_submit_review else "proposed"
        coding = self.store.add(
            unit_id=unit_id,
            code_id=code_id,
            code=code,
            assigned_by="human",
            status=status,
            quote_literal=quote_literal,
            discourse_frame=discourse_frame,
            actors=actors,
            oppositions=oppositions,
            legitimization=legitimization,
            interpretation=interpretation,
            notes=notes,
        )
        logger.info(
            "Codificación manual agregada por {codificador}: {code} para unidad {unit} (estado={status})",
            codificador=codificador,
            code=code,
            unit=unit_id[:8],
            status=status,
        )
        return coding

    def pending_review(self) -> list[Any]:
        """Retorna todas las codificaciones pendientes de revisión humana."""
        return self.store.get_by_status("proposed") + self.store.get_by_status("under_review")

    def approved(self) -> list[Any]:
        """Retorna todas las codificaciones aprobadas."""
        return self.store.get_by_status("approved")

    def rejected(self) -> list[Any]:
        """Retorna todas las codificaciones rechazadas."""
        return self.store.get_by_status("rejected")

    def review_coding(
        self,
        coding_id: str,
        decision: str,
        reviewer: str,
        notes: str | None = None,
    ) -> Any | None:
        """Un investigador revisa y aprueba/rechaza una codificación."""
        return self.store.review(coding_id, decision, reviewer, notes)