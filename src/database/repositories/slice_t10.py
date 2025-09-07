from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from database.models import SliceT10


class SliceT10Repository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_slices_id(self, slices_id: int) -> SliceT10 | None:
        stmt = select(SliceT10).where(SliceT10.slices_id == slices_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, obj: SliceT10) -> SliceT10:
        self.session.add(obj)
        return obj

    def update_fields(self, obj: SliceT10, **fields) -> SliceT10:
        for k, v in fields.items():
            if v is not None:
                setattr(obj, k, v)
        return obj

    def delete_by_slices_id(self, slices_id: int) -> int:
        stmt = delete(SliceT10).where(SliceT10.slices_id == slices_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0
