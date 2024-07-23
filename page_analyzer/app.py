from flask import Flask, request, render_template, redirect, url_for, flash, get_flashed_messages ,abort
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from validators import url as validate_url
from urllib.parse import urlparse
from contextlib import contextmanager

app = Flask(__name__)
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app.secret_key = os.getenv('SECRET_KEY')

@contextmanager
def connect_to_db():
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        yield conn
    except Exception as e:
        print(f"Can't establish connection to database: {e}")
        yield None
    finally:
        if conn:
            conn.close()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if validate_url(url):
            if not is_url_in_db(url):
                url_id = add_url_to_db(url)
                flash('Страница успешно добавлена', 'success')
                return redirect(url_for('urls_id', url_id=url_id))
            else:
                url_id = add_url_to_db(url)
                flash('Страница уже существует', 'info')
                return redirect(url_for('urls_id', url_id=url_id))
        else:
            return redirect(url_for('urls', index_url=url))

    return render_template('index.html')


def add_url_to_db(url):
    base_url = get_base_url(url)
    try:
        with connect_to_db() as conn:
            if conn is None:
                return None

            try:
                cur = conn.cursor()
                cur.execute("SELECT id FROM urls WHERE name = %s", (base_url,))
                existing_id = cur.fetchone()
                if existing_id:
                    url_id = existing_id[0]
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
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return None


def is_url_in_db(url):
    base_url = get_base_url(url)
    try:
        with connect_to_db() as conn:
            if conn is None:
                return False

            try:
                cur = conn.cursor()
                cur.execute("SELECT id FROM urls WHERE name = %s", (base_url,))
                existing_id = cur.fetchone()
                return existing_id is not None
            except psycopg2.Error as e:
                print("Ошибка PostgreSQL:", e)
                return False
            finally:
                cur.close()
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        return False
def get_base_url(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url

@app.route('/urls', methods=['GET', 'POST'])
def urls():
    index_url = request.args.get('index_url', 'https://www.google.com/')
    if not validate_url(index_url):
        flash('Некорректный URL', 'danger')
        return render_template('index.html', code=422)

    try:
        with connect_to_db() as conn:
            if conn is None:
                flash('Произошла ошибка при подключении к базе данных', 'danger')
                return redirect(url_for('index'))

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
                return render_template('urls.html', urls=urls)
            except psycopg2.Error as e:
                print("Ошибка PostgreSQL:", e)
                flash('Произошла ошибка при выполнении запроса', 'danger')
                return redirect(url_for('index'))
            finally:
                cur.close()
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        flash('Произошла ошибка при подключении к базе данных', 'danger')
        return redirect(url_for('index'))

@app.route('/urls/<int:url_id>', methods=['GET', 'POST'])
def urls_id(url_id):
    try:
        with connect_to_db() as conn:
            if conn is None:
                flash('Произошла ошибка при подключении к базе данных', 'danger')
                return redirect(url_for('index'))

            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
                url = cur.fetchone()
                if url is None:
                    flash('URL не найден', 'warning')
                    return redirect(url_for('index'))

                cur.execute("SELECT * FROM url_checks WHERE url_id = %s", (url_id,))
                checks = cur.fetchall()
                messages = get_flashed_messages(with_categories=True)
                return render_template('urls_id.html', url=url, checks=checks, messages=messages)
            except psycopg2.Error as e:
                print("Ошибка PostgreSQL:", e)
                flash('Произошла ошибка при выполнении запроса', 'danger')
                return redirect(url_for('index'))
            finally:
                cur.close()
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        flash('Произошла ошибка при подключении к базе данных', 'danger')
        return redirect(url_for('index'))

@app.route('/urls/<int:url_id>/checks', methods=['POST'])
def create_check(url_id):
    if request.method == 'POST':
        created_at = datetime.now()

        try:
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
                            html_content = response.text

                            soup = BeautifulSoup(html_content, 'html.parser')

                            h1_tag = soup.find('h1')
                            title_tag = soup.find('title')
                            meta_description_tag = soup.find('meta', attrs={'name': 'description'})

                            h1 = h1_tag.text if h1_tag else None
                            title = title_tag.text if title_tag else None
                            description = meta_description_tag['content'] if meta_description_tag and 'content' in meta_description_tag.attrs else None

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
                            flash('Произошла ошибка при проверке', 'danger')
                            flash('Произошла ошибка при проверке', 'danger')
                            flash('Произошла ошибка при проверке', 'danger')
                    else:
                        flash('URL не найден', 'warning')
                except psycopg2.Error as e:
                    print("Ошибка PostgreSQL:", e)
                    flash('Произошла ошибка при проверке', 'danger')
                finally:
                    cur.close()
        except Exception as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            flash('Произошла ошибка при подключении к базе данных', 'danger')

    return redirect(url_for('urls_id', url_id=url_id))

if __name__ == '__main__':
    app.run(debug=True)