from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class ActorBase(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
    )

    nconst: str
    primary_name: str = Field(..., alias="primaryName")
    birth_year: Optional[int] = Field(None, alias="birthYear")
    primary_profession: Optional[str] = Field(None, alias="primaryProfession")