"""Admin API endpoints"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import Session, select, func

from app.core.database import get_session, get_db_stats
from app.core.models import Patient, Appointment, Payment, Certificate, DeviceLog
from app.core.config import get_settings
from app.core.scheduler import scheduler
from app.i18n import i18n

router = APIRouter()
settings = get_settings()


def verify_admin(authorization: Optional[str] = Header(None)):
    """Verify admin authorization"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    # Simple password check (in production, use proper auth)
    if authorization != f"Bearer {settings.admin_password}":
        raise HTTPException(status_code=403, detail="Invalid authorization")
    
    return True


@router.get("/stats")
async def get_statistics(
    admin: bool = Depends(verify_admin),
    session: Session = Depends(get_session)
):
    """Get system statistics"""
    # Database stats
    db_stats = get_db_stats()
    
    # Today's stats
    today_start = datetime.now().replace(hour=0, minute=0, second=0)
    
    today_appointments = session.exec(
        select(func.count(Appointment.id)).where(
            Appointment.created_at >= today_start
        )
    ).one()
    
    today_payments = session.exec(
        select(func.sum(Payment.amount)).where(
            Payment.created_at >= today_start
        )
    ).one() or 0
    
    today_certificates = session.exec(
        select(func.count(Certificate.id)).where(
            Certificate.issued_at >= today_start
        )
    ).one()
    
    return {
        "database": db_stats,
        "today": {
            "appointments": today_appointments,
            "revenue": float(today_payments),
            "certificates": today_certificates
        },
        "system": {
            "uptime_hours": 24,  # Would calculate actual uptime
            "active_sessions": 0,  # Would get from session manager
            "scheduler_jobs": len(scheduler.list_jobs())
        }
    }


@router.get("/logs")
async def get_device_logs(
    admin: bool = Depends(verify_admin),
    limit: int = 100,
    level: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Get device logs"""
    query = select(DeviceLog).order_by(DeviceLog.created_at.desc()).limit(limit)
    
    if level:
        query = query.where(DeviceLog.level == level)
    
    logs = session.exec(query).all()
    
    return {
        "count": len(logs),
        "logs": logs
    }


@router.post("/config/language")
async def update_language_settings(
    languages: list[str],
    default: str,
    admin: bool = Depends(verify_admin)
):
    """Update language settings"""
    # Validate languages
    available = i18n.get_available_locales()
    for lang in languages:
        if lang not in available:
            raise HTTPException(status_code=400, detail=f"Language {lang} not available")
    
    # Update settings (in production, persist to database)
    settings.supported_languages = languages
    settings.default_language = default
    i18n.set_locale(default)
    
    return {
        "status": "updated",
        "supported_languages": languages,
        "default_language": default
    }


@router.post("/config/timeout")
async def update_timeout_settings(
    session_timeout: int,
    idle_timeout: int,
    admin: bool = Depends(verify_admin)
):
    """Update timeout settings"""
    if session_timeout < 60 or idle_timeout < 60:
        raise HTTPException(status_code=400, detail="Timeout must be at least 60 seconds")
    
    settings.session_timeout_seconds = session_timeout
    settings.idle_timeout_seconds = idle_timeout
    
    return {
        "status": "updated",
        "session_timeout_seconds": session_timeout,
        "idle_timeout_seconds": idle_timeout
    }


@router.get("/appointments/summary")
async def get_appointments_summary(
    admin: bool = Depends(verify_admin),
    days: int = 7,
    session: Session = Depends(get_session)
):
    """Get appointments summary for past N days"""
    start_date = datetime.now() - timedelta(days=days)
    
    # Get daily counts
    daily_stats = []
    for i in range(days):
        date = start_date + timedelta(days=i)
        date_start = date.replace(hour=0, minute=0, second=0)
        date_end = date_start + timedelta(days=1)
        
        count = session.exec(
            select(func.count(Appointment.id)).where(
                Appointment.created_at >= date_start,
                Appointment.created_at < date_end
            )
        ).one()
        
        daily_stats.append({
            "date": date.strftime("%Y-%m-%d"),
            "count": count
        })
    
    # Department breakdown
    dept_stats = session.exec(
        select(
            Appointment.department,
            func.count(Appointment.id).label("count")
        ).where(
            Appointment.created_at >= start_date
        ).group_by(Appointment.department)
    ).all()
    
    return {
        "period_days": days,
        "daily_stats": daily_stats,
        "department_stats": [
            {"department": dept, "count": count}
            for dept, count in dept_stats
        ]
    }


@router.post("/maintenance/cleanup")
async def cleanup_old_data(
    admin: bool = Depends(verify_admin),
    days: int = 90,
    session: Session = Depends(get_session)
):
    """Cleanup old data"""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Count records to be deleted
    old_logs = session.exec(
        select(func.count(DeviceLog.id)).where(
            DeviceLog.created_at < cutoff_date
        )
    ).one()
    
    # Delete old logs
    session.exec(
        select(DeviceLog).where(DeviceLog.created_at < cutoff_date)
    ).delete()
    
    session.commit()
    
    return {
        "status": "completed",
        "deleted": {
            "device_logs": old_logs
        }
    }


@router.get("/scheduler/jobs")
async def get_scheduler_jobs(admin: bool = Depends(verify_admin)):
    """Get scheduler job status"""
    return {
        "jobs": scheduler.list_jobs()
    }


@router.post("/test/announcement")
async def test_announcement(
    message: str,
    duration_seconds: int = 30,
    admin: bool = Depends(verify_admin)
):
    """Test announcement system"""
    # In production, this would trigger UI announcement
    return {
        "status": "announced",
        "message": message,
        "duration": duration_seconds
    }