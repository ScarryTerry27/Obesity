from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.models import SobaAssessment, PersonScales


class SobaRepository:
    """Чистый доступ к SOBA без бизнес-логики."""

    def __init__(self, session: Session):
        self.session = session

    # C
    def add(self, soba: SobaAssessment) -> SobaAssessment:
        self.session.add(soba)
        return soba

    # R
    def get_by_id(self, soba_id: int) -> Optional[SobaAssessment]:
        return self.session.get(SobaAssessment, soba_id)

    def get_by_scales_id(self, scales_id: int) -> Optional[SobaAssessment]:
        stmt = select(SobaAssessment).where(SobaAssessment.scales_id == scales_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_person_id(self, person_id: int) -> Optional[SobaAssessment]:
        # join через PersonScales
        stmt = (
            select(SobaAssessment)
            .join(PersonScales, PersonScales.id == SobaAssessment.scales_id)
            .where(PersonScales.person_id == person_id)
        )
        return self.session.execute(stmt).scalar_one_or_none()

    # U
    def update_fields(self, soba: SobaAssessment, **fields) -> SobaAssessment:
        for k, v in fields.items():
            if v is not None:
                setattr(soba, k, v)
        return soba

    # D
    def delete_by_scales_id(self, scales_id: int) -> int:
        soba = self.get_by_scales_id(scales_id)
        if not soba:
            return 0
        self.session.delete(soba)
        return 1
