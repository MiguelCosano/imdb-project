from sqlalchemy import Column, Integer, String, Boolean, Computed
from sqlalchemy.dialects.postgresql import TSVECTOR

from core.database import Base


class Actor(Base):

    __tablename__ = "actors"

    nconst = Column(String(10), primary_key=True, index=True)
    primary_name = Column("primary_name", String(255), nullable=False, index=True)
    birth_year = Column("birth_year", Integer, nullable=True)
    primary_profession = Column("primary_profession", String(255), nullable=True)
    is_dead = Column("is_dead", Boolean, nullable=True)
    search_vector = Column(
        TSVECTOR, Computed("to_tsvector('english', coalesce(primary_name, ''))")
    )
