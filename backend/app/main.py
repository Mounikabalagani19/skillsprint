import os
from fastapi import FastAPI
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

# --- CORS MIDDLEWARE CONFIGURATION ---
# This is the crucial part that needs to be updated.
# It tells the backend to accept requests from your frontend.
default_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
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
    """Seed the database with default challenges if empty.
    This runs once on app startup and only inserts when no challenges exist.
    """
    try:
        db = SessionLocal()
        try:
            count = db.query(models.Challenge).count()
        finally:
            db.close()
        if count == 0:
            print("No challenges found. Seeding default challenges...")
            seed_database()
    except Exception as e:
        # Log and continue serving; seeding is non-critical
        print(f"Startup seeding skipped due to error: {e}")


# Include the main API router
app.include_router(api.api_router, prefix="/api/v1")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the SkillSprint API!"}

