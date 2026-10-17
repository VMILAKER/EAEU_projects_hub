from pydantic import BaseModel, ConfigDict, Field


class Upload(BaseModel):
    number: int = Field(alias="№")
    project: str = Field(alias="Проект")
    direction: str | None = Field(alias="Направление")
    stage: str = Field(alias="Стадия")
    participants_russian: str | None = Field(alias="Российские участники")
    participants_belarus: str | None = Field(alias="Белорусские участники")
    key_facts: str | None = Field(alias="Ключевые факты")
    source: str | None = Field(alias="Источник")
    short_description: str | None = Field(alias="Краткое описание")

    model_config = ConfigDict(extra="forbid")