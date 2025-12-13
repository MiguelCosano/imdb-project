from pydantic import BaseModel, ConfigDict


class Movie(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tconst: str
    primary_title: str
    original_title: str | None
    genres: str | None


class MovieResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    movies: list[Movie]


class Actor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nconst: str
    primary_name: str
    birth_year: int | None
    primary_profession: str | None
    is_dead: bool | None


class ActorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    actors: list[Actor]
