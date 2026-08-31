import feedparser
import requests
import time
import logging
from datetime import datetime
from app import db
from app.models import Source, Article
from app.fulltext import extract_full_text

logger = logging.getLogger(__name__)

def fetch_source(source_id, notify=False):
    source = Source.query.get(source_id)
    if not source:
        return False, "Source not found"

    retries = 3
    for attempt in range(retries):
        try:
            resp = requests.get(source.url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if resp.status_code != 200:
                raise Exception(f"HTTP {resp.status_code}")
            feed = feedparser.parse(resp.content)
            if feed.bozo:
                logger.warning(f"Feed parse warning for {source.url}: {feed.bozo_exception}")

            new_articles = []
            for entry in feed.entries[:50]:
                link = entry.get('link', '')
                if not link:
                    continue
                if Article.query.filter_by(link=link).first():
                    continue

                # 获取全文（如需要）
                content = ''
                if 'content' in entry and entry.content:
                    content = entry.content[0].value[:5000]
                else:
                    content = extract_full_text(link)

                article = Article(
                    title=entry.get('title', 'Untitled'),
                    link=link,
                    summary=entry.get('summary', ''),
                    content=content,
                    published=datetime(*entry.published_parsed[:6]) if entry.get('published_parsed') else datetime.utcnow(),
                    source_id=source.id
                )
                db.session.add(article)
                new_articles.append(article)

            source.last_fetched = datetime.utcnow()
            db.session.commit()

            # 发送邮件通知
            if notify and new_articles:
                from app.notifications import send_email
                subject = f"RSS Aggregator: {source.name} 更新了 {len(new_articles)} 篇文章"
                body = "\n".join([a.title for a in new_articles])
                send_email(subject, body)

            logger.info(f"Fetched {len(new_articles)} new entries from {source.name}")
            return True, f"Fetched {len(new_articles)} new entries"
        except Exception as e:
            logger.error(f"Fetch attempt {attempt+1} failed for {source.url}: {e}")
            if attempt == retries - 1:
                return False, str(e)
            time.sleep(2)
    return False, "Failed after retries"
