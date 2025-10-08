"""
Test to verify TEST1 connection is properly closed with improved version
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from injector import Injector
from active_user_regist_service_improved import ActiveUserRegistServiceImproved, ActiveUserRegistInDto
from app.domain.database import Test1DatabaseSession, Test2DatabaseSession
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_connection_pool_status(session, db_name):
    """Check the connection pool status"""
    engine = session.get_bind()
    pool = engine.pool

    logger.info(f"\n{'='*60}")
    logger.info(f"{db_name} Connection Pool Status:")
    logger.info(f"{'='*60}")
    logger.info(f"Pool size: {pool.size()}")
    logger.info(f"Checked in connections: {pool.checkedin()}")
    logger.info(f"Checked out connections: {pool.checkedout()}")
    logger.info(f"Overflow connections: {pool.overflow()}")
    logger.info(f"{'='*60}\n")

def main():
    logger.info("="*60)
    logger.info("TEST1 Connection Close Verification (IMPROVED VERSION)")
    logger.info("="*60)

    injector = Injector()

    # Get sessions
    test1_session = injector.get(Test1DatabaseSession)
    test2_session = injector.get(Test2DatabaseSession)

    logger.info("\n>>> BEFORE ActiveUserRegistServiceImproved execution")
    check_connection_pool_status(test1_session, "TEST1")
    check_connection_pool_status(test2_session, "TEST2")

    # Execute ActiveUserRegistServiceImproved
    active_user_service = injector.get(ActiveUserRegistServiceImproved)
    in_dto = ActiveUserRegistInDto()

    logger.info(">>> EXECUTING ActiveUserRegistServiceImproved.execute()")
    result = active_user_service.execute(in_dto)
    logger.info(f"Result: {result.sourceUserCount} users from TEST1, {result.activeUserCount} registered to TEST2")

    logger.info("\n>>> AFTER ActiveUserRegistServiceImproved execution")
    check_connection_pool_status(test1_session, "TEST1")
    check_connection_pool_status(test2_session, "TEST2")

    # Check if sessions are in transaction
    logger.info("\n>>> Transaction Status Check")
    logger.info(f"TEST1 session in_transaction: {test1_session.in_transaction()}")
    logger.info(f"TEST2 session in_transaction: {test2_session.in_transaction()}")

    # Check if connections are actually being returned to pool
    logger.info("\n>>> Analysis:")

    test1_checked_out = test1_session.get_bind().pool.checkedout()
    test2_checked_out = test2_session.get_bind().pool.checkedout()

    if test1_checked_out > 0:
        logger.warning(f"⚠️  TEST1 has {test1_checked_out} checked out connection(s) - NOT returned to pool!")
        logger.warning("This may cause connection leak in long-running applications.")
    else:
        logger.info("✓ TEST1 connections properly returned to pool")

    if test2_checked_out > 0:
        logger.warning(f"⚠️  TEST2 has {test2_checked_out} checked out connection(s) - NOT returned to pool!")
    else:
        logger.info("✓ TEST2 connections properly returned to pool")

    logger.info("\n" + "="*60)
    logger.info("Conclusion:")
    logger.info("="*60)
    if test1_checked_out == 0 and test2_checked_out == 0:
        logger.info("✓ IMPROVED VERSION: Both TEST1 and TEST2 connections")
        logger.info("  are properly managed and returned to the pool.")
        logger.info("")
        logger.info("  This version prevents connection leaks by using")
        logger.info("  @Transactional for both TEST1 and TEST2.")
    else:
        logger.info("✗ Connection leak still exists.")
    logger.info("="*60)

if __name__ == "__main__":
    main()
