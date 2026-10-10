from datetime import datetime, timezone

from app import db

MAX_SOURCE_URL_CHARS = 500


def utcnow():
    """naive UTC：与数据库里的 DateTime 列保持一致。"""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    url = db.Column(db.String(MAX_SOURCE_URL_CHARS), unique=True, nullable=False)
    category = db.Column(db.String(100), default="General")
    interval = db.Column(db.Integer, default=30)  # minutes
    enabled = db.Column(db.Boolean, default=True, nullable=False)
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
        db.Index("ix_article_read_published", "read", "published"),
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
