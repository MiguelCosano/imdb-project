from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class MovieBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    tconst: str
    primary_title: str = Field(...)
    original_title: Optional[str] = Field(None)
    genres: Optional[str] = Field(None)
