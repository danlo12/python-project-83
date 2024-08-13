from bs4 import BeautifulSoup


def parse_html_content(html_content):
    if not html_content:
        return None, None, None, None

    soup = BeautifulSoup(html_content, 'html.parser')

    h1 = soup.find('h1').text if soup.find('h1') else None
    title = soup.find('title').text if soup.find('title') else None
    description = soup.find('meta', attrs={'name': 'description'})['content'] if soup.find('meta', attrs={
        'name': 'description'}) and 'content' in soup.find('meta', attrs={'name': 'description'}).attrs else None

    return h1, title, description
