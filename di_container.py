from injector import Injector, Binder, singleton

def create_injector() -> Injector:
    def configure_dependencies(binder: Binder) -> None:
        # Database configurations
        from domain.database import DatabaseConfig, DatabaseEngine, DatabaseSession
        binder.bind(DatabaseConfig, to=DatabaseConfig(), scope=singleton)
        binder.bind(DatabaseEngine, scope=singleton)
        binder.bind(DatabaseSession, scope=singleton)

        # Repository bindings
        from domain.repository.user_repository import AbstractUserRepository, UserRepository
        from domain.repository.department_repository import AbstractDepartmentRepository, DepartmentRepository
        binder.bind(AbstractUserRepository, to=UserRepository)
        binder.bind(AbstractDepartmentRepository, to=DepartmentRepository)

        # Service bindings
        from business.depart_user_regist_service import AbstractDepartUserRegistService, DepartUserRegistService
        from business.department_regist_service import AbstractDepartmentRegistService, DepartmentRegistService
        from business.user_regist_service import AbstractUserRegistService, UserRegistService
        binder.bind(AbstractDepartUserRegistService, to=DepartUserRegistService)
        binder.bind(AbstractDepartmentRegistService, to=DepartmentRegistService)
        binder.bind(AbstractUserRegistService, to=UserRegistService)

        # Processor bindings
        from batch.processor import BatchProcessor
        from batch.data_batch_processor import DataBatchProcessor
        from batch.csv_import_processor import CsvImportProcessor, DataCsvImportProcessor
        binder.bind(BatchProcessor, to=DataBatchProcessor)
        binder.bind(CsvImportProcessor, to=DataCsvImportProcessor)

    return Injector([configure_dependencies])