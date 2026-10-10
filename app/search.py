from sqlalchemy import or_

from app.models import Article

MAX_PER_PAGE = 200
LIKE_ESCAPE = "\\"


def _like_pattern(text):
    """把用户输入转成安全的 LIKE 模式。"""
    escaped = (
        text.replace(LIKE_ESCAPE, LIKE_ESCAPE * 2)
        .replace("%", LIKE_ESCAPE + "%")
        .replace("_", LIKE_ESCAPE + "_")
    )
    return f"%{escaped}%"


def search_articles(query, source_id=None, unread_only=False, page=1, per_page=50):
    """按标题/摘要/正文搜索，支持来源与未读过滤、分页。"""
    q = Article.query

    if query and query.strip():
        pattern = _like_pattern(query.strip())
        q = q.filter(
            or_(
                Article.title.like(pattern, escape=LIKE_ESCAPE),
                Article.summary.like(pattern, escape=LIKE_ESCAPE),
                Article.content.like(pattern, escape=LIKE_ESCAPE),
            )
        )

    if source_id:
        q = q.filter(Article.source_id == source_id)

    if unread_only:
        # read 为 NULL（历史数据或外部写入）并不是「已读」，
        # 只判 is_(False) 会让这些文章从「只看未读」里凭空消失。
        q = q.filter(or_(Article.read.is_(False), Article.read.is_(None)))

    try:
        page = max(1, int(page or 1))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = min(MAX_PER_PAGE, max(1, int(per_page or 50)))
    except (TypeError, ValueError):
        per_page = 50

    return (
        q.order_by(Article.published.desc(), Article.id.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )
