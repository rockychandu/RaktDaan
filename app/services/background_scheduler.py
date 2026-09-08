"""
Local Scheduled Background Processing Worker (Member 3 & Member 4).
Runs periodic background jobs for expiry updates, low stock detection, reservation timeout releases,
and inventory consistency checks without external cloud dependencies.
"""

import time
import threading
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class BackgroundJobScheduler:
    """
    Local Python Daemon Thread Scheduler for Automated System Tasks.
    """
    _thread: Optional[threading.Thread] = None
    _stop_event = threading.Event()
    _interval_seconds: int = 300 # 5 minutes interval

    @classmethod
    def start(cls, app, interval_seconds: int = 300):
        """
        Starts the background scheduler thread attached to Flask application context.
        """
        if cls._thread and cls._thread.is_alive():
            logger.info("BackgroundJobScheduler is already running.")
            return

        cls._interval_seconds = interval_seconds
        cls._stop_event.clear()

        def worker():
            logger.info(f"BackgroundJobScheduler thread started (Interval: {cls._interval_seconds}s).")
            while not cls._stop_event.is_set():
                try:
                    with app.app_context():
                        cls._run_scheduled_tasks()
                except Exception as e:
                    logger.error(f"Error during background job execution: {str(e)}", exc_info=True)

                # Wait for next interval or stop signal
                cls._stop_event.wait(timeout=cls._interval_seconds)

            logger.info("BackgroundJobScheduler thread stopped cleanly.")

        cls._thread = threading.Thread(target=worker, daemon=True, name="RaktDaan-Scheduler")
        cls._thread.start()

    @classmethod
    def stop(cls):
        """
        Signals the background scheduler to stop cleanly.
        """
        if cls._thread and cls._thread.is_alive():
            cls._stop_event.set()
            cls._thread.join(timeout=5)
            logger.info("BackgroundJobScheduler stopped.")

    @classmethod
    def _run_scheduled_tasks(cls):
        """
        Executes internal automated maintenance tasks.
        """
        logger.info("Executing periodic scheduled background tasks...")

        # Task 1: Expiry status scanning & stock exclusion
        from app.services.expiry_engine import ExpiryEngine
        expiry_result = ExpiryEngine.run_automatic_expiry_check()

        # Task 2: Low stock threshold scanning & alert generation
        from app.services.low_stock_engine import LowStockEngine
        LowStockEngine.evaluate_stock_levels()

        # Task 3: Timed-out reservation auto-release
        from app.services.reservation_service import ReservationService
        ReservationService.check_and_release_expired_reservations()

        logger.info("Completed periodic scheduled background tasks successfully.")
