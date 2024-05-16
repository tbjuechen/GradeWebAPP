from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime

from config import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)

    judge = relationship('Grade', back_populates="user")

class Photo(Base):
    __tablename__ = 'photos'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    location = Column(String)

    candidate = relationship('Grade', back_populates='photo')

class Grade(Base):
    __tablename__ = 'grades'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    photo_id = Column(Integer, ForeignKey("photos.id"))
    grade = Column(Integer)
    create_at = Column(DateTime)

    user = relationship('User',back_populates='judge')
    photo = relationship('Photo',back_populates='candidate')

    
