"""
Test to understand transaction behavior with TEST1 reads
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from injector import Injector
from app.domain.repository.test1.user_repository import UserRepository
from app.domain.database import Test1DatabaseSession

def main():
    injector = Injector()

    # Test 1: Check if get_active_users uses a transaction
    print("=" * 60)
    print("Test: Checking TEST1 transaction behavior")
    print("=" * 60)

    user_repository = injector.get(UserRepository)
    session = injector.get(Test1DatabaseSession)

    print(f"\nSession in_transaction before query: {session.in_transaction()}")

    # Execute query
    active_users = user_repository.get_active_users()

    print(f"Session in_transaction after query: {session.in_transaction()}")
    print(f"Found {len(active_users)} active users")

    print("\n" + "=" * 60)
    print("Analysis:")
    print("=" * 60)
    print("SQLAlchemy automatically starts a transaction for reads.")
    print("However, without explicit BEGIN, the transaction is implicit.")
    print("For data consistency, explicit transaction management is recommended.")
    print("=" * 60)

if __name__ == "__main__":
    main()
