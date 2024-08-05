from flask import Flask, request, render_template, redirect, url_for, flash, make_response, session
from datetime import datetime
from validators import url as validate_url
from .database_utils import add_url_to_db, get_urls_with_last_check, get_url_details, is_url_in_db, perform_url_check_and_save_to_db
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app.secret_key = os.getenv('SECRET_KEY')


def process_url(url):
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
        session['invalid_url'] = url
        return redirect(url_for('urls'))


@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')


@app.route('/', methods=['POST'])
def index_post():
    if request.method == 'POST':
        url = request.form['url']
        try:
            return process_url(url)
        except Exception as e:
            print(f"Ошибка при обработке URL: {e}")
            flash('Произошла ошибка при обработке URL', 'danger')
            return redirect(url_for('index'))


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
        urls_data = get_urls_with_last_check()
        return render_template('urls.html', urls=urls_data)
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        flash('Произошла ошибка при подключении к базе данных', 'danger')
        return redirect(url_for('index'))


@app.route('/urls/<int:url_id>', methods=['GET', 'POST'])
def urls_id(url_id):
    try:
        url, checks, messages = get_url_details(url_id)
        return render_template('urls_id.html', url=url, checks=checks, messages=messages)
    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {e}")
        flash('Произошла ошибка при подключении к базе данных', 'danger')
        return redirect(url_for('index'))


@app.route('/urls/<int:url_id>/checks', methods=['POST'])
def create_check(url_id):
    if request.method == 'POST':
        created_at = datetime.now()
        try:
            perform_url_check_and_save_to_db(url_id, created_at)
        except Exception as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            flash('Произошла ошибка при подключении к базе данных', 'danger')
    return redirect(url_for('urls_id', url_id=url_id))


if __name__ == '__main__':
    app.run(debug=True)
