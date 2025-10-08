from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from .base import Base


class ActiveUser(Base):
    __tablename__ = 'active_user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    department_id = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    def __repr__(self):
        return f"<ActiveUser(id={self.id}, username='{self.username}', email='{self.email}')>"
