"""Registro de codificaciones cualitativas con revisión humana obligatoria."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import uuid

from voxitech.utils.logging import get_logger

logger = get_logger()


# Estados válidos de una codificación
CODING_STATUSES = {"proposed", "under_review", "approved", "rejected"}


@dataclass
class Coding:
    """Codificación de una unidad de análisis con un código del libro."""

    coding_id: str
    unit_id: str
    code_id: str
    code: str  # identificador corto del código (ej. GEN_MUJER)
    assigned_by: str  # human | model_suggested | model_suggested_human_reviewed
    status: str  # proposed | under_review | approved | rejected
    reviewed_by: str | None = None
    reviewed_at: str | None = None
    quote_literal: str | None = None
    discourse_frame: str | None = None
    actors: list[str] = field(default_factory=list)
    oppositions: list[str] = field(default_factory=list)
    legitimization: str | None = None
    interpretation: str | None = None
    notes: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CodingStore:
    """Repositorio de codificaciones en memoria con persistencia opcional."""

    def __init__(self) -> None:
        self._codings: dict[str, Coding] = {}
        self._by_unit: dict[str, list[str]] = {}  # unit_id -> [coding_id, ...]

    def add(
        self,
        unit_id: str,
        code_id: str,
        code: str,
        assigned_by: str,
        status: str = "proposed",
        quote_literal: str | None = None,
        discourse_frame: str | None = None,
        actors: list[str] | None = None,
        oppositions: list[str] | None = None,
        legitimization: str | None = None,
        interpretation: str | None = None,
        notes: str | None = None,
        coding_id: str | None = None,
    ) -> Coding:
        """Agrega una nueva codificación."""
        if status not in CODING_STATUSES:
            raise ValueError(f"Estado inválido: {status}. Válidos: {CODING_STATUSES}")

        if assigned_by not in {"human", "model_suggested", "model_suggested_human_reviewed"}:
            raise ValueError(f"assigned_by inválido: {assigned_by}")

        cid = coding_id or str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        coding = Coding(
            coding_id=cid,
            unit_id=unit_id,
            code_id=code_id,
            code=code,
            assigned_by=assigned_by,
            status=status,
            reviewed_by=None,
            reviewed_at=None,
            quote_literal=quote_literal,
            discourse_frame=discourse_frame,
            actors=actors or [],
            oppositions=oppositions or [],
            legitimization=legitimization,
            interpretation=interpretation,
            notes=notes,
            created_at=now,
            updated_at=now,
        )

        self._codings[cid] = coding
        self._by_unit.setdefault(unit_id, []).append(cid)

        logger.info(
            "Codificación agregada: {cid} | unidad={unit} | código={code} | estado={status} | asignado={by}",
            cid=cid[:8],
            unit=unit_id[:8],
            code=code,
            status=status,
            by=assigned_by,
        )

        return coding

    def get(self, coding_id: str) -> Coding | None:
        """Retorna una codificación por su ID."""
        return self._codings.get(coding_id)

    def get_by_unit(self, unit_id: str) -> list[Coding]:
        """Retorna todas las codificaciones de una unidad."""
        return [self._codings[cid] for cid in self._by_unit.get(unit_id, [])]

    def get_all(self) -> list[Coding]:
        """Retorna todas las codificaciones."""
        return list(self._codings.values())

    def get_by_status(self, status: str) -> list[Coding]:
        """Retorna codificaciones por estado."""
        return [c for c in self._codings.values() if c.status == status]

    def review(
        self,
        coding_id: str,
        decision: str,
        reviewer: str,
        notes: str | None = None,
    ) -> Coding | None:
        """Proceso de revisión humana: aprobar o rechazar una codificación.

        Args:
            coding_id: ID de la codificación a revisar.
            decision: "approve" o "reject".
            reviewer: Nombre/ID del investigador que revisa.
            notes: Notas opcionales de la revisión.

        Returns:
            La codificación actualizada, o None si no existe.
        """
        if decision not in {"approve", "reject"}:
            raise ValueError(f"Decisión inválida: {decision}. Use 'approve' o 'reject'.")

        coding = self._codings.get(coding_id)
        if coding is None:
            logger.warning("Codificación no encontrada para revisión: {cid}", cid=coding_id)
            return None

        if coding.status not in {"proposed", "under_review"}:
            logger.warning(
                "Codificación {cid} ya está en estado {status}, no se puede revisar",
                cid=coding_id,
                status=coding.status,
            )
            return coding

        new_status = "approved" if decision == "approve" else "rejected"
        now = datetime.now(timezone.utc).isoformat()

        coding.status = new_status
        coding.reviewed_by = reviewer
        coding.reviewed_at = now
        coding.updated_at = now
        if notes:
            coding.notes = (coding.notes or "") + f"\n[Revisión {reviewer}]: {notes}"

        logger.info(
            "Codificación revisada: {cid} | decisión={decision} | revisor={reviewer}",
            cid=coding_id[:8],
            decision=decision,
            reviewer=reviewer,
        )

        return coding

    def set_under_review(self, coding_id: str) -> Coding | None:
        """Marca una codificación como 'under_review' (lista para revisión humana)."""
        coding = self._codings.get(coding_id)
        if coding is None:
            return None
        if coding.status == "proposed":
            coding.status = "under_review"
            coding.updated_at = datetime.now(timezone.utc).isoformat()
            logger.info("Codificación {cid} enviada a revisión humana", cid=coding_id[:8])
        return coding

    def to_dataframe(self) -> Any:
        """Exporta todas las codificaciones a DataFrame de pandas."""
        import pandas as pd

        records = []
        for c in self._codings.values():
            records.append(
                {
                    "coding_id": c.coding_id,
                    "unit_id": c.unit_id,
                    "code_id": c.code_id,
                    "code": c.code,
                    "assigned_by": c.assigned_by,
                    "status": c.status,
                    "reviewed_by": c.reviewed_by,
                    "reviewed_at": c.reviewed_at,
                    "quote_literal": c.quote_literal,
                    "discourse_frame": c.discourse_frame,
                    "actors": "|".join(c.actors),
                    "oppositions": "|".join(c.oppositions),
                    "legitimization": c.legitimization,
                    "interpretation": c.interpretation,
                    "notes": c.notes,
                    "created_at": c.created_at,
                    "updated_at": c.updated_at,
                }
            )
        return pd.DataFrame(records)