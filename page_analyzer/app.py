from flask import Flask, request, render_template, redirect, url_for, flash, get_flashed_messages
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from validators import url as validate_url

app = Flask(__name__)
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app.secret_key = 'your_secret_key_here'

def connect_to_db():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except:
        print('Can`t establish connection to database')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if validate_url(url):
            url_id = add_url_to_db(url)
            flash('Страница успешно добавлена', 'success')
            return redirect(url_for('urls_id', url_id=url_id))
        else:
            flash('Некорректный URL', 'danger')

    return render_template('index.html')

def add_url_to_db(url):
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM urls WHERE name = %s", (url,))
        existing_id = cur.fetchone()
        if existing_id:
            url_id = existing_id[0]
        else:
            cur.execute("INSERT INTO urls (name) VALUES (%s) RETURNING id", (url,))
            url_id = cur.fetchone()[0]
            conn.commit()
        return url_id
    except psycopg2.Error as e:
        print("Ошибка PostgreSQL:", e)
    finally:
        conn.close()

@app.route('/urls/<int:url_id>', methods=['GET', 'POST'])
def urls_id(url_id):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM urls WHERE id = %s", (url_id,))
    url = cur.fetchone()
    cur.execute("SELECT * FROM url_checks WHERE url_id = %s", (url_id,))
    checks = cur.fetchall()
    conn.close()
    messages = get_flashed_messages(with_categories=True)
    return render_template('urls_id.html', url=url,checks=checks,messages=messages)

@app.route('/urls')
def urls():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("""
            SELECT urls.id, urls.name, MAX(url_checks.created_at) AS last_check_date,
            url_checks.status_code
            FROM urls
            LEFT JOIN url_checks ON urls.id = url_checks.url_id
            GROUP BY urls.id, urls.name, url_checks.status_code 
        """)
    urls = cur.fetchall()
    conn.close()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<int:url_id>/checks', methods=['POST'])
def create_check(url_id):
    if request.method == 'POST':
        try:
            # Получаем текущее время для поля created_at
            created_at = datetime.now()

            conn = connect_to_db()
            cur = conn.cursor()
            cur.execute("SELECT name FROM urls WHERE id = %s", (url_id,))
            url_record = cur.fetchone()
            conn.close()
            if url_record:
                url = url_record[0]

            # Получаем HTML-контент страницы
                response = requests.get(url)
                html_content = response.text

                # Парсим HTML-контент с помощью BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')

                # Извлекаем теги h1, title и meta с атрибутом name="description"
                h1_tag = soup.find('h1')
                title_tag = soup.find('title')
                meta_description_tag = soup.find('meta', attrs={'name': 'description'})

                # Извлекаем текст из тегов, если они найдены
                h1 = h1_tag.text if h1_tag else None
                title = title_tag.text if title_tag else None
                description = meta_description_tag['content'] if meta_description_tag and 'content' in meta_description_tag.attrs else None

                # Получаем статус-код ответа
                status_code = response.status_code

                # Создаем новую запись проверки в базе данных
                conn = connect_to_db()
                cur = conn.cursor()
                cur.execute("INSERT INTO url_checks (url_id, created_at, status_code, h1, title, description) VALUES (%s, %s, %s, %s, %s, %s)", (url_id, created_at, status_code, str(h1), str(title), str(description)))
                conn.commit()
                conn.close()

                flash('Страница успешно проверена', 'success')
        except (psycopg2.Error, requests.RequestException) as e:
            print("Ошибка:", e)
            flash('Ошибка при проверке', 'error')

    # Перенаправляем пользователя обратно на страницу с URL'ом
    return redirect(url_for('urls_id', url_id=url_id))

if __name__ == '__main__':
    app.run(debug=True)