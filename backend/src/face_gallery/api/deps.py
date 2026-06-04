from sqlalchemy.orm import Session

from face_gallery.db.connection import get_session


def get_db() -> Session:
    session = get_session()
    try:
        yield session
    finally:
        session.close()
