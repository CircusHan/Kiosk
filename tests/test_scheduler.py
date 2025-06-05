import importlib.util
import os
import sys
import pytest

# Load scheduler module without importing the full package to avoid heavy
# dependencies during tests
MODULE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "core", "scheduler.py"))
spec = importlib.util.spec_from_file_location("scheduler", MODULE_PATH)
scheduler_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scheduler_module)
KioskScheduler = scheduler_module.KioskScheduler


def dummy_callback():
    return "done"


def test_add_reset_cancel_session_timeout():
    scheduler = KioskScheduler()
    scheduler.start()

    # Add session timeout
    job1 = scheduler.add_session_timeout("s1", timeout_seconds=10, callback=dummy_callback)
    assert "s1" in scheduler._session_timers
    assert scheduler._session_timers["s1"] == job1

    # Reset should keep same job object and reschedule
    scheduler.reset_session_timeout("s1")
    assert scheduler._session_timers["s1"] == job1

    # Cancel should remove job
    scheduler.cancel_session_timeout("s1")
    assert "s1" not in scheduler._session_timers
    assert scheduler.scheduler.get_job(job1.id) is None

    scheduler.shutdown()


def test_re_add_session_timeout_replaces_job():
    scheduler = KioskScheduler()
    scheduler.start()

    job1 = scheduler.add_session_timeout("s2", timeout_seconds=5, callback=dummy_callback)
    job2 = scheduler.add_session_timeout("s2", timeout_seconds=5, callback=dummy_callback)

    # Job should be replaced
    assert job2 is not job1
    assert scheduler.scheduler.get_job(job1.id) is job2
    assert scheduler._session_timers["s2"] == job2

    scheduler.shutdown()
