import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Prefer DATABASE_URL from environment for production (e.g., Render Postgres or a mounted SQLite path)
# Fallback to local SQLite file for development.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app/skillsprint.db")

# SQLAlchemy expects "postgresql+psycopg2://" but many providers (Render) give "postgres://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

# Determine connect_args based on backend
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    # Needed only for SQLite
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

