"""SQLAlchemy models for the platform database."""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

"""Organisation model."""
class Department(Base):    
    __tablename__ = 'departments'    
    id = Column(Float, primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=False)

class Perimeter(Base):
    __tablename__ = 'perimeters'
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=False)
    department_id = Column(Float, ForeignKey('departments.id'), nullable=False)
    department = relationship("Department")

class ACL(Base):
    __tablename__ = 'acls'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False)
    perimeter_id = Column(Integer, ForeignKey('perimeters.id'), nullable=True)
    department_id = Column(Float, ForeignKey('departments.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    perimeter = relationship("Perimeter")
    department = relationship("Department")