"""Database configuration and session management"""

import os
from typing import Generator
from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy.pool import StaticPool
from app.core.models import *


# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./kiosk.db")

# Create engine with appropriate settings
if DATABASE_URL.startswith("sqlite"):
    # SQLite specific settings
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
else:
    # PostgreSQL or other databases
    engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True
    )


def init_db() -> None:
    """Initialize database and create all tables"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session"""
    with Session(engine) as session:
        yield session


def drop_all_tables() -> None:
    """Drop all tables (use with caution!)"""
    SQLModel.metadata.drop_all(engine)


def get_db_stats() -> dict:
    """Get database statistics"""
    with Session(engine) as session:
        stats = {
            "patients": session.query(Patient).count(),
            "appointments": session.query(Appointment).count(),
            "payments": session.query(Payment).count(),
            "certificates": session.query(Certificate).count(),
        }
    return stats


# Initialize database on module import
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        print("Initializing database...")
        init_db()
        print("Database initialized successfully!")
    elif len(sys.argv) > 1 and sys.argv[1] == "drop":
        response = input("Are you sure you want to drop all tables? (yes/no): ")
        if response.lower() == "yes":
            drop_all_tables()
            print("All tables dropped!")
    else:
        print("Usage: python -m app.core.database [init|drop]")