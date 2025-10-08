from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from injector import inject
import logging
from app.business.abstract_service import AbstractService, AbstractInDto, AbstractOutDto
from app.business.decorators.transactional import Transactional
from app.business.decorators.database_enum import Database
from app.domain.repository.test2.product_repository import ProductRepository
from app.domain.model.test2.product import Product
from app.business.vo.product_vo import ProductVo

logging.basicConfig(level=logging.INFO)

@dataclass
class ProductRegistInDto(AbstractInDto):
    productList: List[ProductVo]

@dataclass
class ProductRegistOutDto(AbstractOutDto):
    productCount: int

class AbstractProductRegistService(AbstractService):
    @abstractmethod
    def execute(self, in_dto: ProductRegistInDto) -> ProductRegistOutDto:
        pass

@inject
@dataclass
class ProductRegistService(AbstractProductRegistService):
    product_repository: ProductRepository

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    @Transactional(database=Database.TEST2)
    def execute(self, in_dto: ProductRegistInDto) -> ProductRegistOutDto:
        self.logger.info("=== Starting Product Registration ===")

        products_registered = 0
        for product_vo in in_dto.productList:
            try:
                # Create Product entity from VO
                product = Product(
                    product_name=product_vo.product_name,
                    description=product_vo.description,
                    price=product_vo.price,
                    stock_quantity=product_vo.stock_quantity,
                    category_id=product_vo.category_id
                )

                self.product_repository.create_product(product)
                products_registered += 1
                self.logger.info(f"Registered product: {product_vo.product_name}")
            except Exception as e:
                self.logger.error(f"Failed to register product {product_vo.product_name}: {str(e)}")
                raise

        self.logger.info(f"Successfully registered {products_registered} products")
        self.logger.info("=== Product Registration Completed Successfully ===")

        # Create and return result DTO
        result_dto = ProductRegistOutDto(
            productCount=products_registered
        )

        return result_dto