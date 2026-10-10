import logging

from sqlalchemy import func

from app import db
from app.models import Article, utcnow

logger = logging.getLogger(__name__)


def retention_limits():
    """从配置读取保留策略；没有应用上下文时返回 (0, 0)。"""
    try:
        from flask import current_app, has_app_context

        if not has_app_context():
            return 0, 0
        return (
            max(0, int(current_app.config.get("RETENTION_MAX_ARTICLES_PER_SOURCE", 0) or 0)),
            max(0, int(current_app.config.get("RETENTION_MAX_AGE_DAYS", 0) or 0)),
        )
    except Exception:  # noqa: BLE001 - 保留策略不该影响抓取
        return 0, 0


def apply_retention(source_id, max_articles=None, max_age_days=None):
    """按保留策略清理某个源的文章，返回删除条数。"""
    if max_articles is None or max_age_days is None:
        configured_articles, configured_days = retention_limits()
        max_articles = configured_articles if max_articles is None else max_articles
        max_age_days = configured_days if max_age_days is None else max_age_days

    if not max_articles and not max_age_days:
        return 0

    removed = 0

    if max_age_days:
        cutoff = utcnow() - __import__("datetime").timedelta(days=max_age_days)
        removed += (
            db.session.query(Article)
            .filter(Article.source_id == source_id)
            .filter(Article.published.isnot(None))
            .filter(Article.published < cutoff)
            .delete(synchronize_session=False)
        )

    if max_articles:
        keep_ids = [
            row[0]
            for row in db.session.query(Article.id)
            .filter(Article.source_id == source_id)
            .order_by(Article.published.desc(), Article.id.desc())
            .limit(max_articles)
            .all()
        ]
        if keep_ids:
            removed += (
                db.session.query(Article)
                .filter(Article.source_id == source_id)
                .filter(~Article.id.in_(keep_ids))
                .delete(synchronize_session=False)
            )

    if removed:
        logger.info("按保留策略清理 source=%s 的 %d 篇文章", source_id, removed)
    return removed


def total_articles(source_id=None):
    query = db.session.query(func.count(Article.id))
    if source_id is not None:
        query = query.filter(Article.source_id == source_id)
    return query.scalar() or 0
