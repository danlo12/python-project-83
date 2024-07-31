from flask import Flask, request, render_template, redirect, url_for, flash, get_flashed_messages, make_response, session
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from validators import url as validate_url
from .database_utils import connect_to_db, process_url, get_urls_with_last_check, get_url_details
import psycopg2
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        try:
            return process_url(url)
        except Exception as e:
            print(f"Ошибка при обработке URL: {e}")
            flash('Произошла ошибка при обработке URL', 'danger')
            return redirect(url_for('index'))
    return render_template('index.html')


@app.route('/urls', methods=['GET'])
def urls():
    index_url = session.pop('invalid_url', None)
    if index_url and not validate_url(index_url):
        flash('Некорректный URL', 'danger')
        html_content = render_template('index.html')
        response = make_response(html_content)
        response.status_code = 422
        return response
    try:
        return get_urls_with_last_check()
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        flash('Произошла ошибка при подключении к базе данных', 'danger')
        return redirect(url_for('index'))


@app.route('/urls/<int:url_id>', methods=['GET', 'POST'])
def urls_id(url_id):
    try:
        return get_url_details(url_id)
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
                            response.raise_for_status()
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
