from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base

engine = create_engine(
    "sqlite:///./patients_db.sqlite3",
    echo=True,
    future=True,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    future=True,
)

Base.metadata.create_all(bind=engine)
