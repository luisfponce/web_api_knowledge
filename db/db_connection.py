from sqlmodel import SQLModel, create_engine, Session
import os
# from sqlalchemy.ext.asyncio import AsyncSession

# Ensure that the environment variable DB_URL is set to your MariaDB connection string
# Example: export DB_URL="mariadb+mariadbconnector://user:psw@127.0.0.1:3306/bank_db"

DB_URL = os.getenv("DB_URL")
if not DB_URL:
    DB_URL = "sqlite:///./bank_db.db"  # Default to SQLite if no environment variable is set

connect_args = {"check_same_thread": False}
engine = create_engine(DB_URL, echo=True)

# Actually create the tables in the database
# If using SQLite, the database file will be created in the current directory
SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session