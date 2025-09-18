from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, TIMESTAMP
from sqlalchemy.sql import func
from .base import Base

class Department(Base):
    __tablename__ = 'department'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    manager_id = Column(Integer)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}')>"