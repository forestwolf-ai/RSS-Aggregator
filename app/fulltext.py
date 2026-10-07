"""网页正文抽取。

修复要点：
1. 抽取目标来自 feed 里的文章链接，必须做 SSRF 校验（与抓取同一套策略）。
2. 超时与开关可配置（fulltext.timeout），不再硬编码 10s。
3. lxml 缺失时回退到标准库解析器，而不是让整条链路报错。
"""
import logging

import requests
from bs4 import BeautifulSoup, FeatureNotFound
from flask import current_app, has_app_context

from app.urlsafety import is_safe_url

logger = logging.getLogger(__name__)

MAX_TEXT_CHARS = 5000
STRIP_TAGS = ("script", "style", "nav", "footer", "header", "aside")


def _config(key, default):
    if has_app_context():
        return current_app.config.get(key, default)
    return default


def extract_full_text(url, timeout=None, allow_private=None):
    """尝试从网页提取正文，失败一律返回空字符串（绝不抛异常）。"""
    if timeout is None:
        timeout = int(_config("FULLTEXT_TIMEOUT", 10))
    if allow_private is None:
        allow_private = bool(_config("SECURITY_ALLOW_PRIVATE_NETWORKS", False))

    if not is_safe_url(url, allow_private=allow_private):
        logger.warning("跳过被安全策略拒绝的正文抽取地址: %s", url)
        return ""

    headers = {"User-Agent": _config("FETCH_USER_AGENT", "RSSAggregator/1.0")}
    try:
        response = requests.get(url, timeout=timeout, headers=headers)
        if response.status_code != 200:
            return ""
        try:
            soup = BeautifulSoup(response.text, "lxml")
        except FeatureNotFound:  # lxml 未安装时退回标准库解析器
            soup = BeautifulSoup(response.text, "html.parser")

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
    except Exception as exc:  # noqa: BLE001 - 抽取失败不应影响抓取
        logger.warning("正文抽取失败 %s: %s", url, exc)
        return ""
