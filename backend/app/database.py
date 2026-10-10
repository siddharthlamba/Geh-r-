import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./gehor.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def run_migrations():
    """
    Safely ensures all tables and backward-compatible columns exist.
    """
    Base.metadata.create_all(bind=engine)
    
    # SQLite schema migration for Complaint model
    if "sqlite" in DATABASE_URL:
        with engine.connect() as conn:
            cursor = conn.execute(text("PRAGMA table_info(complaints)"))
            existing_cols = {row[1] for row in cursor.fetchall()}
            
            new_columns = [
                ("ai_summary", "TEXT"),
                ("resolution_plan", "TEXT"),
                ("predicted_department", "VARCHAR(100)"),
                ("routing_confidence", "FLOAT DEFAULT 0.92"),
                ("routing_mode", "VARCHAR(30) DEFAULT 'SUPERVISED'"),
                ("ai_provider", "VARCHAR(50) DEFAULT 'gemini_free_tier'"),
                ("verified_email", "VARCHAR(120)")
            ]
            
            for col_name, col_type in new_columns:
                if col_name not in existing_cols:
                    conn.execute(text(f"ALTER TABLE complaints ADD COLUMN {col_name} {col_type}"))
            conn.commit()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
