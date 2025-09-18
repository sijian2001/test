from dataclasses import dataclass
from typing import List, Optional
from injector import inject
from domain.database import DatabaseSession
from domain.model.test2.product_info import ProductInfo


@inject
@dataclass
class ProductInfoRepository:
    db_session: DatabaseSession

    def __post_init__(self):
        pass

    def get_all_product_info(self) -> List[ProductInfo]:
        """Get all product info with category details"""
        session = self.db_session.get_session("test2")
        return session.query(ProductInfo).all()

    def get_product_info_by_id(self, product_id: int) -> Optional[ProductInfo]:
        """Get product info by product ID"""
        session = self.db_session.get_session("test2")
        return session.query(ProductInfo).filter(ProductInfo.product_id == product_id).first()

    def get_product_info_by_name(self, product_name: str) -> Optional[ProductInfo]:
        """Get product info by product name"""
        session = self.db_session.get_session("test2")
        return session.query(ProductInfo).filter(ProductInfo.product_name == product_name).first()

    def get_product_info_by_category(self, category_id: int) -> List[ProductInfo]:
        """Get product info by category ID"""
        session = self.db_session.get_session("test2")
        return session.query(ProductInfo).filter(ProductInfo.category_id == category_id).all()

    def get_product_info_by_category_name(self, category_name: str) -> List[ProductInfo]:
        """Get product info by category name"""
        session = self.db_session.get_session("test2")
        return session.query(ProductInfo).filter(ProductInfo.category_name == category_name).all()

    def get_product_info_by_price_range(self, min_price: float, max_price: float) -> List[ProductInfo]:
        """Get product info by price range"""
        session = self.db_session.get_session("test2")
        return session.query(ProductInfo).filter(
            ProductInfo.price >= min_price,
            ProductInfo.price <= max_price
        ).all()

    def get_product_info_in_stock(self) -> List[ProductInfo]:
        """Get product info for products that are in stock"""
        session = self.db_session.get_session("test2")
        return session.query(ProductInfo).filter(ProductInfo.stock_quantity > 0).all()

    def get_product_info_out_of_stock(self) -> List[ProductInfo]:
        """Get product info for products that are out of stock"""
        session = self.db_session.get_session("test2")
        return session.query(ProductInfo).filter(ProductInfo.stock_quantity <= 0).all()

    def search_product_info_by_name(self, search_term: str) -> List[ProductInfo]:
        """Search product info by product name (partial match)"""
        session = self.db_session.get_session("test2")
        return session.query(ProductInfo).filter(
            ProductInfo.product_name.like(f"%{search_term}%")
        ).all()

    def search_product_info_by_description(self, search_term: str) -> List[ProductInfo]:
        """Search product info by product description (partial match)"""
        session = self.db_session.get_session("test2")
        return session.query(ProductInfo).filter(
            ProductInfo.description.like(f"%{search_term}%")
        ).all()

    def get_product_info_by_parent_category(self, parent_category_id: int) -> List[ProductInfo]:
        """Get product info by parent category ID"""
        session = self.db_session.get_session("test2")
        return session.query(ProductInfo).filter(ProductInfo.parent_category_id == parent_category_id).all()

    def get_product_info_without_category(self) -> List[ProductInfo]:
        """Get product info for products without a category"""
        session = self.db_session.get_session("test2")
        return session.query(ProductInfo).filter(ProductInfo.category_id.is_(None)).all()

    def get_product_info_sorted_by_price(self, ascending: bool = True) -> List[ProductInfo]:
        """Get all product info sorted by price"""
        session = self.db_session.get_session("test2")
        if ascending:
            return session.query(ProductInfo).order_by(ProductInfo.price.asc()).all()
        else:
            return session.query(ProductInfo).order_by(ProductInfo.price.desc()).all()

    def get_product_info_sorted_by_stock(self, ascending: bool = True) -> List[ProductInfo]:
        """Get all product info sorted by stock quantity"""
        session = self.db_session.get_session("test2")
        if ascending:
            return session.query(ProductInfo).order_by(ProductInfo.stock_quantity.asc()).all()
        else:
            return session.query(ProductInfo).order_by(ProductInfo.stock_quantity.desc()).all()

    def get_product_info_sorted_by_name(self, ascending: bool = True) -> List[ProductInfo]:
        """Get all product info sorted by product name"""
        session = self.db_session.get_session("test2")
        if ascending:
            return session.query(ProductInfo).order_by(ProductInfo.product_name.asc()).all()
        else:
            return session.query(ProductInfo).order_by(ProductInfo.product_name.desc()).all()

    def get_product_info_count_by_category(self) -> List[tuple]:
        """Get product count by category"""
        session = self.db_session.get_session("test2")
        return session.query(
            ProductInfo.category_name,
            session.query(ProductInfo).filter(
                ProductInfo.category_name == ProductInfo.category_name
            ).count().label('product_count')
        ).group_by(ProductInfo.category_name).all()