from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from .base import Base

class UserInfo(Base):
    __tablename__ = 'user_info'

    user_id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    department_name = Column(String(100))
    manager_id = Column(Integer)
    is_active = Column(String(10))
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)

    def __repr__(self):
        return f"<UserInfo(user_id={self.user_id}, username='{self.username}', department='{self.department_name}')>"