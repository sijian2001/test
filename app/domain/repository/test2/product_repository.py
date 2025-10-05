from dataclasses import dataclass
from typing import List, Optional
from injector import inject
from app.domain.database import Test2DatabaseSession
from app.domain.model.test2.product import Product


@inject
@dataclass
class ProductRepository:
    db_session: Test2DatabaseSession

    def __post_init__(self):
        pass

    def get_all_products(self) -> List[Product]:
        """Get all products"""
        session = self.db_session
        return session.query(Product).all()

    def get_product_by_id(self, product_id: int) -> Optional[Product]:
        """Get product by ID"""
        session = self.db_session
        return session.query(Product).filter(Product.product_id == product_id).first()

    def get_product_by_name(self, product_name: str) -> Optional[Product]:
        """Get product by name"""
        session = self.db_session
        return session.query(Product).filter(Product.product_name == product_name).first()

    def get_products_by_category(self, category_id: int) -> List[Product]:
        """Get products by category ID"""
        session = self.db_session
        return session.query(Product).filter(Product.category_id == category_id).all()

    def get_products_by_price_range(self, min_price: float, max_price: float) -> List[Product]:
        """Get products by price range"""
        session = self.db_session
        return session.query(Product).filter(
            Product.price >= min_price,
            Product.price <= max_price
        ).all()

    def get_products_in_stock(self) -> List[Product]:
        """Get products that are in stock"""
        session = self.db_session
        return session.query(Product).filter(Product.stock_quantity > 0).all()

    def get_products_out_of_stock(self) -> List[Product]:
        """Get products that are out of stock"""
        session = self.db_session
        return session.query(Product).filter(Product.stock_quantity <= 0).all()

    def search_products_by_name(self, search_term: str) -> List[Product]:
        """Search products by name (partial match)"""
        session = self.db_session
        return session.query(Product).filter(
            Product.product_name.like(f"%{search_term}%")
        ).all()

    def create_product(self, product: Product) -> Product:
        """Create a new product"""
        session = self.db_session
        session.add(product)
        session.flush()
        session.refresh(product)
        return product

    def update_product(self, product: Product) -> Product:
        """Update an existing product"""
        session = self.db_session
        session.merge(product)
        session.flush()
        return product

    def update_stock_quantity(self, product_id: int, new_quantity: int) -> bool:
        """Update stock quantity for a product"""
        session = self.db_session
        product = self.get_product_by_id(product_id)
        if product:
            product.stock_quantity = new_quantity
            session.flush()
            return True
        return False

    def delete_product(self, product_id: int) -> bool:
        """Delete a product by ID"""
        session = self.db_session
        product = self.get_product_by_id(product_id)
        if product:
            session.delete(product)
            session.flush()
            return True
        return False