from app.database import Base
from sqlalchemy import Column, Integer, String, Enum, DateTime
from datetime import datetime

class Ingredient(Base):
    __tablename__ = "ingredients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    tag = Column(String, nullable=True)
    amount = Column(Integer, nullable=False)
    unit_majar = Column(String, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())