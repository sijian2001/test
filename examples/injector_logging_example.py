"""
Injector Logging Example

This example demonstrates how to enable debug logging for python-injector
to trace dependency injection operations.
"""

import logging
from dataclasses import dataclass
from injector import Injector, Module, provider, inject, singleton


# Configure logging BEFORE creating injector
def setup_injector_logging():
    """
    Enable debug logging for injector to trace dependency injection

    Available log messages:
    - Injector.get(): Shows interface, scope, and provider being used
    - create_object(): Shows class being created with kwargs
    - args_to_inject(): Shows bindings being provided for functions
    """
    # Get the injector logger
    injector_logger = logging.getLogger('injector')

    # Set level to DEBUG to see all injection traces
    injector_logger.setLevel(logging.DEBUG)

    # Add a handler to output logs
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)

    # Format logs nicely
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)

    injector_logger.addHandler(handler)


# Example classes
@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 3306
    database: str = "test"


@inject
@dataclass
class DatabaseConnection:
    config: DatabaseConfig

    def __post_init__(self):
        print(f"Creating DB connection to {self.config.host}:{self.config.port}/{self.config.database}")


@inject
@dataclass
class UserRepository:
    db_connection: DatabaseConnection

    def get_users(self):
        print("Fetching users from database")
        return ["user1", "user2"]


@inject
@dataclass
class UserService:
    user_repository: UserRepository

    def list_users(self):
        return self.user_repository.get_users()


# Module configuration
class AppModule(Module):
    @singleton
    @provider
    def provide_config(self) -> DatabaseConfig:
        print("Providing DatabaseConfig")
        return DatabaseConfig(host="prod-db.example.com", port=3306, database="production")

    @provider
    def provide_db_connection(self, config: DatabaseConfig) -> DatabaseConnection:
        print("Providing DatabaseConnection")
        return DatabaseConnection(config=config)


def main():
    print("=== Example 1: Without logging ===")
    injector_no_log = Injector([AppModule()])
    service1 = injector_no_log.get(UserService)
    service1.list_users()

    print("\n=== Example 2: With DEBUG logging ===")
    # Enable injector debug logging
    setup_injector_logging()

    injector_with_log = Injector([AppModule()])
    service2 = injector_with_log.get(UserService)
    service2.list_users()

    print("\n=== Example 3: Verify singleton behavior ===")
    config1 = injector_with_log.get(DatabaseConfig)
    config2 = injector_with_log.get(DatabaseConfig)
    print(f"Same config instance? {config1 is config2}")


if __name__ == "__main__":
    main()
