"""Web interface endpoints"""

import logging
import google.generativeai as genai # Added for Gemini
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from pydantic import BaseModel # Added for request body model

from app.core.config import get_settings

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory="templates")

# Temporary storage for API key (mimicking session behavior)
# WARNING: Not suitable for production. Use secure storage in a real app.
api_key_storage = {}


class VoiceCommandPayload(BaseModel): # Pydantic model for request body
    text: str


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


@router.post("/settings") # Changed to post for API key saving, GET is separate
async def save_settings(request: Request, gemini_api_key: str = Form(None)):
    if gemini_api_key:
        api_key_storage['gemini_api_key'] = gemini_api_key
        logger.info(f"API Key saved (first 5 chars): {gemini_api_key[:5]}...")
        return JSONResponse({"message": "API Key saved successfully!"}, status_code=200)
    return JSONResponse({"message": "API Key is required."}, status_code=400)

@router.get("/settings", response_class=HTMLResponse) # GET for displaying the page
async def settings_page(request: Request):
    """설정 페이지"""
    context = {"request": request}
    return templates.TemplateResponse("settings.html", context)

@router.get("/voice-interaction", response_class=HTMLResponse)
async def voice_interaction_page(request: Request):
    """음성 인터랙션 페이지"""
    context = {"request": request}
    return templates.TemplateResponse("voice_interaction.html", context)

@router.post("/api/voice_command")
async def voice_command(payload: VoiceCommandPayload): # Use Pydantic model for payload
    """음성 명령 API 엔드포인트"""
    user_text = payload.text
    logger.info(f"Voice command received with text: '{user_text}'")

    if not user_text:
        # This case should ideally be caught by Pydantic model if text is not optional
        logger.warning("Voice command API called with no text, though Pydantic model should prevent this if 'text' is mandatory.")
        return JSONResponse(content={"error": "No text provided"}, status_code=400)

    api_key = api_key_storage.get('gemini_api_key')

    if not api_key:
        logger.error("Gemini API key not configured. Please set it in settings via the UI.")
        return JSONResponse(content={"error": "API key not configured. Please set it in settings."}, status_code=401)

    try:
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel('gemini-pro')

        logger.info(f"Sending to Gemini: '{user_text}'")
        # Note: Using generate_content_async for FastAPI's async context
        response = await model.generate_content_async(user_text)

        ai_response_text = response.text
        logger.info(f"Received from Gemini: '{ai_response_text}'")

        return JSONResponse(content={
            "user_text": user_text,
            "ai_response": ai_response_text
        })

    except Exception as e:
        logger.error(f"Error communicating with Gemini API: {e}", exc_info=True)
        # It's good practice to not expose raw error messages from external services to the client.
        # However, for debugging during development, str(e) can be useful.
        # Consider a more generic message for production.
        error_message = f"Error processing your request with AI: {type(e).__name__} - {str(e)}"
        return JSONResponse(content={"error": error_message}, status_code=500)


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