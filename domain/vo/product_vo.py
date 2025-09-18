from dataclasses import dataclass
from typing import Optional


@dataclass
class ProductVo:
    product_name: str
    description: Optional[str]
    price: float
    stock_quantity: int
    category_id: Optional[int]