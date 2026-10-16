"""MySQL connection helper. Credentials come from environment variables (.env)."""
import os

import pymysql
from dotenv import load_dotenv
from fastapi import HTTPException
from pymysql.cursors import DictCursor

load_dotenv()  # reads backend/.env


def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "business_listings_db"),
        charset="utf8mb4",
        cursorclass=DictCursor,
        autocommit=False,
        connect_timeout=5,
    )


def get_db():
    """FastAPI dependency: opens one connection per request and always closes it."""
    try:
        conn = get_connection()
    except pymysql.MySQLError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to the database. Check that MySQL is running and backend/.env is correct.",
        )
    try:
        yield conn
    finally:
        conn.close()
