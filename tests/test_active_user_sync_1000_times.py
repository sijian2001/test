"""
Test active_user_sync_main.py 1000 times by running it as subprocess
"""
import subprocess
import sys
import time
import pymysql
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def get_mysql_connection_count():
    """Get current MySQL connection count"""
    try:
        conn = pymysql.connect(
            host='localhost',
            user='user1',
            password='1234',
            database='test1'
        )
        cursor = conn.cursor()
        cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
        result = cursor.fetchone()
        threads_connected = int(result[1])
        cursor.close()
        conn.close()
        return threads_connected
    except Exception as e:
        logger.error(f"Failed to get connection count: {e}")
        return -1

def get_mysql_stats():
    """Get MySQL connection statistics"""
    try:
        conn = pymysql.connect(
            host='localhost',
            user='user1',
            password='1234',
            database='test1'
        )
        cursor = conn.cursor()

        cursor.execute("SHOW STATUS LIKE 'Threads_connected'")
        threads_connected = int(cursor.fetchone()[1])

        cursor.execute("SHOW STATUS LIKE 'Max_used_connections'")
        max_used_connections = int(cursor.fetchone()[1])

        cursor.close()
        conn.close()

        return {
            'threads_connected': threads_connected,
            'max_used_connections': max_used_connections
        }
    except Exception as e:
        logger.error(f"Failed to get MySQL stats: {e}")
        return None

def main():
    logger.info("="*80)
    logger.info("Connection Leak Test: Running active_user_sync_main.py 1000 times")
    logger.info("="*80)
    logger.info("")

    total = 1000
    success_count = 0
    error_count = 0

    # Initial connection check
    logger.info("Initial MySQL connection status:")
    initial_stats = get_mysql_stats()
    if initial_stats:
        logger.info(f"  Threads_connected: {initial_stats['threads_connected']}")
        logger.info(f"  Max_used_connections: {initial_stats['max_used_connections']}")
    logger.info("")

    logger.info(f"Starting {total} iterations...")
    logger.info("Progress will be shown every 100 iterations")
    logger.info("")

    start_time = time.time()

    for i in range(1, total + 1):
        try:
            # Run the batch program as subprocess
            result = subprocess.run(
                [sys.executable, r".\app\batch\active_user_sync_main.py"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                success_count += 1
            else:
                error_count += 1
                logger.error(f"Iteration {i} failed with return code: {result.returncode}")
                if result.stderr:
                    logger.error(f"  Error: {result.stderr[:200]}")

        except subprocess.TimeoutExpired:
            error_count += 1
            logger.error(f"Iteration {i} timed out")
        except Exception as e:
            error_count += 1
            logger.error(f"Iteration {i} error: {str(e)}")

        # Show progress every 100 iterations
        if i % 100 == 0:
            conn_count = get_mysql_connection_count()
            logger.info(f"Iteration {i}/{total}: Success={success_count}, Errors={error_count}, MySQL Connections={conn_count}")

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Final statistics
    logger.info("")
    logger.info("="*80)
    logger.info("Test Results")
    logger.info("="*80)
    logger.info(f"Total iterations: {total}")
    logger.info(f"Successful: {success_count}")
    logger.info(f"Errors: {error_count}")
    logger.info(f"Elapsed time: {elapsed_time:.2f} seconds")
    logger.info(f"Average time per iteration: {elapsed_time/total*1000:.2f} ms")
    logger.info("")

    # Final connection check
    logger.info("="*80)
    logger.info("Final MySQL Connection Status")
    logger.info("="*80)
    final_stats = get_mysql_stats()
    if final_stats:
        logger.info(f"Threads_connected: {final_stats['threads_connected']}")
        logger.info(f"Max_used_connections: {final_stats['max_used_connections']}")

        # Analysis
        logger.info("")
        logger.info("="*80)
        logger.info("Connection Leak Analysis")
        logger.info("="*80)

        if initial_stats:
            conn_diff = final_stats['threads_connected'] - initial_stats['threads_connected']
            logger.info(f"Connection difference: {conn_diff}")
            logger.info(f"  Initial: {initial_stats['threads_connected']}")
            logger.info(f"  Final: {final_stats['threads_connected']}")
            logger.info("")

            if conn_diff > 2:
                logger.warning("⚠️  WARNING: Significant connection increase detected!")
                logger.warning(f"   {conn_diff} more connections than at start")
                logger.warning("   This indicates a potential connection leak.")
            elif conn_diff > 0:
                logger.info(f"ℹ️  Minor connection increase: {conn_diff}")
                logger.info("   This is within acceptable range for connection pooling.")
            else:
                logger.info("✓ No connection leak detected")
                logger.info("  Connection count remains stable.")

    logger.info("")
    logger.info("="*80)
    logger.info("Conclusion")
    logger.info("="*80)
    logger.info("If Threads_connected remains stable (not increasing significantly),")
    logger.info("then no connection leak is detected.")
    logger.info("="*80)

if __name__ == "__main__":
    main()
