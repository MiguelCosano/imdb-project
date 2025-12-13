from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ActorBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    nconst: str
    primary_name: str = Field(...)
    birth_year: Optional[int] = Field(None)
    primary_profession: Optional[str] = Field(None)
    is_dead: Optional[bool] = Field(None)
