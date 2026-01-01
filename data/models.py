"""SQLAlchemy models for the platform database."""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

class Department(Base):
    """Organisation model."""
    
    __tablename__ = 'departments'
    
    id = Column(Float, primary_key=True, default=lambda: uuid.uuid4().int)
    name = Column(String(255), nullable=False)