from sqlalchemy import Column, Float, Integer, String

from database import Base


class Recipe(Base):
    __tablename__ = "Recipe"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    number_of_views = Column(Integer, index=True, default=0)
    cooking_time = Column(Float, index=True)
    ingredients = Column(String, index=True)
    description = Column(String, index=True)
