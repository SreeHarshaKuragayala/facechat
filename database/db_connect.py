import psycopg2
from config.settings import DB_CONFIG

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def run_query(query, params=None, fetch=False):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    result = None
    if fetch:
        result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return result