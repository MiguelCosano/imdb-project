from sqlalchemy import Column, Integer, String, Text

from core.database import Base

class Movie(Base):

    __tablename__="movies"

    tconst = Column(String(10), primary_key=True, index=True)
    primary_title = Column("primaryTitle", String(255), nullable=False, index=True)
    original_title = Column("originalTitle", String(255), nullable=True)
    genres = Column("genres", String(255), nullable=True)