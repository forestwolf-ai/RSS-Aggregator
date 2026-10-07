"""Web 路由。

修复要点：
1. 蓝图必须声明 template_folder='templates'。模板在 app/web/templates/，
   而 Flask(__name__) 只会去 app/templates/ 找，原来每个页面都
   TemplateNotFound → 整站 500。
2. 分页链接保留当前查询条件（原来用 request.view_args，把 q / lang / source_id /
   unread 全丢了，搜索翻到第二页就变成全量列表）。
3. 会改状态的操作用 POST（原来是 GET：浏览器预取、<img> 标签、爬虫都能删库）。
4. interval 容错解析并强制 ≥ 5 分钟（原来非数字直接 500，0/负数会注册非法任务）。
5. 重复 URL 友好提示而不是 IntegrityError 500；新增/导入的源立即注册调度任务。
6. 补上「标记已读」入口，让 unread 过滤形成闭环（原来 read 永远是 False）。
"""
import logging

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy.exc import IntegrityError

from app import db
from app.fetcher import fetch_source
from app.i18n import translate
from app.models import Article, Source
from app.opml import export_opml, import_opml
from app.search import search_articles
from app.security import check_csrf_origin
from app.urlsafety import is_safe_url

logger = logging.getLogger(__name__)

MIN_INTERVAL_MINUTES = 5
DEFAULT_INTERVAL_MINUTES = 30
PER_PAGE = 50
MAX_OPML_BYTES = 5 * 1024 * 1024
FILTER_KEYS = ("q", "source_id", "unread", "lang")

web_bp = Blueprint("web", __name__, template_folder="templates")
web_bp.before_request(check_csrf_origin)


# --------------------------------------------------------------------------- #
# 辅助函数
# --------------------------------------------------------------------------- #
def _language():
    return request.args.get("lang") or current_app.config.get("APP_LANGUAGE", "en")


def _page_url(page):
    """保留当前查询条件的分页链接。"""
    args = request.args.to_dict(flat=True)
    args["page"] = page
    return url_for(request.endpoint, **args)


def _lang_url(language):
    """切换语言时保留其它查询条件。"""
    args = request.args.to_dict(flat=True)
    args["lang"] = language
    args.pop("page", None)
    return url_for(request.endpoint, **args)


def _context(**extra):
    lang = _language()
    context = {
        "lang": lang,
        "_": lambda key: translate(key, lang),
        "page_url": _page_url,
        "lang_url": _lang_url,
        # 原来模板只取 i18n 字典，config.yaml 里的 app.name 配了也不会显示
        "app_name": current_app.config.get("APP_NAME") or translate("app_name", lang),
    }
    context.update(extra)
    return context


def _parse_interval(raw, default=DEFAULT_INTERVAL_MINUTES):
    """容错解析更新间隔，并强制不小于 5 分钟。"""
    try:
        value = int(str(raw).strip())
    except (TypeError, ValueError):
        return max(MIN_INTERVAL_MINUTES, int(default or DEFAULT_INTERVAL_MINUTES))
    return max(MIN_INTERVAL_MINUTES, value)


def _scheduling_enabled():
    return bool(current_app.config.get("SCHEDULER_ENABLED", True))


def _schedule(source):
    """把源注册进调度器；调度器未启用时静默跳过。"""
    if not _scheduling_enabled():
        return
    from app.scheduler import schedule_source

    try:
        schedule_source(source, notify=True, app=current_app._get_current_object())
    except Exception as exc:  # noqa: BLE001 - 调度失败不应让页面 500
        logger.warning("注册调度任务失败 source=%s: %s", source.id, exc)


def _schedule_all():
    if not _scheduling_enabled():
        return
    from app.scheduler import schedule_source

    app = current_app._get_current_object()
    for source in Source.query.all():
        try:
            schedule_source(source, notify=True, app=app)
        except Exception as exc:  # noqa: BLE001
            logger.warning("注册调度任务失败 source=%s: %s", source.id, exc)


def _local_redirect(candidate, fallback):
    """只接受站内相对路径，避免开放重定向。"""
    if candidate and candidate.startswith("/") and not candidate.startswith("//"):
        return candidate
    return fallback


def _allow_private():
    return bool(current_app.config.get("SECURITY_ALLOW_PRIVATE_NETWORKS", False))


# --------------------------------------------------------------------------- #
# 页面
# --------------------------------------------------------------------------- #
@web_bp.route("/")
def index():
    page = request.args.get("page", 1, type=int) or 1
    articles = (
        Article.query.order_by(Article.published.desc(), Article.id.desc())
        .paginate(page=max(1, page), per_page=PER_PAGE, error_out=False)
    )
    return render_template(
        "index.html",
        **_context(sources=Source.query.order_by(Source.id).all(), articles=articles)
    )


@web_bp.route("/search")
def search():
    query = request.args.get("q", "")
    source_id = request.args.get("source_id", type=int)
    unread = request.args.get("unread", "false").lower() == "true"
    page = request.args.get("page", 1, type=int) or 1
    pagination = search_articles(query, source_id, unread, page=page, per_page=PER_PAGE)
    return render_template(
        "index.html",
        **_context(
            sources=Source.query.order_by(Source.id).all(),
            articles=pagination,
            search_query=query,
            search_source_id=source_id,
            search_unread=unread,
        )
    )


@web_bp.route("/healthz")
def healthz():
    """容器健康检查用。"""
    return "ok", 200, {"Content-Type": "text/plain; charset=utf-8"}


# --------------------------------------------------------------------------- #
# 源管理
# --------------------------------------------------------------------------- #
@web_bp.route("/add_source", methods=["POST"])
def add_source():
    url = (request.form.get("url") or "").strip()
    name = (request.form.get("name") or "").strip()
    category = (request.form.get("category") or "").strip() or "General"

    if not url:
        flash("Feed URL is required.")
        return redirect(url_for("web.index"))

    if not is_safe_url(url, allow_private=_allow_private()):
        logger.warning("拒绝添加被安全策略拦截的地址: %s", url)
        flash("该地址被安全策略拒绝（不允许内网/回环地址）")
        return redirect(url_for("web.index"))

    if Source.query.filter_by(url=url).first():
        flash(f"Feed already exists: {url}")
        return redirect(url_for("web.index"))

    interval = _parse_interval(
        request.form.get("interval"),
        current_app.config.get("SCHEDULER_DEFAULT_INTERVAL", DEFAULT_INTERVAL_MINUTES),
    )
    source = Source(name=name or url, url=url[:500], category=category[:100], interval=interval)
    db.session.add(source)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash(f"Feed already exists: {url}")
        return redirect(url_for("web.index"))

    _schedule(source)

    ok, message = fetch_source(source.id, notify=True)
    if ok:
        flash(f"Source added. {message}")
    else:
        flash(f"Source added, but the first fetch failed: {message}")
    return redirect(url_for("web.index"))


@web_bp.route("/delete_source/<int:source_id>", methods=["POST"])
def delete_source(source_id):
    source = db.get_or_404(Source, source_id)
    if _scheduling_enabled():
        from app.scheduler import unschedule_source

        unschedule_source(source.id)
    label = source.name or source.url
    db.session.delete(source)
    db.session.commit()
    flash(f"Deleted source: {label}")
    return redirect(url_for("web.index"))


@web_bp.route("/refresh_source/<int:source_id>", methods=["POST"])
def refresh_source(source_id):
    source = db.get_or_404(Source, source_id)
    ok, message = fetch_source(source.id, notify=True)
    flash(message if ok else f"Fetch failed: {message}")
    return redirect(url_for("web.index"))


@web_bp.route("/article/<int:article_id>/read", methods=["POST"])
def mark_read(article_id):
    article = db.get_or_404(Article, article_id)
    article.read = True
    db.session.commit()
    return redirect(
        _local_redirect(request.form.get("next"), url_for("web.index"))
    )


@web_bp.route("/article/<int:article_id>/unread", methods=["POST"])
def mark_unread(article_id):
    article = db.get_or_404(Article, article_id)
    article.read = False
    db.session.commit()
    return redirect(
        _local_redirect(request.form.get("next"), url_for("web.index"))
    )


# --------------------------------------------------------------------------- #
# OPML
# --------------------------------------------------------------------------- #
@web_bp.route("/export_opml")
def export_opml_route():
    content = export_opml()
    return current_app.response_class(
        content,
        mimetype="text/xml",
        headers={"Content-Disposition": "attachment; filename=feeds.opml"},
    )


@web_bp.route("/import_opml", methods=["POST"])
def import_opml_route():
    upload = request.files.get("opml_file")
    if upload is None or not upload.filename:
        flash("请选择要导入的 OPML 文件")
        return redirect(url_for("web.index"))

    raw = upload.read(MAX_OPML_BYTES + 1)
    if len(raw) > MAX_OPML_BYTES:
        flash("OPML 文件过大（上限 5 MB）")
        return redirect(url_for("web.index"))

    success, failed = import_opml(raw, allow_private=_allow_private())
    if success:
        _schedule_all()  # 新导入的源也要进入调度
    flash(f"Imported {success} feeds, failed: {failed}")
    return redirect(url_for("web.index"))


@web_bp.errorhandler(403)
def forbidden(error):  # pragma: no cover - 仅提供可读提示
    logger.warning("返回 403: %s", error)
    return "403 Forbidden: cross-site request blocked", 403
