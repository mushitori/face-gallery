from pathlib import Path

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from face_gallery.config import get_settings

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def _schema_path() -> Path:
    return Path(__file__).parent / "schema.sql"


def _configure_sqlite(dbapi_conn) -> None:  # noqa: ANN001
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA busy_timeout=60000")
    cursor.close()


def init_db() -> None:
    global _engine, _SessionLocal
    settings = get_settings()
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    url = f"sqlite:///{settings.db_path}"
    _engine = create_engine(
        url,
        connect_args={"check_same_thread": False, "timeout": 30},
    )

    @event.listens_for(_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, _):  # noqa: ANN001
        _configure_sqlite(dbapi_conn)

    schema = _schema_path().read_text(encoding="utf-8")
    with _engine.begin() as conn:
        for stmt in schema.split(";"):
            s = stmt.strip()
            if s:
                conn.execute(text(s))
        _apply_migrations(conn)

    _SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False)


def _apply_migrations(conn) -> None:  # noqa: ANN001
    try:
        conn.execute(
            text("ALTER TABLE jobs ADD COLUMN force INTEGER NOT NULL DEFAULT 0")
        )
    except Exception:
        pass
    try:
        conn.execute(
            text(
                "ALTER TABLE jobs ADD COLUMN pause_requested INTEGER NOT NULL DEFAULT 0"
            )
        )
    except Exception:
        pass


def get_engine() -> Engine:
    if _engine is None:
        init_db()
    assert _engine is not None
    return _engine


def get_session() -> Session:
    if _SessionLocal is None:
        init_db()
    assert _SessionLocal is not None
    return _SessionLocal()


def commit_session(session: Session) -> None:
    from face_gallery.db.retry import run_with_retry

    def _commit() -> None:
        session.commit()

    run_with_retry(_commit)
