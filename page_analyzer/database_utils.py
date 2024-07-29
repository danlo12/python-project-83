from flask import Flask, request, render_template, redirect, url_for, flash, get_flashed_messages, make_response, session
import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from validators import url as validate_url
from urllib.parse import urlparse
from contextlib import contextmanager

DATABASE_URL = os.getenv('DATABASE_URL')


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



