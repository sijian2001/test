"""
Test connection leak by running active_user_sync 1000 times
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from injector import Injector
from app.business.active_user_regist_service import ActiveUserRegistService, ActiveUserRegistInDto
from app.domain.database import Test1DatabaseSession, Test2DatabaseSession
import logging
import time

# ログレベルを上げて出力を抑制
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# SQLAlchemyのログを抑制
logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
logging.getLogger('app.business.decorators.transactional').setLevel(logging.WARNING)
logging.getLogger('app.business.active_user_regist_service').setLevel(logging.WARNING)

def check_connection_pool_status(session, db_name):
    """Check the connection pool status"""
    engine = session.get_bind()
    pool = engine.pool
    return {
        'db_name': db_name,
        'size': pool.size(),
        'checked_in': pool.checkedin(),
        'checked_out': pool.checkedout(),
        'overflow': pool.overflow(),
        'in_transaction': session.in_transaction()
    }

def main():
    logger.info("="*80)
    logger.info("Connection Leak Test: Running active_user_sync 1000 times")
    logger.info("="*80)

    # Initialize injector and get sessions
    injector = Injector()
    test1_session = injector.get(Test1DatabaseSession)
    test2_session = injector.get(Test2DatabaseSession)
    active_user_service = injector.get(ActiveUserRegistService)

    logger.info("\nInitial Connection Pool Status:")
    test1_status = check_connection_pool_status(test1_session, "TEST1")
    test2_status = check_connection_pool_status(test2_session, "TEST2")
    logger.info(f"TEST1: checked_in={test1_status['checked_in']}, checked_out={test1_status['checked_out']}, in_transaction={test1_status['in_transaction']}")
    logger.info(f"TEST2: checked_in={test2_status['checked_in']}, checked_out={test2_status['checked_out']}, in_transaction={test2_status['in_transaction']}")

    # Run 1000 times
    iterations = 1000
    start_time = time.time()

    logger.info(f"\nStarting {iterations} iterations...")
    logger.info("(Progress will be shown every 100 iterations)")

    for i in range(1, iterations + 1):
        try:
            in_dto = ActiveUserRegistInDto()
            result = active_user_service.execute(in_dto)

            # Show progress every 100 iterations
            if i % 100 == 0:
                test1_status = check_connection_pool_status(test1_session, "TEST1")
                test2_status = check_connection_pool_status(test2_session, "TEST2")

                logger.info(f"\nIteration {i}:")
                logger.info(f"  TEST1: checked_in={test1_status['checked_in']}, checked_out={test1_status['checked_out']}, in_transaction={test1_status['in_transaction']}")
                logger.info(f"  TEST2: checked_in={test2_status['checked_in']}, checked_out={test2_status['checked_out']}, in_transaction={test2_status['in_transaction']}")

                # Check for connection leak
                if test1_status['checked_out'] > 1:
                    logger.warning(f"  ⚠️  TEST1 connection leak detected: {test1_status['checked_out']} connections checked out!")
                if test2_status['checked_out'] > 1:
                    logger.warning(f"  ⚠️  TEST2 connection leak detected: {test2_status['checked_out']} connections checked out!")

        except Exception as e:
            logger.error(f"Error at iteration {i}: {str(e)}")
            break

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Final status check
    logger.info("\n" + "="*80)
    logger.info("Final Connection Pool Status:")
    logger.info("="*80)

    test1_final = check_connection_pool_status(test1_session, "TEST1")
    test2_final = check_connection_pool_status(test2_session, "TEST2")

    logger.info(f"\nTEST1:")
    logger.info(f"  Pool size: {test1_final['size']}")
    logger.info(f"  Checked in: {test1_final['checked_in']}")
    logger.info(f"  Checked out: {test1_final['checked_out']}")
    logger.info(f"  Overflow: {test1_final['overflow']}")
    logger.info(f"  In transaction: {test1_final['in_transaction']}")

    logger.info(f"\nTEST2:")
    logger.info(f"  Pool size: {test2_final['size']}")
    logger.info(f"  Checked in: {test2_final['checked_in']}")
    logger.info(f"  Checked out: {test2_final['checked_out']}")
    logger.info(f"  Overflow: {test2_final['overflow']}")
    logger.info(f"  In transaction: {test2_final['in_transaction']}")

    logger.info(f"\n" + "="*80)
    logger.info("Test Results:")
    logger.info("="*80)
    logger.info(f"Total iterations completed: {i}")
    logger.info(f"Elapsed time: {elapsed_time:.2f} seconds")
    logger.info(f"Average time per iteration: {elapsed_time/i*1000:.2f} ms")

    # Analysis
    logger.info(f"\nConnection Leak Analysis:")

    if test1_final['checked_out'] > 1:
        logger.warning(f"❌ TEST1: Connection leak detected!")
        logger.warning(f"   {test1_final['checked_out']} connections are still checked out")
        logger.warning(f"   This WILL cause problems in long-running applications")
    elif test1_final['checked_out'] == 1:
        logger.info(f"⚠️  TEST1: 1 connection checked out (singleton session pattern)")
        logger.info(f"   This is acceptable for singleton session design")
        logger.info(f"   BUT transaction is still active: {test1_final['in_transaction']}")
        if test1_final['in_transaction']:
            logger.warning(f"   ⚠️  Transaction not closed - this could cause issues")
    else:
        logger.info(f"✓ TEST1: No connection leak")

    if test2_final['checked_out'] > 0:
        logger.warning(f"❌ TEST2: Connection leak detected!")
        logger.warning(f"   {test2_final['checked_out']} connections are still checked out")
    else:
        logger.info(f"✓ TEST2: No connection leak")

    logger.info(f"\n" + "="*80)
    logger.info("Recommendation:")
    logger.info("="*80)

    if test1_final['checked_out'] > 1 or test2_final['checked_out'] > 0:
        logger.info("Connection leak detected. Immediate action required!")
        logger.info("Add @Transactional decorator to ensure proper cleanup.")
    elif test1_final['in_transaction']:
        logger.info("TEST1 transaction remains active after 1000 executions.")
        logger.info("While connections are not leaking due to singleton pattern,")
        logger.info("the unclosed transaction could cause data consistency issues.")
        logger.info("")
        logger.info("Consider adding @Transactional for TEST1 operations")
        logger.info("to ensure proper transaction lifecycle management.")
    else:
        logger.info("Connection management is working correctly.")

    logger.info("="*80)

if __name__ == "__main__":
    main()
