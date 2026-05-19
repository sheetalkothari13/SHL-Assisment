import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.logging_config import setup_logging, logger
from app.database import init_db
from app.routers import chat, catalog, campaign
from app.exceptions import SHLAssessmentException
import os

# Initialize structured logging
setup_logging()

app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version
)

# Enable CORS for local web browsing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup hook to initialize the SQLite database
@app.on_event("startup")
async def on_startup():
    logger.info("Starting up FastAPI application server...")
    await init_db()
    logger.info("Application server startup complete.")

# Global request timeout middleware (30 seconds)
@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    try:
        # Wrap request execution in an asyncio timeout of 30 seconds
        response = await asyncio.wait_for(call_next(request), timeout=30.0)
        if request.url.path == "/" or request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response
    except asyncio.TimeoutError:
        logger.error(f"Request timeout exceeded for path: {request.url.path}")
        return JSONResponse(
            status_code=504,
            content={"detail": "Request execution time exceeded 30 seconds limit."}
        )

# Unified exception handlers
@app.exception_handler(SHLAssessmentException)
async def shl_exception_handler(request: Request, exc: SHLAssessmentException):
    logger.error(f"Unified Handler caught exception: {exc.message} (Status: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server crash: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please consult the system logs."}
    )

@app.get("/health", tags=["Health"])
async def health_check():
    """Service Health Verification"""
    return {"status": "ok"}

# Register APIRouters
app.include_router(chat.router)
app.include_router(catalog.router)
app.include_router(campaign.router)

# Resolve and mount the frontend static directory
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_dir = os.path.join(current_dir, "static")

if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    # Root route serves the dashboard index.html directly
    @app.get("/")
    async def get_index():
        return FileResponse(
            os.path.join(static_dir, "index.html"),
            headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"}
        )
