from psycopg2 import extras
import psycopg2
import os
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


@contextmanager
def connect_to_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()


def get_url_id(conn, base_url):
    with conn.cursor(cursor_factory=extras.DictCursor) as cur:
        cur.execute("SELECT id FROM urls WHERE name = %s", (base_url,))
        existing_id = cur.fetchone()
        if existing_id:
            return existing_id['id']
        return None


def create_url(conn, base_url):
    with conn.cursor(cursor_factory=extras.DictCursor) as cur:
        cur.execute("INSERT INTO urls (name) VALUES (%s) RETURNING id", (base_url,))
        url_id = cur.fetchone()['id']
        conn.commit()
        if url_id:
            return url_id
        return None


def add_url_to_db(url):
    with connect_to_db() as conn:
        return create_url(conn, url)


def extract_url_id_from_db(url):
    with connect_to_db() as conn:
        url_id = get_url_id(conn, url)
        return url_id


def is_url_in_db(url):
    with connect_to_db() as conn:
        cur = conn.cursor(cursor_factory=extras.DictCursor)
        cur.execute("SELECT id FROM urls WHERE name = %s", (url,))
        existing_id = cur.fetchone()
        if existing_id:
            return existing_id
        return None


def get_urls_with_last_check():
    with connect_to_db() as conn:
        cur = conn.cursor(cursor_factory=extras.DictCursor)
        cur.execute("""
                SELECT urls.id, urls.name, MAX(url_checks.created_at) AS last_check_date,
                url_checks.status_code
                FROM urls
                LEFT JOIN url_checks ON urls.id = url_checks.url_id
                GROUP BY urls.id, urls.name, url_checks.status_code
                ORDER BY urls.id DESC
            """)
        urls = cur.fetchall()
        return urls


def get_url_details(url_id):
    with connect_to_db() as conn:
        cur = conn.cursor(cursor_factory=extras.DictCursor)
        cur.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
        url = cur.fetchone()
        if url is None:
            raise Exception("URL не найден")
        cur.execute("SELECT * FROM url_checks WHERE url_id = %s", (url_id,))
        checks = cur.fetchall()
        return url, checks


def get_url_from_db(url_id):
    with connect_to_db() as conn:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            cur.execute("SELECT name FROM urls WHERE id = %s", (url_id,))
            url_record = cur.fetchone()
            if url_record:
                return url_record['name']
        return None


def save_url_check_to_db(url_id, created_at, status_code, h1, title, description):
    with connect_to_db() as conn:
        with conn.cursor(cursor_factory=extras.DictCursor) as cur:
            cur.execute(
                "INSERT INTO url_checks (url_id, created_at, status_code, h1, title, description) VALUES (%s, %s, %s, %s, %s, %s)",
                (url_id, created_at, status_code, h1, title, description)
            )
            conn.commit()
