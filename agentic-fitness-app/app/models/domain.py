from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    clerk_id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    
    diets = relationship("GeneratedDiet", back_populates="user")
    programs = relationship("GeneratedProgram", back_populates="user")

class GeneratedDiet(Base):
    __tablename__ = "generated_diets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.clerk_id"))
    diet_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="diets")

class GeneratedProgram(Base):
    __tablename__ = "generated_programs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.clerk_id"))
    program_json = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="programs")
