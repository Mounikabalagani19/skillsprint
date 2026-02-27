import os
import time
import logging
import asyncio
import signal
import traceback
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, SessionLocal
from . import models
from .seed import seed_database
from .api.v1 import api

# This line creates the database tables if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SkillSprint API",
    description="API for the SkillSprint micro-learning application.",
    version="0.1.0"
)

# Configure a module logger (uses Uvicorn's error logger by default in Render)
logger = logging.getLogger("uvicorn.error")

# --- CORS MIDDLEWARE CONFIGURATION ---
# This is the crucial part that needs to be updated.
# It tells the backend to accept requests from your frontend.
default_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "https://skill-sprint.me",
    "https://www.skill-sprint.me",
]

# Support comma-separated CORS_ORIGINS env var for production (e.g., your Vercel frontend URL)
env_origins = os.getenv("CORS_ORIGINS", "").strip()
extra_origins = [o.strip() for o in env_origins.split(",") if o.strip()] if env_origins else []
origins = default_origins + extra_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # Allow Vercel preview deployments like https://<hash>-<project>.vercel.app
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)


# --- Auto-seed on first boot (for environments without shell) ---
@app.on_event("startup")
def ensure_seed_data():
    """Create tables and seed the database with default challenges on startup.
    It's idempotent: only inserts missing titles, so it's safe to run every boot.
    """
    try:
        from .database import Base, engine
        
        # Force recreate all tables (drops old schema if exists)
        # ONLY for initial deployment - remove this after first successful deploy
        print("Dropping all tables to apply schema changes...")
        Base.metadata.drop_all(bind=engine)
        print("Creating all tables with current schema...")
        Base.metadata.create_all(bind=engine)
        print("Database tables initialized")
        
        # Seed challenges
        inserted = seed_database()
        print(f"Seeding check complete. Inserted: {inserted}")
    except Exception as e:
        # Log and continue serving; seeding is non-critical
        print(f"Startup initialization error: {e}")
        import traceback
        traceback.print_exc()


# --- Request logging middleware ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    client = request.client.host if request.client else "-"
    ua = request.headers.get("user-agent", "-")
    logger.info(f"REQ start: {client} {request.method} {request.url.path} UA={ua}")
    try:
        resp = await call_next(request)
    except Exception as e:
        logger.exception(f"Error handling request {request.method} {request.url.path}: {e}")
        raise
    logger.info(f"REQ done: {client} {request.method} {request.url.path} -> {resp.status_code}")
    return resp


# --- Heartbeat background task ---
_heartbeat_task = None

async def _heartbeat_loop(interval_seconds: int = 300):
    while True:
        logger.info(f"heartbeat: app alive time={int(time.time())}")
        await asyncio.sleep(interval_seconds)


def _handle_signal(sig, frame):
    # Synchronous signal handler used to log the receipt of OS signals.
    try:
        logger.warning(f"OS signal received: {sig}. Trace:\n{''.join(traceback.format_stack(frame))}")
    except Exception:
        logger.warning(f"OS signal received: {sig} (no stack available)")


@app.on_event("startup")
def _start_heartbeat_and_signals():
    """Register signal handlers and start a periodic heartbeat logger."""
    global _heartbeat_task
    try:
        loop = asyncio.get_event_loop()
        _heartbeat_task = loop.create_task(_heartbeat_loop())
    except RuntimeError:
        # If there's no running loop (rare under some servers), skip heartbeat
        logger.warning("Could not start heartbeat task: no running event loop")

    # Register handlers for SIGTERM and SIGINT so we log the signal before shutdown
    try:
        signal.signal(signal.SIGTERM, _handle_signal)
        signal.signal(signal.SIGINT, _handle_signal)
    except Exception as e:
        logger.debug(f"Could not register signal handlers: {e}")


# Include the main API router
app.include_router(api.api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the SkillSprint API!"}


# Health check endpoint used by uptime monitors. Accepts GET and HEAD to avoid
# 405s from services that probe with HEAD or GET. Returns minimal JSON.
@app.api_route("/health", methods=["GET", "HEAD"], tags=["Health"])
def health_check():
    return {"status": "ok"}


@app.on_event("shutdown")
def log_shutdown():
    """Log a timestamped shutdown message so platform logs capture why the process stopped.
    This doesn't change shutdown behavior but makes Render/host logs easier to interpret.
    """
    try:
        pid = os.getpid()
    except Exception:
        pid = None
    logger.info(f"Application shutdown initiated. pid={pid} time={int(time.time())}")
    # Cancel heartbeat if running
    try:
        global _heartbeat_task
        if _heartbeat_task is not None:
            _heartbeat_task.cancel()
            logger.info("Heartbeat task cancelled")
    except Exception:
        logger.debug("Error cancelling heartbeat task")

