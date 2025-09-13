from pydantic import BaseModel, Field, ConfigDict


class Qor15Input(BaseModel):
    q1: int = Field(..., ge=0, le=10)
    q2: int = Field(..., ge=0, le=10)
    q3: int = Field(..., ge=0, le=10)
    q4: int = Field(..., ge=0, le=10)
    q5: int = Field(..., ge=0, le=10)
    q6: int = Field(..., ge=0, le=10)
    q7: int = Field(..., ge=0, le=10)
    q8: int = Field(..., ge=0, le=10)
    q9: int = Field(..., ge=0, le=10)
    q10: int = Field(..., ge=0, le=10)
    q11: int = Field(..., ge=0, le=10)
    q12: int = Field(..., ge=0, le=10)
    q13: int = Field(..., ge=0, le=10)
    q14: int = Field(..., ge=0, le=10)
    q15: int = Field(..., ge=0, le=10)


class Qor15Read(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scales_id: int
    q1: int
    q2: int
    q3: int
    q4: int
    q5: int
    q6: int
    q7: int
    q8: int
    q9: int
    q10: int
    q11: int
    q12: int
    q13: int
    q14: int
    q15: int
    total_score: int
