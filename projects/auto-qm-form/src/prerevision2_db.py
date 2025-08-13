from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from src.config import get_settings

settings = get_settings()

# 同步 Engine（初期簡化；未來可換 async）
engine = create_engine(
    settings.DATABASE_URL,
    echo=(settings.APP_ENV == "dev"),
    future=True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
