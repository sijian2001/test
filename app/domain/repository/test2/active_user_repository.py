from dataclasses import dataclass
from typing import List, Optional
from injector import inject
from app.domain.database import Test2DatabaseSession
from app.domain.model.test2.active_user import ActiveUser


@inject
@dataclass
class ActiveUserRepository:
    db_session: Test2DatabaseSession

    def __post_init__(self):
        pass

    def get_all_active_users(self) -> List[ActiveUser]:
        """Get all active users"""
        session = self.db_session
        return session.query(ActiveUser).all()

    def get_active_user_by_id(self, user_id: int) -> Optional[ActiveUser]:
        """Get active user by ID"""
        session = self.db_session
        return session.query(ActiveUser).filter(ActiveUser.id == user_id).first()

    def get_active_user_by_username(self, username: str) -> Optional[ActiveUser]:
        """Get active user by username"""
        session = self.db_session
        return session.query(ActiveUser).filter(ActiveUser.username == username).first()

    def get_active_user_by_email(self, email: str) -> Optional[ActiveUser]:
        """Get active user by email"""
        session = self.db_session
        return session.query(ActiveUser).filter(ActiveUser.email == email).first()

    def get_active_users_by_department(self, department_id: int) -> List[ActiveUser]:
        """Get active users by department ID"""
        session = self.db_session
        return session.query(ActiveUser).filter(ActiveUser.department_id == department_id).all()

    def search_active_users_by_name(self, search_term: str) -> List[ActiveUser]:
        """Search active users by first name or last name (partial match)"""
        session = self.db_session
        return session.query(ActiveUser).filter(
            (ActiveUser.first_name.like(f"%{search_term}%")) |
            (ActiveUser.last_name.like(f"%{search_term}%"))
        ).all()

    def create_active_user(self, username: str, email: str, first_name: str = None,
                          last_name: str = None, department_id: int = None) -> ActiveUser:
        """Create a new active user"""
        session = self.db_session
        active_user = ActiveUser(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            department_id=department_id
        )
        session.add(active_user)
        session.flush()
        session.refresh(active_user)
        return active_user

    def update_active_user(self, user_id: int, username: str = None, email: str = None,
                          first_name: str = None, last_name: str = None,
                          department_id: int = None) -> Optional[ActiveUser]:
        """Update an existing active user"""
        session = self.db_session
        active_user = self.get_active_user_by_id(user_id)
        if active_user:
            if username:
                active_user.username = username
            if email:
                active_user.email = email
            if first_name is not None:
                active_user.first_name = first_name
            if last_name is not None:
                active_user.last_name = last_name
            if department_id is not None:
                active_user.department_id = department_id
            session.flush()
            session.refresh(active_user)
        return active_user

    def delete_active_user(self, user_id: int) -> bool:
        """Delete an active user by ID"""
        session = self.db_session
        active_user = self.get_active_user_by_id(user_id)
        if active_user:
            session.delete(active_user)
            session.flush()
            return True
        return False

    def delete_all_active_users(self) -> int:
        """Delete all active users"""
        session = self.db_session
        count = session.query(ActiveUser).count()
        session.query(ActiveUser).delete()
        session.flush()
        return count
