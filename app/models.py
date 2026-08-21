from app import db
from datetime import datetime

class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    url = db.Column(db.String(500), unique=True, nullable=False)
    category = db.Column(db.String(100), default="General")
    interval = db.Column(db.Integer, default=30)  # minutes
    last_fetched = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    articles = db.relationship('Article', backref='source', lazy='dynamic', cascade="all, delete-orphan")

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    link = db.Column(db.String(1000))
    summary = db.Column(db.Text)
    content = db.Column(db.Text)
    published = db.Column(db.DateTime)
    read = db.Column(db.Boolean, default=False)
    source_id = db.Column(db.Integer, db.ForeignKey('source.id'))