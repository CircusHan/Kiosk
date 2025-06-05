"""API Router Module"""

from fastapi import APIRouter
from app.api.endpoints import reception, payment, certificate, admin, session, web, websocket

api_router = APIRouter()

# Include sub-routers
api_router.include_router(reception.router, prefix="/reception", tags=["reception"])
api_router.include_router(payment.router, prefix="/payment", tags=["payment"])
api_router.include_router(certificate.router, prefix="/certificate", tags=["certificate"])
api_router.include_router(session.router, prefix="/session", tags=["session"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(websocket.router, prefix="/websocket", tags=["websocket"])

# Web interface router (no prefix for root paths)
web_router = APIRouter()
web_router.include_router(web.router, tags=["web"])