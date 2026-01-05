"""SQLAlchemy models for the platform database."""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Float, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

Base = declarative_base()

"""Association table for Perimeter-Department many-to-many relationship."""
perimeter_departments = Table(
    'perimeter_departments',
    Base.metadata,
    Column('perimeter_id', Integer, ForeignKey('perimeters.id'), primary_key=True),
    Column('department_id', Float, ForeignKey('departments.id'), primary_key=True)
)

"""Organisation model."""
class Department(Base):    
    __tablename__ = 'departments'    
    id = Column(Float, primary_key=True, autoincrement=False)
    name = Column(String(255), nullable=False)

class Perimeter(Base):
    __tablename__ = 'perimeters'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    departments = relationship("Department", secondary=perimeter_departments)

class ACL(Base):
    __tablename__ = 'acls'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(255), nullable=False)
    perimeter_id = Column(Integer, ForeignKey('perimeters.id'), nullable=True)
    department_id = Column(Float, ForeignKey('departments.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    perimeter = relationship("Perimeter")
    department = relationship("Department")