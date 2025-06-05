"""Task scheduler configuration using APScheduler"""

import logging
from datetime import datetime
from typing import Optional, Callable
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.job import Job

logger = logging.getLogger(__name__)


class KioskScheduler:
    """Centralized scheduler for kiosk tasks"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            jobstores={
                'default': MemoryJobStore()
            },
            executors={
                'default': AsyncIOExecutor()
            },
            job_defaults={
                'coalesce': False,
                'max_instances': 1
            },
            timezone='Asia/Seoul'
        )
        self._session_timers = {}
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shutdown")
    
    def add_session_timeout(
        self,
        session_id: str,
        timeout_seconds: int,
        callback: Callable,
        **kwargs
    ) -> Job:
        """Add session timeout job"""
        job_id = f"session_timeout_{session_id}"
        
        # Remove existing timeout for this session
        if job_id in self._session_timers:
            self.scheduler.remove_job(job_id)
        
        # Add new timeout job
        job = self.scheduler.add_job(
            callback,
            'interval',
            seconds=timeout_seconds,
            id=job_id,
            kwargs=kwargs,
            max_instances=1,
            replace_existing=True
        )
        
        self._session_timers[session_id] = job
        logger.info(f"Session timeout set for {session_id}: {timeout_seconds}s")
        
        return job
    
    def reset_session_timeout(self, session_id: str):
        """Reset session timeout by rescheduling"""
        job_id = f"session_timeout_{session_id}"
        if job_id in self._session_timers:
            job = self._session_timers[job_id]
            job.reschedule('interval', seconds=job.trigger.interval.total_seconds())
            logger.info(f"Session timeout reset for {session_id}")
    
    def cancel_session_timeout(self, session_id: str):
        """Cancel session timeout"""
        job_id = f"session_timeout_{session_id}"
        if job_id in self._session_timers:
            self.scheduler.remove_job(job_id)
            del self._session_timers[session_id]
            logger.info(f"Session timeout cancelled for {session_id}")
    
    def add_emr_sync_job(
        self,
        interval_minutes: int,
        sync_function: Callable
    ) -> Job:
        """Add EMR synchronization job"""
        return self.scheduler.add_job(
            sync_function,
            'interval',
            minutes=interval_minutes,
            id='emr_sync',
            replace_existing=True
        )
    
    def add_backup_job(
        self,
        hour: int,
        minute: int,
        backup_function: Callable
    ) -> Job:
        """Add daily backup job"""
        return self.scheduler.add_job(
            backup_function,
            'cron',
            hour=hour,
            minute=minute,
            id='daily_backup',
            replace_existing=True
        )
    
    def add_cleanup_job(
        self,
        interval_hours: int,
        cleanup_function: Callable
    ) -> Job:
        """Add periodic cleanup job"""
        return self.scheduler.add_job(
            cleanup_function,
            'interval',
            hours=interval_hours,
            id='periodic_cleanup',
            replace_existing=True
        )
    
    def get_job_status(self, job_id: str) -> Optional[dict]:
        """Get job status"""
        job = self.scheduler.get_job(job_id)
        if job:
            return {
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time,
                'pending': job.pending
            }
        return None
    
    def list_jobs(self) -> list:
        """List all scheduled jobs"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time,
                'trigger': str(job.trigger)
            })
        return jobs


# Global scheduler instance
scheduler = KioskScheduler()