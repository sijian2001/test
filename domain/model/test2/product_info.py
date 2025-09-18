from sqlalchemy import Column, Integer, String, Text, DECIMAL, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from .base import Base


class ProductInfo(Base):
    __tablename__ = 'product_info'

    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    category_id = Column(Integer, ForeignKey('categories.category_id'))
    category_name = Column(String(255))
    category_description = Column(Text)
    parent_category_id = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    def __repr__(self):
        return f"<ProductInfo(product_id={self.product_id}, product_name='{self.product_name}', category_name='{self.category_name}', price={self.price})>"