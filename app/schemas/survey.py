"""Pydantic schemas for the parser pipeline — SurveyModel contract."""
from pydantic import BaseModel, Field


class SurveyProject(BaseModel):
    name: str


class SurveyFloor(BaseModel):
    id: str
    name: str
    image_ref: str | None = None


class SurveyRadio(BaseModel):
    band: str
    channel: int | None = None
    tx_power: float | None = None


class SurveyAP(BaseModel):
    name: str
    model: str | None = None
    vendor: str | None = None
    floor_id: str | None = None
    x: float | None = None
    y: float | None = None
    radios: list[SurveyRadio] = Field(default_factory=list)


class SurveyModel(BaseModel):
    project: SurveyProject
    floors: list[SurveyFloor] = Field(default_factory=list)
    aps: list[SurveyAP] = Field(default_factory=list)
    source_filename: str


class ParsedSurveyFile(BaseModel):
    survey_file_id: int
    filename: str
    survey: SurveyModel | None = None
    error: str | None = None


def floor_name_for(survey: SurveyModel, floor_id: str | None) -> str:
    """Resolve floor_id to display name; fall back to raw id or em dash."""
    if floor_id is None:
        return "—"
    for floor in survey.floors:
        if floor.id == floor_id:
            return floor.name
    return floor_id
