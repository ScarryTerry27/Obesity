from sqlalchemy.orm import Session
from database.models import SobaAssessment
from database.repositories.soba import SobaRepository
from database.repositories.person_scales import PersonScalesRepository
from database.services.utils import NotFoundError
from database.schemas.soba import SobaCreate, SobaUpdate, SobaRead


class SobaService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = SobaRepository(session)
        self.scales_repo = PersonScalesRepository(session)

    def _ensure_scales(self, person_id: int):
        # создаёт при отсутствии + flush() => ps.id гарантирован
        return self.scales_repo.get_or_create_for_person(person_id)

    def _maybe_cache_stopbang(self, soba: SobaAssessment, ps) -> None:
        if getattr(ps, "stopbang", None):
            soba.stopbang_score_cached = getattr(ps.stopbang, "total_score", None)
            soba.stopbang_risk_cached = getattr(ps.stopbang, "risk_level", None)

    def upsert_for_person(self, person_id: int, data: SobaCreate | SobaUpdate) -> SobaRead:
        ps = self._ensure_scales(person_id)

        soba = self.repo.get_by_scales_id(ps.id)
        payload = data.model_dump(exclude_unset=True)

        if soba is None:
            # ПРИВЯЗЫВАЕМ ЧЕРЕЗ RELATIONSHIP, а не через scales_id
            soba = SobaAssessment(scales=ps, **payload)
            self._maybe_cache_stopbang(soba, ps)
            self.session.add(soba)
            ps.soba_filled = True
        else:
            self.repo.update_fields(soba, **payload)
            if soba.stopbang_score_cached is None or soba.stopbang_risk_cached is None:
                self._maybe_cache_stopbang(soba, ps)
            ps.soba_filled = True

        # гарантируем, что всё пронумеровано до коммита
        self.session.flush()
        self.session.commit()
        self.session.refresh(soba)
        self.session.refresh(ps)
        return SobaRead.model_validate(soba)

    def get_for_person(self, person_id: int) -> SobaRead:
        ps = self.scales_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError(f"SOBA for person #{person_id} not found")
        soba = self.repo.get_by_scales_id(ps.id)
        if not soba:
            raise NotFoundError(f"SOBA for person #{person_id} not found")
        return SobaRead.model_validate(soba)

    def delete_for_person(self, person_id: int) -> bool:
        ps = self.scales_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError(f"PersonScales for person #{person_id} not found")
        affected = self.repo.delete_by_scales_id(ps.id)
        if affected:
            ps.soba_filled = False
            self.session.commit()
            return True
        return False
