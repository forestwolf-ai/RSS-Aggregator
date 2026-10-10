import logging
from urllib.parse import urlsplit

from flask import abort, current_app, request

logger = logging.getLogger(__name__)

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


def _origin_of(value):
    if not value:
        return None
    try:
        return urlsplit(value).netloc.lower() or None
    except ValueError:
        return None


def check_csrf_origin():
    """POST/PUT/PATCH/DELETE 的来源校验；作为 before_request 钩子注册。"""
    if request.method in SAFE_METHODS:
        return None
    if not current_app.config.get("SECURITY_CSRF_ORIGIN_CHECK", True):
        return None

    origin = _origin_of(request.headers.get("Origin")) or _origin_of(request.headers.get("Referer"))
    if origin is None:
        # 非浏览器客户端（curl / 脚本）不带这两个头，交给鉴权层处理
        return None

    if origin != request.host.lower():
        logger.warning("拒绝跨站请求：origin=%s host=%s path=%s", origin, request.host, request.path)
        abort(403)
    return None
