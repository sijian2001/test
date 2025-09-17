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
        from domain.repository.user_info_repository import AbstractUserInfoRepository, UserInfoRepository
        binder.bind(AbstractUserRepository, to=UserRepository)
        binder.bind(AbstractDepartmentRepository, to=DepartmentRepository)
        binder.bind(AbstractUserInfoRepository, to=UserInfoRepository)

        # Service bindings
        from business.depart_user_regist_service import AbstractDepartUserRegistService, DepartUserRegistService
        from business.department_regist_service import AbstractDepartmentRegistService, DepartmentRegistService
        from business.user_regist_service import AbstractUserRegistService, UserRegistService
        from business.user_info_service import AbstractUserInfoService, UserInfoService
        from business.csv_export_service import AbstractCsvExportService, CsvExportService
        binder.bind(AbstractDepartUserRegistService, to=DepartUserRegistService)
        binder.bind(AbstractDepartmentRegistService, to=DepartmentRegistService)
        binder.bind(AbstractUserRegistService, to=UserRegistService)
        binder.bind(AbstractUserInfoService, to=UserInfoService)
        binder.bind(AbstractCsvExportService, to=CsvExportService)

        # Processor bindings
        from batch.processor import BatchProcessor
        from batch.data_batch_processor import DataBatchProcessor
        from batch.csv_import_processor import CsvImportProcessor, DataCsvImportProcessor
        from batch.csv_export_processor import CsvExportProcessor, UserInfoCsvExportProcessor
        from batch.csv_export_batch_processor import CsvExportBatchProcessor
        binder.bind(BatchProcessor, to=DataBatchProcessor)
        binder.bind(CsvImportProcessor, to=DataCsvImportProcessor)
        binder.bind(CsvExportProcessor, to=UserInfoCsvExportProcessor)

    return Injector([configure_dependencies])