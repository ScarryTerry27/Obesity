from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from database.models import SliceT1


class SliceT1Repository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_slices_id(self, slices_id: int) -> SliceT1 | None:
        stmt = select(SliceT1).where(SliceT1.slices_id == slices_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def add(self, obj: SliceT1) -> SliceT1:
        self.session.add(obj)
        return obj

    def update_fields(self, obj: SliceT1, **fields) -> SliceT1:
        for k, v in fields.items():
            if v is not None:
                setattr(obj, k, v)
        return obj

    def delete_by_slices_id(self, slices_id: int) -> int:
        stmt = delete(SliceT1).where(SliceT1.slices_id == slices_id)
        res = self.session.execute(stmt)
        return res.rowcount or 0
