"""Main FastAPI application entry point"""

import sys
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.database import init_db
from app.core.scheduler import scheduler
from app.utils.logger import setup_logging
from app.api import api_router, web_router

# Import UI only if running as main
if __name__ == "__main__":
    from app.ui.main_window import run_ui

settings = get_settings()
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Healthcare Kiosk Application...")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Start scheduler
    scheduler.start()
    logger.info("Scheduler started")
    
    # Setup monitoring if enabled
    if settings.enable_monitoring and settings.sentry_dsn:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            integrations=[FastApiIntegration()],
            traces_sample_rate=0.1,
        )
        logger.info("Monitoring enabled")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Healthcare Kiosk Application...")
    scheduler.shutdown()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/api/docs" if settings.debug else None,
    redoc_url="/api/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(api_router, prefix="/api")
app.include_router(web_router)


@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "api_docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected",
        "scheduler": "running" if scheduler.scheduler.running else "stopped"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "type": type(exc).__name__}
        )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    # Check if running in GUI mode or API-only mode
    if "--api-only" in sys.argv:
        # Run API server only
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            workers=1 if settings.debug else settings.workers
        )
    else:
        # Run with GUI
        logger.info("Starting application with GUI...")
        
        # Start FastAPI in background thread
        import threading
        import uvicorn
        
        def run_api():
            uvicorn.run(
                app,
                host="127.0.0.1",  # Local only for GUI mode
                port=settings.port,
                log_level="info"
            )
        
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        
        # Run GUI in main thread
        run_ui()