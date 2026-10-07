"""ORM 模型。

修复要点：
1. `Article.link` 增加唯一索引。原来只靠「先查再插」去重，手动刷新（请求线程）
   与定时任务（调度线程）并发时会重复入库。
2. 增加排序/过滤用索引（published、source_id），避免翻页时全表排序。
3. 时间统一用 naive UTC，避免 aware/naive 混用，也避开 3.12 起废弃的 utcnow()。
"""
from datetime import datetime, timezone

from app import db


def utcnow():
    """naive UTC：与数据库里的 DateTime 列保持一致。"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    url = db.Column(db.String(500), unique=True, nullable=False)
    category = db.Column(db.String(100), default="General")
    interval = db.Column(db.Integer, default=30)  # minutes
    last_fetched = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    articles = db.relationship(
        "Article", backref="source", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Source {self.name}>"


class Article(db.Model):
    __table_args__ = (
        db.Index("uq_article_link", "link", unique=True),
        db.Index("ix_article_published", "published"),
        db.Index("ix_article_source_id", "source_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    link = db.Column(db.String(1000), nullable=False)
    summary = db.Column(db.Text)
    content = db.Column(db.Text)  # 全文内容
    published = db.Column(db.DateTime)
    read = db.Column(db.Boolean, default=False)
    source_id = db.Column(db.Integer, db.ForeignKey("source.id"))

    def __repr__(self):
        return f"<Article {self.title}>"
