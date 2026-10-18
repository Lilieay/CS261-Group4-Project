from collections.abc import Mapping
from typing import Any, Protocol

from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload

from app.models.guide import Guide


class ModelDumpPayload(Protocol):
    def model_dump(self) -> dict[str, Any]: ...


GuideUpdateData = Mapping[str, object] | ModelDumpPayload

_EDITABLE_FIELDS = {
    "course_id",
    "title",
    "academic_year",
    "semester",
    "exam_period",
    "topics",
    "exam_format",
    "objective_count",
    "subjective_count",
    "additional_advice",
}


class UpdateOwnedGuideDAO:
    """Update an existing guide only when the supplied publisher owns it."""

    def __init__(self, session: Session):
        self.session = session

    def update_owned(
        self,
        guide_id: int,
        publisher_id: int,
        payload: GuideUpdateData,
    ) -> Guide | None:
        values = (
            dict(payload)
            if isinstance(payload, Mapping)
            else payload.model_dump()
        )
        unknown_fields = values.keys() - _EDITABLE_FIELDS
        if unknown_fields:
            raise ValueError(
                "Unsupported guide update fields: "
                + ", ".join(sorted(unknown_fields))
            )
        if not values:
            raise ValueError("Guide update payload must not be empty")

        statement = (
            update(Guide)
            .where(
                Guide.id == guide_id,
                Guide.publisher_id == publisher_id,
            )
            .values(**values)
            .execution_options(synchronize_session=False)
        )
        result = self.session.execute(statement)
        if result.rowcount != 1:
            return None

        refreshed = (
            select(Guide)
            .where(Guide.id == guide_id)
            .options(joinedload(Guide.course))
            .execution_options(populate_existing=True)
        )
        return self.session.scalars(refreshed).one()
