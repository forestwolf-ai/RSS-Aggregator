import feedparser
import requests
import time
from datetime import datetime
from app import db
from app.models import Source, Article

def fetch_source(source_id, notify=False):
    source = Source.query.get(source_id)
    if not source:
        return False, "Source not found"
    
    retries = 3
    for attempt in range(retries):
        try:
            resp = requests.get(source.url, timeout=15)
            if resp.status_code != 200:
                raise Exception(f"HTTP {resp.status_code}")
            feed = feedparser.parse(resp.content)
            
            new_articles = []
            for entry in feed.entries[:50]:
                link = entry.get('link', '')
                if not link:
                    continue
                existing = Article.query.filter_by(link=link).first()
                if existing:
                    continue
                
                article = Article(
                    title=entry.get('title', 'Untitled'),
                    link=link,
                    summary=entry.get('summary', ''),
                    published=datetime(*entry.published_parsed[:6]) if entry.get('published_parsed') else datetime.utcnow(),
                    source_id=source.id
                )
                db.session.add(article)
                new_articles.append(article)
            
            source.last_fetched = datetime.utcnow()
            db.session.commit()
            
            # 如果启用通知且有新文章，发送邮件
            if notify and new_articles:
                from app.notifications import send_email
                from app.config import ConfigLoader
                config = ConfigLoader().get('notifications.email')
                subject = f"RSS Aggregator: {source.name} 更新了 {len(new_articles)} 篇文章"
                body = "\n".join([a.title for a in new_articles])
                send_email(subject, body, config)
            
            return True, f"Fetched {len(new_articles)} new entries"
        except Exception as e:
            if attempt == retries - 1:
                return False, str(e)
            time.sleep(2)
    return False, "Failed after retries"
