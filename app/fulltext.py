import logging

from bs4 import BeautifulSoup, FeatureNotFound
from flask import current_app, has_app_context

from app.urlsafety import UnsafeURLError, safe_get

logger = logging.getLogger(__name__)

MAX_TEXT_CHARS = 5000
DEFAULT_MAX_BYTES = 2 * 1024 * 1024
STRIP_TAGS = ("script", "style", "nav", "footer", "header", "aside")


def _config(key, default):
    if has_app_context():
        return current_app.config.get(key, default)
    return default


def extract_full_text(url, timeout=None, allow_private=None, max_bytes=None):
    """尝试从网页提取正文，失败一律返回空字符串（绝不抛异常）。"""
    if timeout is None:
        timeout = int(_config("FULLTEXT_TIMEOUT", 10))
    if allow_private is None:
        allow_private = bool(_config("SECURITY_ALLOW_PRIVATE_NETWORKS", False))
    if max_bytes is None:
        max_bytes = int(_config("FULLTEXT_MAX_BYTES", DEFAULT_MAX_BYTES))

    headers = {"User-Agent": _config("FETCH_USER_AGENT", "RSSAggregator/1.0")}
    try:
        result = safe_get(
            url,
            timeout=timeout,
            headers=headers,
            max_bytes=max_bytes,
            allow_private=allow_private,
        )
        if result.status_code != 200:
            return ""
        try:
            soup = BeautifulSoup(result.content, "lxml")
        except FeatureNotFound:  # lxml 未安装时退回标准库解析器
            soup = BeautifulSoup(result.content, "html.parser")

        container = (
            soup.find("article")
            or soup.find("div", class_="content")
            or soup.find("div", class_="post")
            or soup.body
        )
        if container is None:
            return ""
        for tag in container(STRIP_TAGS):
            tag.decompose()
        return container.get_text(separator="\n", strip=True)[:MAX_TEXT_CHARS]
    except UnsafeURLError as exc:
        logger.warning("跳过被安全策略拒绝的正文抽取地址: %s", exc)
        return ""
    except Exception as exc:  # noqa: BLE001 - 抽取失败不应影响抓取
        logger.warning("正文抽取失败 %s: %s", url, exc)
        return ""
