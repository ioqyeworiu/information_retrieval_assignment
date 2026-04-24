from sqlalchemy import Column, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship
from rag_module.util.database import Model
from datetime import datetime

class User(Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_img = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    birth = Column(Date, nullable=True)
    gender = Column(String, nullable=True)
    height = Column(Integer, nullable=True)
    weight = Column(Integer, nullable=True)
    goal = Column(String, nullable=True)
    health_condition = Column(String, nullable=True)
    workout_history = Column(String, nullable=True)
    practice_level = Column(String, nullable=True)
    excercise_favourite = Column(String, nullable=True)
    diet_favourite = Column(String, nullable=True)
    practice_plan = Column(String, nullable=True)
    routine = Column(String, nullable=True)

    created_at = Column(DateTime, nullable=True, default=datetime.now())
    updated_at = Column(DateTime, nullable=True, default=datetime.now(), onupdate=datetime.now())

    sessions = relationship("Session", back_populates="user")
    user_exercise_docs = relationship("UserExerciseDoc", back_populates="user")