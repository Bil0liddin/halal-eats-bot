from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def get_session() -> Session:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db() -> None:
    from app import models  # noqa: F401 (register models on Base.metadata)
    from app.models import Base

    Base.metadata.create_all(bind=engine)
    _ensure_column("users", "language", "VARCHAR(8)")
    _ensure_column("products", "image_url", "VARCHAR(500)")


def _ensure_column(table: str, column: str, sql_type: str) -> None:
    if engine.dialect.name != "sqlite":
        return
    with engine.connect() as conn:
        columns = {row[1] for row in conn.exec_driver_sql(f"PRAGMA table_info({table})")}
        if column not in columns:
            conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}")
            conn.commit()
