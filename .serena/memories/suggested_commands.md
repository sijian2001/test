# Suggested Commands

## Environment Setup

### Windows
```bash
setup.bat
```

### Linux/macOS
```bash
./setup.sh
```

## Testing Commands

### Run all tests
```bash
python -m pytest tests/ -v
```

### Run specific test suites
```bash
# User management tests (test1)
python -m pytest tests/business/test_user_info_service.py -v
python -m pytest tests/repository/test_user_repository.py -v

# Product management tests (test2)
python -m pytest tests/business/test_product_info_service.py -v
python -m pytest tests/repository/test_product_repository.py -v
python -m pytest tests/business/test_category_regist_service.py -v
```

## Application Execution

### User Management (test1 database)
```bash
python csv_import_main.py        # Import users/departments from CSV
python csv_export_main.py        # Export user information to CSV
```

### Product Management (test2 database)
```bash
python categories_import_main.py  # Import categories from CSV
python products_import_main.py    # Import products from CSV
python product_info_export_main.py # Export product information to CSV
```

## Windows System Commands
- List files: `dir` or `ls` (if using Git Bash)
- Change directory: `cd <path>`
- Find files: `where <filename>` or `dir /s <pattern>`
- Search in files: `findstr /s /i <pattern> <files>`
- Environment activation: `venv\Scripts\activate`
- Environment deactivation: `deactivate`