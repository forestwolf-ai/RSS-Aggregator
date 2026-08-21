import requests
from bs4 import BeautifulSoup

def extract_full_text(url):
    """尝试从网页提取正文内容，失败返回空字符串"""
    try:
        resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(resp.text, 'lxml')
        # 常见正文标签
        article = soup.find('article') or soup.find('div', class_='content') or soup.find('div', class_='post') or soup.body
        if article:
            for tag in article(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                tag.decompose()
            text = article.get_text(separator='\n', strip=True)
            return text[:5000]
    except Exception:
        pass
    return ''