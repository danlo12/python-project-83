from flask import Flask, request, render_template, redirect, url_for, flash
from datetime import datetime
from validators import url as validate_url
from .database_utils import add_url_to_db, extract_url_id_from_db, get_urls_with_last_check, get_url_details, is_url_in_db, save_url_check_to_db, get_url_from_db
import os
from dotenv import load_dotenv
from .urls import normalize_url
import requests
from .html_parser import parse_html_content

app = Flask(__name__)
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/urls', methods=['POST'])
def submit_url():
    url = normalize_url(request.form['url'])
    try:
        if validate_url(url):
            if not is_url_in_db(url):
                url_id = add_url_to_db(url)
                flash('Страница успешно добавлена', 'success')
                return redirect(url_for('urls_id', url_id=url_id))
            else:
                url_id = extract_url_id_from_db(url)
                flash('Страница уже существует', 'info')
                return redirect(url_for('urls_id', url_id=url_id))
        else:
            flash('Некорректный URL', 'danger')
            return render_template('index.html'), 422
    except Exception:
        flash('Произошла ошибка при обработке URL', 'danger')
        return render_template('index.html'), 422


@app.route('/urls', methods=['GET'])
def urls():
    try:
        urls_data = get_urls_with_last_check()
        return render_template('urls.html', urls=urls_data)
    except ConnectionError:
        flash('Произошла ошибка при подключении к базе данных', 'danger')
        return redirect(url_for('index'))


@app.route('/urls/<int:url_id>', methods=['GET', 'POST'])
def urls_id(url_id):
    try:
        url, checks = get_url_details(url_id)
        return render_template('urls_id.html', url=url, checks=checks)
    except Exception:
        flash('URL не найден', 'warning')
        return redirect(url_for('index'))


@app.route('/urls/<int:url_id>/checks', methods=['POST'])
def create_check(url_id):
    created_at = datetime.now()
    try:
        url = get_url_from_db(url_id)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html_content = response.text
        h1, title, description = map(str, parse_html_content(html_content))
        status_code = response.status_code
        save_url_check_to_db(url_id, created_at, status_code, h1, title, description)
    except Exception:
        flash('Произошла ошибка при проверке', 'danger')
    flash('Страница успешно проверена', 'success')
    return redirect(url_for('urls_id', url_id=url_id))


if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG')
    app.run(debug=debug_mode)
