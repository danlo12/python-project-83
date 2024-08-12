import os
from urllib.parse import urlparse
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def normalize_url(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url


def check_url(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        html_content = response.text

        soup = BeautifulSoup(html_content, 'html.parser')
        h1 = soup.find('h1').text if soup.find('h1') else None
        title = soup.find('title').text if soup.find('title') else None
        description = soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={'name': 'description'}) and 'content' in soup.find('meta', attrs={'name': 'description'}).attrs else None

        return response.status_code, h1, title, description
    except requests.RequestException as e:
        print("Ошибка при запросе к URL:", e)
        return None, None, None, None
