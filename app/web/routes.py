from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models import Source, Article
from app.fetcher import fetch_source
from app.i18n import translate
from flask import current_app, flash
from app.search import search_articles

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    lang = request.args.get('lang', 'en')
    sources = Source.query.all()
    articles = Article.query.order_by(Article.published.desc()).limit(100).all()
    return render_template('index.html', sources=sources, articles=articles, lang=lang, _=lambda k: translate(k, lang))

@web_bp.route('/add_source', methods=['POST'])
def add_source():
    name = request.form.get('name')
    url = request.form.get('url')
    category = request.form.get('category', 'General')
    interval = int(request.form.get('interval', 30))
    if url:
        source = Source(name=name, url=url, category=category, interval=interval)
        db.session.add(source)
        db.session.commit()
        fetch_source(source.id)
    return redirect(url_for('web.index'))

@web_bp.route('/delete_source/<int:source_id>')
def delete_source(source_id):
    source = Source.query.get_or_404(source_id)
    db.session.delete(source)
    db.session.commit()
    return redirect(url_for('web.index'))

@web_bp.route('/refresh_source/<int:source_id>')
def refresh_source(source_id):
    fetch_source(source_id)
    return redirect(url_for('web.index'))

@web_bp.route('/search')
def search():
    lang = request.args.get('lang', 'en')
    query = request.args.get('q', '')
    source_id = request.args.get('source_id', type=int)
    unread = request.args.get('unread', 'false').lower() == 'true'
    articles = search_articles(query, source_id, unread)
    sources = Source.query.all()
    return render_template('index.html', sources=sources, articles=articles, lang=lang, _=lambda k: translate(k, lang))

@web_bp.route('/export_opml')
def export_opml_route():
    from app.opml import export_opml
    opml_content = export_opml()
    return current_app.response_class(
        opml_content,
        mimetype='text/xml',
        headers={'Content-Disposition': 'attachment;filename=feeds.opml'}
    )

@web_bp.route('/import_opml', methods=['POST'])
def import_opml_route():
    from app.opml import import_opml
    file = request.files['opml_file']
    if file:
        success, failed = import_opml(file.read().decode('utf-8'))
        flash(f"Imported {success} feeds, failed: {failed}")
    return redirect(url_for('web.index'))
