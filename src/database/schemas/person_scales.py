from typing import Optional
from pydantic import BaseModel, ConfigDict
from database.schemas.mmse import MMSEResultRead


class PersonScalesRead(BaseModel):
    el_ganzouri_filled: bool = False
    ariscat_filled: bool = False
    stopbang_filled: bool = False
    soba_filled: bool = False
    lee_rcri_filled: bool = False
    caprini_filled: bool = False
    las_vegas_filled: bool = False
    aldrete_filled: bool = False
    mmse_t0_filled: bool = False
    mmse_t10_filled: bool = False
    mmse_results: list[MMSEResultRead] | None = None

    class Config:
        from_attributes = True


class PersonScalesUpdate(BaseModel):
    # все поля опциональные — обновляем только переданные
    el_ganzouri_filled: Optional[bool] = None
    ariscat_filled: Optional[bool] = None
    soba_stopbang_filled: Optional[bool] = None
    lee_rcri_filled: Optional[bool] = None
    caprini_filled: Optional[bool] = None
    las_vegas_filled: Optional[bool] = None
    mmse_t0_filled: Optional[bool] = None
    mmse_t10_filled: Optional[bool] = None
    aldrete_filled: Optional[bool] = None
