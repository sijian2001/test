from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from injector import inject
import logging
from .abstract_service import AbstractService, AbstractInDto, AbstractOutDto
from domain.repository.test2.product_info_repository import ProductInfoRepository
from domain.model.test2.product_info import ProductInfo

logging.basicConfig(level=logging.INFO)

@dataclass
class ProductInfoSearchInDto(AbstractInDto):
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    in_stock_only: Optional[bool] = None
    search_term: Optional[str] = None
    sort_by: Optional[str] = None  # "price", "stock", "name"
    sort_order: Optional[str] = "asc"  # "asc", "desc"

@dataclass
class ProductInfoOutDto(AbstractOutDto):
    product_info_list: List[ProductInfo]
    total_count: int

class AbstractProductInfoService(AbstractService):
    @abstractmethod
    def get_all_product_info(self) -> ProductInfoOutDto:
        pass

    @abstractmethod
    def search_product_info(self, in_dto: ProductInfoSearchInDto) -> ProductInfoOutDto:
        pass

    @abstractmethod
    def execute(self, in_dto: ProductInfoSearchInDto) -> ProductInfoOutDto:
        pass

@inject
@dataclass
class ProductInfoService(AbstractProductInfoService):
    product_info_repository: ProductInfoRepository

    def __post_init__(self):
        self.logger = logging.getLogger(__name__)

    def get_all_product_info(self) -> ProductInfoOutDto:
        self.logger.info("=== Getting All Product Info ===")

        product_info_list = self.product_info_repository.get_all_product_info()

        result_dto = ProductInfoOutDto(
            product_info_list=product_info_list,
            total_count=len(product_info_list)
        )

        self.logger.info(f"Retrieved {result_dto.total_count} product info records")
        self.logger.info("=== Get All Product Info Completed Successfully ===")

        return result_dto

    def search_product_info(self, in_dto: ProductInfoSearchInDto) -> ProductInfoOutDto:
        self.logger.info("=== Starting Product Info Search ===")

        product_info_list = []

        # Priority-based search logic
        if in_dto.product_id:
            self.logger.info(f"Searching by product_id: {in_dto.product_id}")
            product_info = self.product_info_repository.get_product_info_by_id(in_dto.product_id)
            if product_info:
                product_info_list = [product_info]
        elif in_dto.product_name:
            self.logger.info(f"Searching by product_name: {in_dto.product_name}")
            product_info = self.product_info_repository.get_product_info_by_name(in_dto.product_name)
            if product_info:
                product_info_list = [product_info]
        elif in_dto.category_id:
            self.logger.info(f"Searching by category_id: {in_dto.category_id}")
            product_info_list = self.product_info_repository.get_product_info_by_category(in_dto.category_id)
        elif in_dto.category_name:
            self.logger.info(f"Searching by category_name: {in_dto.category_name}")
            product_info_list = self.product_info_repository.get_product_info_by_category_name(in_dto.category_name)
        elif in_dto.min_price is not None or in_dto.max_price is not None:
            min_price = in_dto.min_price if in_dto.min_price is not None else 0.0
            max_price = in_dto.max_price if in_dto.max_price is not None else 999999.99
            self.logger.info(f"Searching by price range: {min_price} - {max_price}")
            product_info_list = self.product_info_repository.get_product_info_by_price_range(min_price, max_price)
        elif in_dto.search_term:
            self.logger.info(f"Searching by search term: {in_dto.search_term}")
            # Search in both product name and description
            name_results = self.product_info_repository.search_product_info_by_name(in_dto.search_term)
            desc_results = self.product_info_repository.search_product_info_by_description(in_dto.search_term)
            # Combine and deduplicate results
            product_info_list = self._deduplicate_product_info_list(name_results + desc_results)
        elif in_dto.in_stock_only is not None:
            if in_dto.in_stock_only:
                self.logger.info("Getting products in stock")
                product_info_list = self.product_info_repository.get_product_info_in_stock()
            else:
                self.logger.info("Getting products out of stock")
                product_info_list = self.product_info_repository.get_product_info_out_of_stock()
        else:
            self.logger.info("No specific search criteria provided, getting all product info")
            product_info_list = self.product_info_repository.get_all_product_info()

        # Apply sorting if specified
        if in_dto.sort_by and product_info_list:
            product_info_list = self._apply_sorting(product_info_list, in_dto.sort_by, in_dto.sort_order)

        result_dto = ProductInfoOutDto(
            product_info_list=product_info_list,
            total_count=len(product_info_list)
        )

        self.logger.info(f"Search completed - Found {result_dto.total_count} product info records")
        self.logger.info("=== Product Info Search Completed Successfully ===")

        return result_dto

    def execute(self, in_dto: ProductInfoSearchInDto) -> ProductInfoOutDto:
        return self.search_product_info(in_dto)

    def get_product_info_by_category_tree(self, parent_category_id: int) -> ProductInfoOutDto:
        """Get product info by parent category (including all subcategories)"""
        self.logger.info(f"=== Getting Product Info by Parent Category: {parent_category_id} ===")

        product_info_list = self.product_info_repository.get_product_info_by_parent_category(parent_category_id)

        result_dto = ProductInfoOutDto(
            product_info_list=product_info_list,
            total_count=len(product_info_list)
        )

        self.logger.info(f"Retrieved {result_dto.total_count} product info records for parent category")
        return result_dto

    def get_uncategorized_products(self) -> ProductInfoOutDto:
        """Get products without a category"""
        self.logger.info("=== Getting Uncategorized Products ===")

        product_info_list = self.product_info_repository.get_product_info_without_category()

        result_dto = ProductInfoOutDto(
            product_info_list=product_info_list,
            total_count=len(product_info_list)
        )

        self.logger.info(f"Retrieved {result_dto.total_count} uncategorized product records")
        return result_dto

    def get_product_statistics_by_category(self) -> dict:
        """Get product count statistics by category"""
        self.logger.info("=== Getting Product Statistics by Category ===")

        category_stats = self.product_info_repository.get_product_info_count_by_category()

        stats_dict = {}
        for category_name, count in category_stats:
            stats_dict[category_name] = count

        self.logger.info(f"Retrieved statistics for {len(stats_dict)} categories")
        return stats_dict

    def _deduplicate_product_info_list(self, product_info_list: List[ProductInfo]) -> List[ProductInfo]:
        """Remove duplicate ProductInfo objects based on product_id"""
        seen_ids = set()
        deduplicated_list = []

        for product_info in product_info_list:
            if product_info.product_id not in seen_ids:
                seen_ids.add(product_info.product_id)
                deduplicated_list.append(product_info)

        return deduplicated_list

    def _apply_sorting(self, product_info_list: List[ProductInfo], sort_by: str, sort_order: str) -> List[ProductInfo]:
        """Apply sorting to the product info list"""
        reverse = sort_order.lower() == "desc"

        if sort_by == "price":
            return sorted(product_info_list, key=lambda x: x.price or 0, reverse=reverse)
        elif sort_by == "stock":
            return sorted(product_info_list, key=lambda x: x.stock_quantity or 0, reverse=reverse)
        elif sort_by == "name":
            return sorted(product_info_list, key=lambda x: x.product_name or "", reverse=reverse)
        else:
            self.logger.warning(f"Unknown sort_by parameter: {sort_by}. Returning unsorted list.")
            return product_info_list