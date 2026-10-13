from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import get_database_url

db_url = get_database_url()

engine = create_engine(db_url)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db_sql():
    """Launch POSTGRESql database session 

    Yields:
        _type_: Session
    """

    db = SessionLocal()
    # Base.metadata.drop_all(bind=engine)
    # Base.metadata.create_all(bind=engine)
    # db.execute(text('CREATE EXTENSION IF NOT EXISTS vector;'))
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
