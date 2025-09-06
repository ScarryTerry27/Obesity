from sqlalchemy.orm import Session
from database.models import PersonScales, MouthOpening, Thyromental, Mallampati, NeckMobility, MandibleProtrusion, \
    WeightBand, DifficultIntubationHx, ElGanzouriResult
from database.repositories.elganzouri import ElGanzouriRepository
from database.repositories.person_scales import PersonScalesRepository

from database.schemas.elganzouri import ElGanzouriInput, ElGanzouriRead, ScalesStatusRead
from database.services.utils import NotFoundError


def _cls_mouth_opening(v: float) -> MouthOpening:
    return MouthOpening.GE_4_CM if v >= 4.0 else MouthOpening.LT_4_CM


def _cls_thyromental(v: float) -> Thyromental:
    if v > 6.5:
        return Thyromental.GT_6_5_CM
    if 6.0 <= v <= 6.5:
        return Thyromental.BW_6_0_6_5
    return Thyromental.LT_6_0_CM


def _cls_mallampati(v: int) -> Mallampati:
    if v == 1:
        return Mallampati.I
    if v == 2:
        return Mallampati.II
    return Mallampati.III  # III/IV


def _cls_neck_mobility(v: float) -> NeckMobility:
    if v > 90:
        return NeckMobility.GT_90_DEG
    if 80 <= v <= 90:
        return NeckMobility.BW_80_90
    return NeckMobility.LT_80_DEG


def _cls_mandible_protrusion(v: bool) -> MandibleProtrusion:
    return MandibleProtrusion.YES if v else MandibleProtrusion.NO


def _cls_weight_band(v: float) -> WeightBand:
    if v < 90:
        return WeightBand.LT_90_KG
    if v <= 110:
        return WeightBand.KG_90_110
    return WeightBand.GT_110_KG


def _cls_diff_hx(v: str) -> DifficultIntubationHx:
    m = {"Нет": DifficultIntubationHx.NO,
         "Недостоверно": DifficultIntubationHx.UNCERTAIN,
         "Определенно": DifficultIntubationHx.DEFINITE}
    return m.get(v, DifficultIntubationHx.NO)


class ElGanzouriService:
    """Бизнес-логика и транзакции для шкалы El-Ganzouri."""

    def __init__(self, session: Session):
        self.session = session
        self.ps_repo = PersonScalesRepository(session)
        self.elg_repo = ElGanzouriRepository(session)

    # вспомогательное
    def _get_or_create_person_scales(self, person_id: int) -> PersonScales:
        ps = self.ps_repo.get_by_person_id(person_id)
        if ps is None:
            ps = PersonScales(person_id=person_id)
            self.ps_repo.add(ps)
            self.session.flush()  # получим ps.id до коммита
        return ps

    # C/U (upsert)
    def upsert_result(self, person_id: int, data: ElGanzouriInput) -> ElGanzouriRead:
        ps = self._get_or_create_person_scales(person_id)

        res = self.elg_repo.get_by_scales_id(ps.id)
        if res is None:
            res = ElGanzouriResult(scales_id=ps.id)
            self.elg_repo.add(res)

        # map raw → enum
        res.mouth_opening = _cls_mouth_opening(data.interincisor_cm)
        res.thyromental = _cls_thyromental(data.thyromental_cm)
        res.mallampati = _cls_mallampati(data.mallampati_raw)
        res.neck_mobility = _cls_neck_mobility(data.neck_ext_deg)
        res.mandible_protrusion = _cls_mandible_protrusion(data.can_protrude)
        res.weight_band = _cls_weight_band(data.weight_kg)
        res.diff_intubation_hx = _cls_diff_hx(data.diff_hx)

        # keep raw
        res.interincisor_cm = data.interincisor_cm
        res.thyromental_cm = data.thyromental_cm
        res.neck_ext_deg = data.neck_ext_deg
        res.weight_kg = data.weight_kg
        res.mallampati_raw = data.mallampati_raw

        # статус в person_scales
        self.ps_repo.update_fields(ps, el_ganzouri_filled=True)

        self.session.commit()
        self.session.refresh(res)
        return ElGanzouriRead.model_validate(res)

    # R
    def get_result(self, person_id: int) -> ElGanzouriRead:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        res = self.elg_repo.get_by_scales_id(ps.id)
        if not res:
            raise NotFoundError("ElGanzouriResult not found")
        return ElGanzouriRead.model_validate(res)

    def get_status(self, person_id: int) -> ScalesStatusRead:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps or not ps.el_ganzouri_filled:
            return ScalesStatusRead(filled=False, total_score=None)
        res = self.elg_repo.get_by_scales_id(ps.id)
        score = res.total_score if res else None
        return ScalesStatusRead(filled=True, total_score=score)

    # D (опционально)
    def clear_result(self, person_id: int) -> bool:
        ps = self.ps_repo.get_by_person_id(person_id)
        if not ps:
            raise NotFoundError("PersonScales not found")
        affected = self.elg_repo.delete_by_scales_id(ps.id)
        # если удалили — сбросим флаг
        if affected:
            self.ps_repo.update_fields(ps, el_ganzouri_filled=False)
        self.session.commit()
        return bool(affected)
