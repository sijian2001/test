# Codebase Structure

## Directory Layout

```
.
├── batch/                      # Batch processing layer
│   ├── processor.py           # Base processor class
│   ├── csv_import_processor.py
│   ├── csv_export_processor.py
│   ├── categories_csv_import_processor.py
│   ├── products_csv_import_processor.py
│   └── product_info_csv_export_processor.py
│
├── business/                   # Business logic layer
│   ├── decorators/            # Decorators
│   │   └── session_manager.py # Session management decorator
│   ├── vo/                    # Value Objects (DTOs)
│   │   ├── user_vo.py
│   │   ├── department_vo.py
│   │   ├── product_vo.py
│   │   └── category_vo.py
│   ├── abstract_service.py    # Abstract service base class
│   ├── user_regist_service.py
│   ├── user_info_service.py
│   ├── department_regist_service.py
│   ├── product_regist_service.py
│   ├── product_info_service.py
│   └── category_regist_service.py
│
├── domain/                     # Domain layer
│   ├── model/                 # Domain models
│   │   ├── test1/            # test1 DB models
│   │   └── test2/            # test2 DB models
│   ├── repository/            # Repository layer
│   │   ├── test1/            # test1 DB repositories
│   │   │   ├── user_repository.py
│   │   │   ├── department_repository.py
│   │   │   └── user_info_repository.py
│   │   └── test2/            # test2 DB repositories
│   │       ├── product_repository.py
│   │       ├── category_repository.py
│   │       └── product_info_repository.py
│   └── database.py           # Database connection management
│
├── tests/                     # Unit tests
│   ├── batch/                # Batch layer tests
│   ├── business/             # Business layer tests
│   └── repository/           # Repository layer tests
│
├── work/                      # CSV input/output directory
│   ├── user.csv
│   ├── department.csv
│   ├── categories.csv
│   ├── products.csv
│   ├── report.csv            # User info export
│   └── product_report.csv    # Product info export
│
├── sql/                       # SQL files
│   ├── create_db_user.sql
│   ├── create_user_table.sql
│   ├── create_department_table.sql
│   └── create_user_info_view.sql
│
├── venv/                      # Virtual environment
├── db.yaml                    # Database configuration
├── requirements.txt           # Python dependencies
├── setup.bat                  # Windows setup script
├── setup.sh                   # Linux/macOS setup script
├── CLAUDE.md                  # Development guidelines
├── DESIGN.md                  # System design document
└── README.md                  # Project documentation
```

## Layer Responsibilities

### Batch Layer (`batch/`)
- CSV file processing
- Batch execution control
- Calls Business Layer for data processing
- Inherits from base `Processor` class

### Business Layer (`business/`)
- Business logic implementation
- Data transformation
- Workflow control
- Unified `execute(in_dto) -> out_dto` interface
- Transaction management via `@SessionManager`

### Domain Layer (`domain/`)
- Data access abstraction (Repository pattern)
- SQLAlchemy ORM entity models
- Database session management
- Separated by database: test1 and test2

### Configuration Files
- `db.yaml`: Database connection strings for test1 and test2
- `requirements.txt`: Python package dependencies
- `CLAUDE.md`: Claude Code development guidelines (Japanese)
- `.claude/CLAUDE.md`: Project-level guidelines (English)
- `DESIGN.md`: Comprehensive system design document

### Working Directories
- `work/`: CSV import/export files
- `sql/`: Database setup SQL scripts
- `tests/`: Comprehensive unit test suite