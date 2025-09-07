from typing import Optional

from pydantic import BaseModel


class PersonSlicesRead(BaseModel):
    t0_filled: bool = False
    t1_filled: bool = False
    t2_filled: bool = False
    t3_filled: bool = False
    t4_filled: bool = False
    t5_filled: bool = False
    t6_filled: bool = False
    t7_filled: bool = False
    t8_filled: bool = False
    t9_filled: bool = False
    t10_filled: bool = False
    t11_filled: bool = False
    t12_filled: bool = False

    class Config:
        from_attributes = True


class PersonSlicesUpdate(BaseModel):
    t0_filled: Optional[bool] = None
    t1_filled: Optional[bool] = None
    t2_filled: Optional[bool] = None
    t3_filled: Optional[bool] = None
    t4_filled: Optional[bool] = None
    t5_filled: Optional[bool] = None
    t6_filled: Optional[bool] = None
    t7_filled: Optional[bool] = None
    t8_filled: Optional[bool] = None
    t9_filled: Optional[bool] = None
    t10_filled: Optional[bool] = None
    t11_filled: Optional[bool] = None
    t12_filled: Optional[bool] = None

