import psycopg2
from psycopg2 import OperationalError
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
    except OperationalError as e:
        print("❌ Veritabanı bağlantı hatası:", e)
        raise

# Tabloyu sadece bir kere oluşturmak için istersen burada fonksiyon olarak koyabilirsin.
def create_table_if_not_exists():
    conn = get_db_connection()
    cursor = conn.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS ratings (
        id SERIAL PRIMARY KEY,
        kod_adi TEXT,
        ex_ismi TEXT,
        empati INTEGER,
        guvenilirlik INTEGER,
        duygusallik INTEGER,
        romantiklik INTEGER,
        espri_anlayisi INTEGER,
        zeka INTEGER,
        hirs INTEGER,
        tutku INTEGER,
        sorumluluk INTEGER,
        durustluk INTEGER,
        kiskanclik INTEGER,
        sosyal_hayat INTEGER,
        seyahat_macera INTEGER,
        fiziksel_cekicilik INTEGER,
        cinsel_uyum INTEGER,
        opucuk_kalitesi INTEGER,
        on_sevisme INTEGER,
        yatakta_yaraticilik INTEGER,
        fanteziye_aciklik INTEGER,
        cinsel_istek INTEGER
    );
    """
    cursor.execute(create_table_query)
    conn.commit()
    cursor.close()
    conn.close()
