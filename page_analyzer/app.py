from flask import Flask, request, render_template, redirect, url_for, flash
import psycopg2
import os
from dotenv import load_dotenv

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
        url_id = add_url_to_db(url)
        flash('URL успешно добавлен', 'success')
        return redirect(url_for('urls_id', url_id=url_id))

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
    return render_template('urls_id.html', url=url)

@app.route('/urls')
def urls():
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM urls")
    urls = cur.fetchall()
    conn.close()
    return render_template('urls.html', urls=urls)

if __name__ == '__main__':
    app.run(debug=True)