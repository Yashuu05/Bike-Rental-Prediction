import os
import sys
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.logger import logging as log

load_dotenv()

# AWS RDS MySQL Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "bikerental_db")

# Safely URL-encode password (handles special characters like '#', '@', etc.)
encoded_password = quote_plus(DB_PASSWORD)

# Connection URL format for MySQL with PyMySQL driver
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# SQLAlchemy Engine & Session
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={"connect_timeout": 10}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    log.info(f"Database engine created for host: {DB_HOST}")
except Exception as e:
    log.warning(f"Could not create database engine with URL {DATABASE_URL}: {e}")
    engine = None
    SessionLocal = None

Base = declarative_base()


def get_db():
    """Dependency for providing a SQLAlchemy database session to FastAPI endpoints."""
    if SessionLocal is None:
        yield None
        return

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
