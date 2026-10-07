"""数据库结构引导。

`db.create_all()` 只会新建缺失的表，不会给已存在的表补索引/约束。
所以升级到带唯一索引的版本时，这里做一次幂等补齐：
先清理历史重复文章（同一 link 只保留 id 最小的一条），再建唯一索引。

请在应用上下文内调用：`with app.app_context(): ensure_schema(app)`。
"""
import logging

from sqlalchemy import inspect, text

from app import db

logger = logging.getLogger(__name__)

INDEX_DDL = (
    ("uq_article_link", "CREATE UNIQUE INDEX IF NOT EXISTS uq_article_link ON article (link)"),
    ("ix_article_published", "CREATE INDEX IF NOT EXISTS ix_article_published ON article (published)"),
    ("ix_article_source_id", "CREATE INDEX IF NOT EXISTS ix_article_source_id ON article (source_id)"),
)

_FIND_DUPLICATES = text(
    "SELECT link FROM article "
    "WHERE link IS NOT NULL AND link <> '' "
    "GROUP BY link HAVING COUNT(*) > 1"
)

_DELETE_DUPLICATES = text(
    "DELETE FROM article WHERE link = :link AND id NOT IN "
    "(SELECT MIN(id) FROM article WHERE link = :link)"
)


def _cleanup_articles(conn):
    """删除重复文章与空链接记录，返回删除条数。"""
    removed = conn.execute(
        text("DELETE FROM article WHERE link IS NULL OR link = ''")
    ).rowcount or 0

    for (link,) in conn.execute(_FIND_DUPLICATES).fetchall():
        removed += conn.execute(_DELETE_DUPLICATES, {"link": link}).rowcount or 0

    if removed:
        logger.warning("已清理 %d 条重复/无效文章记录（升级唯一索引所需）", removed)
    return removed


def ensure_schema(app=None):
    """建表并补齐索引；可重复调用。"""
    db.create_all()

    with db.engine.begin() as conn:
        if "article" not in inspect(conn).get_table_names():
            return

        _cleanup_articles(conn)

        for name, ddl in INDEX_DDL:
            try:
                conn.execute(text(ddl))
            except Exception as exc:  # noqa: BLE001 - 索引建不上不应阻断启动
                logger.warning("创建索引 %s 失败：%s", name, exc)
