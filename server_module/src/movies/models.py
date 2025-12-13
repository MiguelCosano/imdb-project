from sqlalchemy import Column, Computed, String, Text
from sqlalchemy.dialects.postgresql import TSVECTOR

from core.database import Base


class Movie(Base):

    __tablename__ = "movies"

    tconst = Column(String(10), primary_key=True, index=True)
    primary_title = Column("primary_title", String(255), nullable=False, index=True)
    original_title = Column("original_title", String(255), nullable=True)
    genres = Column("genres", String(255), nullable=True)
    search_vector = Column(
        TSVECTOR, Computed("to_tsvector('english', coalesce(primary_name, ''))")
    )
