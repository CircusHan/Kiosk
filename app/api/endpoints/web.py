"""Web interface endpoints"""

from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def web_interface(request: Request):
    """웹 인터페이스 메인 페이지"""
    context = {
        "request": request,
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "default_language": settings.default_language,
        "supported_languages": settings.supported_languages,
        "session_timeout": settings.session_timeout_seconds,
        "tts_enabled": settings.tts_enabled
    }
    return templates.TemplateResponse("index.html", context)


@router.get("/kiosk", response_class=HTMLResponse) 
async def kiosk_mode(request: Request):
    """키오스크 전용 모드 (전체화면)"""
    context = {
        "request": request,
        "app_name": settings.app_name,
        "kiosk_mode": True,
        "fullscreen": True
    }
    return templates.TemplateResponse("index.html", context)


@router.get("/admin", response_class=HTMLResponse)
async def admin_interface(request: Request):
    """관리자 인터페이스 (향후 구현)"""
    context = {
        "request": request,
        "app_name": settings.app_name,
        "admin_mode": True
    }
    # 향후 admin.html 템플릿 생성
    return templates.TemplateResponse("index.html", context)


@router.get("/health-check")
async def web_health_check():
    """웹 인터페이스 상태 확인"""
    return {
        "status": "healthy",
        "web_interface": "active",
        "templates": "loaded"
    }