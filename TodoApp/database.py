from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = (
    "postgresql+psycopg://postgres:Test9561@localhost:5432/TodoAplicationDatabase"
)



engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
