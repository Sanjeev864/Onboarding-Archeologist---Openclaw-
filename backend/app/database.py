from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
if settings.database_url.startswith("sqlite:///"):
    db_path = settings.database_url.replace("sqlite:///", "")
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_sqlite_schema() -> None:
    if not settings.database_url.startswith("sqlite"):
        return

    inspector = inspect(engine)
    if "repositories" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("repositories")}
    additions = {
        "last_webhook_received": "DATETIME",
        "webhook_secret": "VARCHAR(200)",
        "auto_reanalyze": "BOOLEAN DEFAULT 0",
        "total_commits_analyzed": "INTEGER DEFAULT 0",
        "coverage_percentage": "FLOAT DEFAULT 0.0",
    }
    with engine.begin() as connection:
        for name, definition in additions.items():
            if name not in columns:
                connection.execute(text(f"ALTER TABLE repositories ADD COLUMN {name} {definition}"))
