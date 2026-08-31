from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app import db
from app.models import Source, Article
from app.fetcher import fetch_source
from app.i18n import translate
from app.search import search_articles
from app.opml import export_opml, import_opml

web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    lang = request.args.get('lang', current_app.config.get('APP_LANGUAGE', 'en'))
    page = request.args.get('page', 1, type=int)
    sources = Source.query.all()
    articles = Article.query.order_by(Article.published.desc()).paginate(page=page, per_page=50, error_out=False)
    return render_template('index.html',
                           sources=sources,
                           articles=articles,
                           lang=lang,
                           _=lambda k: translate(k, lang))

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
        # 立即抓取并允许通知
        fetch_source(source.id, notify=True)
        flash('Source added and fetched.')
    return redirect(url_for('web.index'))

@web_bp.route('/delete_source/<int:source_id>')
def delete_source(source_id):
    source = Source.query.get_or_404(source_id)
    db.session.delete(source)
    db.session.commit()
    return redirect(url_for('web.index'))

@web_bp.route('/refresh_source/<int:source_id>')
def refresh_source(source_id):
    fetch_source(source_id, notify=True)
    return redirect(url_for('web.index'))

@web_bp.route('/search')
def search():
    lang = request.args.get('lang', current_app.config.get('APP_LANGUAGE', 'en'))
    query = request.args.get('q', '')
    source_id = request.args.get('source_id', type=int)
    unread = request.args.get('unread', 'false').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    pagination = search_articles(query, source_id, unread, page=page, per_page=50)
    sources = Source.query.all()
    return render_template('index.html',
                           sources=sources,
                           articles=pagination,
                           lang=lang,
                           _=lambda k: translate(k, lang),
                           search_query=query,
                           search_source_id=source_id,
                           search_unread=unread)

@web_bp.route('/export_opml')
def export_opml_route():
    opml_content = export_opml()
    return current_app.response_class(
        opml_content,
        mimetype='text/xml',
        headers={'Content-Disposition': 'attachment;filename=feeds.opml'}
    )

@web_bp.route('/import_opml', methods=['POST'])
def import_opml_route():
    file = request.files.get('opml_file')
    if file:
        success, failed = import_opml(file.read().decode('utf-8', errors='ignore'))
        flash(f"Imported {success} feeds, failed: {failed}")
    return redirect(url_for('web.index'))
