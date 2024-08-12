from flask import flash, get_flashed_messages
import psycopg2
from psycopg2 import extras
import os
from contextlib import contextmanager
from dotenv import load_dotenv
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
from .config import check_url



@contextmanager
def connect_to_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    except psycopg2.Error as e:
        print("Ошибка при подключении к базе данных:", e)
        yield None
    finally:
        conn.close()


def get_url_id(conn, base_url):
    with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("SELECT id FROM urls WHERE name = %s", (base_url,))
        existing_id = cur.fetchone()
        if existing_id:
            return existing_id['id']
        return None


def create_url(conn, base_url):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO urls (name) VALUES (%s) RETURNING id", (base_url,))
        url_id = cur.fetchone()[0]
        conn.commit()
        return url_id


def add_url_to_db(url):
    with connect_to_db() as conn:
        url_id = get_url_id(conn, url)
        if url_id is not None:
            return url_id

        return create_url(conn, url)


def is_url_in_db(url):
    with connect_to_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM urls WHERE name = %s", (url,))
        existing_id = cur.fetchone()
        return existing_id is not None


def get_urls_with_last_check():
    with connect_to_db() as conn:
        cur = conn.cursor()
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
        if conn is None:
            flash('Произошла ошибка при подключении к базе данных', 'danger')
            raise Exception("Ошибка при подключении к базе данных")

        cur = conn.cursor()
        cur.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
        url = cur.fetchone()
        if url is None:
            flash('URL не найден', 'warning')
            raise Exception("URL не найден")

        cur.execute("SELECT * FROM url_checks WHERE url_id = %s", (url_id,))
        checks = cur.fetchall()
        messages = get_flashed_messages(with_categories=True)
        return url, checks, messages


def get_url_from_db(conn, url_id):
    with conn.cursor() as cur:
        cur.execute("SELECT name FROM urls WHERE id = %s", (url_id,))
        url_record = cur.fetchone()
        return url_record[0] if url_record else None


def save_url_check_to_db(conn, url_id, created_at, status_code, h1, title, description):
    with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO url_checks (url_id, created_at, status_code, h1, title, description) VALUES (%s, %s, %s, %s, %s, %s)",
            (url_id, created_at, status_code, str(h1), str(title), str(description))
        )
        conn.commit()
        flash('Страница успешно проверена', 'success')


def perform_url_check_and_save_to_db(url_id, created_at):
    with connect_to_db() as conn:
        if conn is None:
            flash('Произошла ошибка при подключении к базе данных', 'danger')
            raise Exception("Произошла ошибка при подключении к базе данных")

        url = get_url_from_db(conn, url_id)
        if not url:
            flash('URL не найден', 'warning')
            return

        status_code, h1, title, description = check_url(url)
        if status_code is None:
            flash('Произошла ошибка при проверке', 'danger')
        else:
            save_url_check_to_db(conn, url_id, created_at, status_code, h1, title, description)
