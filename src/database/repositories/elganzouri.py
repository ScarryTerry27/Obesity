from sqlalchemy.orm import Session
from sqlalchemy import select, delete

from database.models import ElGanzouriResult


class ElGanzouriRepository:
    """CRUD для el_ganzouri_results без бизнес-логики."""

    def __init__(self, session: Session):
        self.session = session

    def get_by_scales_id(self, scales_id: int) -> ElGanzouriResult | None:
        stmt = select(ElGanzouriResult).where(ElGanzouriResult.scales_id == scales_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, res: ElGanzouriResult) -> ElGanzouriResult:
        self.session.add(res)
        return res

    def delete_by_scales_id(self, scales_id: int) -> int:
        stmt = delete(ElGanzouriResult).where(ElGanzouriResult.scales_id == scales_id)
        result = self.session.execute(stmt)
        return result.rowcount or 0
