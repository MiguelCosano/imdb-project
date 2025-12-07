from sqlalchemy import Column, Integer, String

from core.database import Base

class Actor(Base):

    __tablename__="actors"

    nconst = Column(String(10), primary_key=True, index=True)
    primary_name = Column("primaryName", String(255), nullable=False, index=True)
    birth_year = Column("birthYear", Integer, nullable=True)
    primary_profession = Column("primaryProfession", String(255), nullable=True)