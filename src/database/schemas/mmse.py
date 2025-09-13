from pydantic import BaseModel, ConfigDict


class MMSEInput(BaseModel):
    orientation_date: bool
    orientation_month: bool
    orientation_year: bool
    orientation_weekday: bool
    orientation_season: bool
    orientation_city: bool
    orientation_region: bool
    orientation_institution: bool
    orientation_floor: bool
    orientation_country: bool

    registration_ball1: bool
    registration_ball2: bool
    registration_ball3: bool

    attention_93: bool
    attention_86: bool
    attention_79: bool
    attention_72: bool
    attention_65: bool

    recall_ball1: bool
    recall_ball2: bool
    recall_ball3: bool

    language_clock: bool
    language_pen: bool
    language_repeat: bool

    command_take_paper: bool
    command_fold_paper: bool
    command_put_on_knee: bool

    reading_close_eyes: bool
    writing_sentence: bool
    copying_pentagons: bool


class MMSEResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    scales_id: int
    timepoint: int

    orientation_date: bool
    orientation_month: bool
    orientation_year: bool
    orientation_weekday: bool
    orientation_season: bool
    orientation_city: bool
    orientation_region: bool
    orientation_institution: bool
    orientation_floor: bool
    orientation_country: bool

    registration_ball1: bool
    registration_ball2: bool
    registration_ball3: bool

    attention_93: bool
    attention_86: bool
    attention_79: bool
    attention_72: bool
    attention_65: bool

    recall_ball1: bool
    recall_ball2: bool
    recall_ball3: bool

    language_clock: bool
    language_pen: bool
    language_repeat: bool

    command_take_paper: bool
    command_fold_paper: bool
    command_put_on_knee: bool

    reading_close_eyes: bool
    writing_sentence: bool
    copying_pentagons: bool

    total_score: int
