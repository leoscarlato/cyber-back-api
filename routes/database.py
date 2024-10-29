import os
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

def create_database(url):
    db_name = url.rsplit('/', 1)[-1]
    engine = create_engine(url.rsplit('/', 1)[0])

    with engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
        print(f"Database '{db_name}' created or already exists.")

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    conn = engine.connect()
    conn.close()
    print("Connected to the database successfully.")
except OperationalError:
    create_database(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
