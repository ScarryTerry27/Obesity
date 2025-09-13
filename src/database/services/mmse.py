from sqlalchemy.orm import Session

from database.models import PersonScales, MMSEResult
from database.repositories.person_scales import PersonScalesRepository
from database.repositories.mmse import MMSERepository
from database.schemas.mmse import MMSEInput, MMSEResultRead
from database.services.utils import NotFoundError


MMSE_FIELDS = [
    'orientation_date', 'orientation_month', 'orientation_year', 'orientation_weekday',
    'orientation_season', 'orientation_city', 'orientation_region', 'orientation_institution',
    'orientation_floor', 'orientation_country',
    'registration_ball1', 'registration_ball2', 'registration_ball3',
    'attention_93', 'attention_86', 'attention_79', 'attention_72', 'attention_65',
    'recall_ball1', 'recall_ball2', 'recall_ball3',
    'language_clock', 'language_pen', 'language_repeat',
    'command_take_paper', 'command_fold_paper', 'command_put_on_knee',
    'reading_close_eyes', 'writing_sentence', 'copying_pentagons'
]


class MMSEService:
    """Upsert/get/clear MMSE results for t0 and t10."""

    def __init__(self, session: Session):
        self.session = session
        self.ps_repo = PersonScalesRepository(session)
        self.repo = MMSERepository(session)

    def _get_or_create_ps(self, person_id: int) -> PersonScales:
        ps = self.ps_repo.get_by_person_id(person_id)
        if ps is None:
            ps = PersonScales(person_id=person_id)
            self.ps_repo.add(ps)
            self.session.flush()
        return ps

    def upsert_result(self, person_id: int, timepoint: int, data: MMSEInput) -> MMSEResultRead:
        ps = self._get_or_create_ps(person_id)
        res = self.repo.get_by_scales_and_time(ps.id, timepoint)
        if res is None:
            res = MMSEResult(scales_id=ps.id, timepoint=timepoint)
            self.repo.add(res)

        for field in MMSE_FIELDS:
            setattr(res, field, int(getattr(data, field)))

        res.total_score = sum(getattr(res, f) for f in MMSE_FIELDS)

        if timepoint == 0:
            self.ps_repo.update_fields(ps, mmse_t0_filled=True)
        elif timepoint == 10:
            self.ps_repo.update_fields(ps, mmse_t10_filled=True)

        self.session.commit()
        self.session.refresh(res)
        self.session.refresh(ps)
        return MMSEResultRead.model_validate(res)

    def get_result(self, person_id: int, timepoint: int) -> MMSEResultRead:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        res = self.repo.get_by_scales_and_time(ps.id, timepoint)
        if not res:
            raise NotFoundError("MMSEResult not found")
        return MMSEResultRead.model_validate(res)

    def clear_result(self, person_id: int, timepoint: int) -> bool:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        affected = self.repo.delete_by_scales_and_time(ps.id, timepoint)
        if affected:
            if timepoint == 0:
                self.ps_repo.update_fields(ps, mmse_t0_filled=False)
            elif timepoint == 10:
                self.ps_repo.update_fields(ps, mmse_t10_filled=False)
        self.session.commit()
        return bool(affected)
