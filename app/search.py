from app.models import Article, Source
from sqlalchemy import or_

def search_articles(query, source_id=None, unread_only=False, page=1, per_page=50):
    """全文搜索，支持分页"""
    q = Article.query
    if query:
        pattern = f'%{query}%'
        q = q.filter(or_(
            Article.title.like(pattern),
            Article.summary.like(pattern),
            Article.content.like(pattern)
        ))
    if source_id:
        q = q.filter(Article.source_id == source_id)
    if unread_only:
        q = q.filter(Article.read == False)
    return q.order_by(Article.published.desc()).paginate(page=page, per_page=per_page, error_out=False)
