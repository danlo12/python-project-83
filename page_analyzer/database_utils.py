from flask import Flask, redirect, url_for, flash, render_template, get_flashed_messages
import requests
import psycopg2
import os
from urllib.parse import urlparse
from contextlib import contextmanager
from dotenv import load_dotenv
from bs4 import BeautifulSoup

app = Flask(__name__)
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app.secret_key = os.getenv('SECRET_KEY')


def get_base_url(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url


@contextmanager
def connect_to_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()


def get_or_create_url_id(conn, base_url):
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM urls WHERE name = %s", (base_url,))
        existing_id = cur.fetchone()
        if existing_id:
            return existing_id[0]
        else:
            cur.execute("INSERT INTO urls (name) VALUES (%s) RETURNING id", (base_url,))
            url_id = cur.fetchone()[0]
            conn.commit()
            return url_id
    except psycopg2.Error as e:
        print("Ошибка PostgreSQL:", e)
        return None
    finally:
        cur.close()


def add_url_to_db(url):
    base_url = get_base_url(url)
    try:
        with connect_to_db() as conn:
            if conn is None:
                return None
            return get_or_create_url_id(conn, base_url)
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return None


def is_url_in_db(url):
    base_url = get_base_url(url)
    with connect_to_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM urls WHERE name = %s", (base_url,))
        existing_id = cur.fetchone()
        return existing_id is not None


def get_urls_with_last_check():
    with connect_to_db() as conn:
        if conn is None:
            flash('Произошла ошибка при подключении к базе данных', 'danger')
            raise Exception("Ошибка при подключении к базе данных")
        try:
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
        except psycopg2.Error as e:
            print("Ошибка PostgreSQL:", e)
            flash('Произошла ошибка при выполнении запроса', 'danger')
            raise Exception("Ошибка при выполнении запроса")
        finally:
            cur.close()


def get_url_details(url_id):
    with connect_to_db() as conn:
        if conn is None:
            flash('Произошла ошибка при подключении к базе данных', 'danger')
            raise Exception("Ошибка при подключении к базе данных")

        try:
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
        except psycopg2.Error as e:
            print("Ошибка PostgreSQL:", e)
            flash('Произошла ошибка при выполнении запроса', 'danger')
            raise Exception("Произошла ошибка при выполнении запроса")
        finally:
            cur.close()


def check_url_status_and_store(url_id, created_at):
    with connect_to_db() as conn:
        if conn is None:
            flash('Произошла ошибка при подключении к базе данных', 'danger')
            return redirect(url_for('urls_id', url_id=url_id))

        try:
            cur = conn.cursor()
            cur.execute("SELECT name FROM urls WHERE id = %s", (url_id,))
            url_record = cur.fetchone()
            if url_record:
                url = url_record[0]

                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    html_content = response.text

                    soup = BeautifulSoup(html_content, 'html.parser')

                    h1_tag = soup.find('h1')
                    title_tag = soup.find('title')
                    meta_description_tag = soup.find('meta', attrs={'name': 'description'})

                    h1 = h1_tag.text if h1_tag else None
                    title = title_tag.text if title_tag else None
                    description = meta_description_tag[
                        'content'] if meta_description_tag and 'content' in meta_description_tag.attrs else None

                    status_code = response.status_code

                    cur.execute(
                        "INSERT INTO url_checks (url_id, created_at, status_code, h1, title, description) VALUES (%s, %s, %s, %s, %s, %s)",
                        (url_id, created_at, status_code, str(h1), str(title), str(description))
                    )
                    conn.commit()
                    flash('Страница успешно проверена', 'success')
                except requests.RequestException as e:
                    print("Ошибка при запросе к URL:", e)
                    flash('Произошла ошибка при проверке', 'danger')
            else:
                flash('URL не найден', 'warning')
        except psycopg2.Error as e:
            print("Ошибка PostgreSQL:", e)
            flash('Произошла ошибка при проверке', 'danger')
        finally:
            cur.close()
