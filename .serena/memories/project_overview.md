# Project Overview

## Project Purpose
Dual-database Python batch processing application for:
- **test1 database**: User management system (users, departments)
- **test2 database**: Product management system (products, categories)
- CSV import/export functionality
- Clean architecture with dependency injection

## Tech Stack
- **Language**: Python 3.8+
- **ORM**: SQLAlchemy 2.0+
- **Database**: MySQL 5.7+ (dual databases: test1, test2)
- **Dependency Injection**: injector 0.20+
- **Testing**: pytest 7.0+, pytest-mock 3.10+
- **Configuration**: PyYAML 6.0+, python-dotenv 1.0+
- **Database Driver**: PyMySQL 1.0+

## System Architecture
```
Batch Layer (batch/)
    ↓
Business Layer (business/)
    ↓
Domain Layer (domain/)
    ↓
Infrastructure (test1 DB + test2 DB)
```

## Multi-Database Architecture
- **test1 database**: User and department management
  - Tables: `user`, `department`
  - Views: `user_info`
  - Session: `Test1DatabaseSession`
  - Repositories in: `domain/repository/test1/`
  
- **test2 database**: Product and category management
  - Tables: `products`, `categories`
  - Session: `Test2DatabaseSession`
  - Repositories in: `domain/repository/test2/`

## Key Design Patterns
1. **AbstractService Pattern**: All services implement `execute(in_dto) -> out_dto`
2. **Dependency Injection**: Using `@inject` and `@dataclass` decorators
3. **Session Management**: `@SessionManager` decorator for transaction lifecycle
4. **Repository Pattern**: Database-specific repositories for data access
5. **Value Objects**: DTOs in `business/vo/` for data transfer

## Main Entry Points
- `csv_import_main.py`: Import users/departments from CSV (test1)
- `csv_export_main.py`: Export user information to CSV (test1)
- `categories_import_main.py`: Import categories from CSV (test2)
- `products_import_main.py`: Import products from CSV (test2)
- `product_info_export_main.py`: Export product information to CSV (test2)