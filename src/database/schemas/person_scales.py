from typing import Optional
from pydantic import BaseModel, ConfigDict


class PersonScalesRead(BaseModel):
    el_ganzouri_filled: bool = False
    ariscat_filled: bool = False
    stopbang_filled: bool = False
    soba_filled: bool = False
    lee_rcri_filled: bool = False
    caprini_filled: bool = False
    las_vegas_filled: bool = False
    qor15_filled: bool = False

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
    qor15_filled: Optional[bool] = None
