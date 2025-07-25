from dotenv import load_dotenv

import os

import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv(dotenv_path=r'C:\man_rate_project\.env')

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "db.cwiqviwqmbgvzlbdritv.supabase.co"),
        port=int(os.getenv("DB_PORT", 5432)),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "Mine12345.6463"),  # .env'deki DB_PASSWORD ile eşleşmeli
        database=os.getenv("DB_NAME", "postgres"),
        cursor_factory=RealDictCursor
    )
    return conn
