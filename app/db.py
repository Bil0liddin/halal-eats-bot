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
    _ensure_language_column()


def _ensure_language_column() -> None:
    if engine.dialect.name != "sqlite":
        return
    with engine.connect() as conn:
        columns = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(users)")}
        if "language" not in columns:
            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN language VARCHAR(8)")
            conn.commit()
