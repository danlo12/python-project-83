from flask import Flask, request, render_template, redirect, url_for, flash
import psycopg2
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')
app.secret_key = 'your_secret_key_here'

def connect_to_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        add_url_to_db(url)
        flash('URL успешно добавлен', 'success')
        return redirect(url_for('index'))
    else:
        return render_template('index.html')

def add_url_to_db(url):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO urls (name) VALUES (%s)", (url,))
    conn.commit()
    conn.close()


@app.route('/urls', methods=['GET', 'POST'])
def urls():
    if request.method == 'POST':
        url = request.form['url']
        add_url_to_db(url)
        flash('URL успешно добавлен', 'success')
        return redirect(url_for('urls'))
    else:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM urls ORDER BY id DESC")
        urls = cur.fetchall()
        conn.close()
        return render_template('urls.html', urls=urls)

if __name__ == '__main__':
    app.run(debug=True)