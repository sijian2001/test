from enum import Enum


class Database(str, Enum):
    """
    Database identifier enum for multi-database architecture

    Attributes:
        TEST1: User management database
        TEST2: Product management database
    """
    TEST1 = 'test1'
    TEST2 = 'test2'
