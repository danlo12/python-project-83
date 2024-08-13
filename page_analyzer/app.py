from flask import Flask, request, render_template, redirect, url_for, flash, make_response
from datetime import datetime
from validators import url as validate_url
from .database_utils import add_url_to_db, get_urls_with_last_check, get_url_details, is_url_in_db, perform_url_check_and_save_to_db
import os
from dotenv import load_dotenv
from .urls import normalize_url

app = Flask(__name__)
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')


@app.route('/urls', methods=['POST'])
def submit_url():
    url = request.form['url']
    try:
        if validate_url(url):
            if not is_url_in_db(normalize_url(url)):
                url_id = add_url_to_db(normalize_url(url))
                flash('Страница успешно добавлена', 'success')
                return redirect(url_for('urls_id', url_id=url_id))
            else:
                url_id = add_url_to_db(normalize_url(url))
                flash('Страница уже существует', 'info')
                return redirect(url_for('urls_id', url_id=url_id))
        else:
            flash('Некорректный URL', 'danger')
            return render_template('index.html'), 422
    except Exception as e:
        print(f"Ошибка при обработке URL: {e}")
        flash('Произошла ошибка при обработке URL', 'danger')
        response = make_response(render_template('index.html'))
        response.status_code = 422
        return response


@app.route('/urls', methods=['GET'])
def urls():
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
        url, checks = get_url_details(url_id)
        return render_template('urls_id.html', url=url, checks=checks)
    except Exception as e:
        print(f"URL не найден: {e}")
        flash('URL не найден', 'warning')
        return redirect(url_for('index'))


@app.route('/urls/<int:url_id>/checks', methods=['POST'])
def create_check(url_id):
    if request.method == 'POST':
        created_at = datetime.now()
        try:
            perform_url_check_and_save_to_db(url_id, created_at)
        except Exception as e:
            print(f"Ошибка при подключении к базе данных: {e}")
            flash('Произошла ошибка при проверке', 'danger')
        flash('Страница успешно проверена', 'success')
    return redirect(url_for('urls_id', url_id=url_id))


if __name__ == '__main__':
    app.run(debug=True)
