from pydantic import BaseModel, ConfigDict


class AldreteInput(BaseModel):
    activity_score: int
    respiration_score: int
    pressure_score: int
    consciousness_score: int
    spo2_score: int


class AldreteRead(AldreteInput):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scales_id: int
    total_score: int
