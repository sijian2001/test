from dataclasses import dataclass
from typing import List, Optional
from injector import inject
from app.domain.database import Test2DatabaseSession
from app.domain.model.test2.category import Category


@inject
@dataclass
class CategoryRepository:
    db_session: Test2DatabaseSession

    def __post_init__(self):
        pass

    def get_all_categories(self) -> List[Category]:
        """Get all categories"""
        session = self.db_session
        return session.query(Category).all()

    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        session = self.db_session
        return session.query(Category).filter(Category.category_id == category_id).first()

    def get_category_by_name(self, category_name: str) -> Optional[Category]:
        """Get category by name"""
        session = self.db_session
        return session.query(Category).filter(Category.category_name == category_name).first()

    def get_categories_by_parent(self, parent_category_id: Optional[int]) -> List[Category]:
        """Get categories by parent category ID"""
        session = self.db_session
        return session.query(Category).filter(Category.parent_category_id == parent_category_id).all()

    def get_root_categories(self) -> List[Category]:
        """Get root categories (categories with no parent)"""
        session = self.db_session
        return session.query(Category).filter(Category.parent_category_id.is_(None)).all()

    def create_category(self, category: Category) -> Category:
        """Create a new category"""
        session = self.db_session
        session.add(category)
        session.flush()
        session.refresh(category)
        return category

    def update_category(self, category: Category) -> Category:
        """Update an existing category"""
        session = self.db_session
        session.merge(category)
        session.flush()
        return category

    def delete_category(self, category_id: int) -> bool:
        """Delete a category by ID"""
        session = self.db_session
        category = self.get_category_by_id(category_id)
        if category:
            session.delete(category)
            session.flush()
            return True
        return False