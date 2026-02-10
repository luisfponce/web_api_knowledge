from sqlmodel import SQLModel, create_engine, Session
from core import config
# from sqlalchemy.ext.asyncio import AsyncSession

connect_args = {"check_same_thread": False}
engine = create_engine(config.DB_URL, echo=True)

# Actually create the tables in the database
# If using SQLite, the database file will be created in the current directory
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session