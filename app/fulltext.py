import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def extract_full_text(url):
    """尝试从网页提取正文内容，失败返回空字符串"""
    try:
        resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        if resp.status_code != 200:
            return ''
        soup = BeautifulSoup(resp.text, 'lxml')
        article = soup.find('article') or soup.find('div', class_='content') or soup.find('div', class_='post') or soup.body
        if article:
            for tag in article(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()
            text = article.get_text(separator='\n', strip=True)
            return text[:5000]
    except Exception as e:
        logger.warning(f"Fulltext extraction failed for {url}: {e}")
    return ''
