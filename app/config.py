"""配置加载：YAML → Flask 配置。

修复要点：
1. 原来 `_load_config` 把配置写在**实例属性**上，而 `get()` / `to_flask_config()`
   读的是**类属性** `cls._config`（永远是 None），于是：
     - `ConfigLoader.get()` 恒返回默认值；
     - `to_flask_config()` 在 `'server' in cls._config` 处抛
       `TypeError: argument of type 'NoneType' is not iterable`，应用直接起不来。
   现在统一用类属性承载配置，并支持按路径重新加载。
2. 相对 SQLite 路径锚定到项目根目录，避免 Flask-SQLAlchemy 3.x 把它塞进
   instance 目录（容器里会导致数据不在挂载卷上）。
"""
import logging
import os
import re
import yaml

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.yaml")

_SQLITE_PREFIX = "sqlite:///"
_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:[\\/]")


def normalize_sqlite_uri(uri, base_dir=None):
    """把相对 SQLite 路径锚定到 base_dir（默认项目根目录），并创建所在目录。

    - `sqlite:///data/rss.db`   → `<base_dir>/data/rss.db`（相对路径被锚定）
    - `sqlite:////app/data/x.db` → 原样返回（已经是绝对路径）
    - `sqlite:///C:/x/rss.db`    → 原样返回（Windows 绝对路径）
    - `sqlite:///:memory:`       → 原样返回
    - 非 sqlite URL              → 原样返回
    """
    if not uri or not isinstance(uri, str):
        return uri
    if not uri.startswith(_SQLITE_PREFIX):
        return uri

    path = uri[len(_SQLITE_PREFIX):]
    if (not path) or path == ":memory:" or path.startswith("/") or _WINDOWS_DRIVE.match(path):
        return uri

    base = base_dir or PROJECT_ROOT
    full_path = os.path.normpath(os.path.join(base, path))
    directory = os.path.dirname(full_path)
    if directory:
        try:
            os.makedirs(directory, exist_ok=True)
        except OSError as exc:  # 只读文件系统等：交给 SQLAlchemy 报更明确的错
            logger.warning("无法创建数据库目录 %s: %s", directory, exc)
    return _SQLITE_PREFIX + full_path.replace("\\", "/")


class ConfigLoader:
    """进程内单例；配置存放在类属性上，随配置路径变化而重新加载。"""

    _instance = None
    _config = None
    _config_path = None

    def __new__(cls, config_path=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        cls._instance._load_config(config_path or DEFAULT_CONFIG_PATH)
        return cls._instance

    def _load_config(self, config_path):
        cls = type(self)
        abs_path = os.path.abspath(config_path)
        if cls._config is not None and cls._config_path == abs_path:
            return  # 同一份配置无需重复读盘
        with open(abs_path, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
        if not isinstance(data, dict):
            raise ValueError(f"配置文件格式错误（顶层必须是映射）: {abs_path}")
        cls._config = data
        cls._config_path = abs_path

    # -- 读取 ------------------------------------------------------------- #
    @classmethod
    def _ensure_loaded(cls):
        if cls._config is None:
            cls(DEFAULT_CONFIG_PATH)
        return cls._config

    @classmethod
    def get(cls, key, default=None):
        """按 `a.b.c` 取值，缺失或类型不符时返回 default。"""
        value = cls._ensure_loaded()
        for part in str(key).split("."):
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        return default if value is None else value

    @classmethod
    def to_flask_config(cls):
        """把 YAML 映射成 Flask 风格的大写配置键。"""
        raw = cls._ensure_loaded()
        flask_config = {}

        def section(name):
            value = raw.get(name)
            return value if isinstance(value, dict) else {}

        server = section("server")
        flask_config["SERVER_HOST"] = server.get("host", "0.0.0.0")
        flask_config["SERVER_PORT"] = int(server.get("port", 5000))
        flask_config["SERVER_DEBUG"] = bool(server.get("debug", False))

        database = section("database")
        flask_config["SQLALCHEMY_DATABASE_URI"] = database.get("url") or "sqlite:///data/rss.db"

        sched = section("scheduler")
        flask_config["SCHEDULER_ENABLED"] = bool(sched.get("enabled", True))
        flask_config["SCHEDULER_DEFAULT_INTERVAL"] = int(sched.get("default_interval", 30))

        app_section = section("app")
        flask_config["APP_NAME"] = app_section.get("name", "RSS Aggregator")
        flask_config["APP_LANGUAGE"] = app_section.get("language", "en")
        flask_config["APP_TIMEZONE"] = app_section.get("timezone", "UTC")
        flask_config["SECRET_KEY"] = app_section.get("secret_key")

        email = section("notifications").get("email")
        email = email if isinstance(email, dict) else {}
        flask_config["EMAIL_ENABLED"] = bool(email.get("enabled", False))
        flask_config["EMAIL_SMTP_SERVER"] = email.get("smtp_server", "")
        flask_config["EMAIL_SMTP_PORT"] = int(email.get("smtp_port", 587))
        flask_config["EMAIL_USERNAME"] = email.get("username", "")
        flask_config["EMAIL_PASSWORD"] = email.get("password", "")
        flask_config["EMAIL_FROM"] = email.get("from_addr", "")
        flask_config["EMAIL_TO"] = email.get("to_addr", "")
        flask_config["EMAIL_USE_TLS"] = bool(email.get("use_tls", True))

        security = section("security")
        flask_config["SECURITY_ALLOW_PRIVATE_NETWORKS"] = bool(
            security.get("allow_private_networks", False)
        )
        flask_config["SECURITY_CSRF_ORIGIN_CHECK"] = bool(security.get("csrf_origin_check", True))

        fulltext = section("fulltext")
        flask_config["FULLTEXT_ENABLED"] = bool(fulltext.get("enabled", True))
        flask_config["FULLTEXT_MAX_PER_FETCH"] = int(fulltext.get("max_per_fetch", 5))
        flask_config["FULLTEXT_TIMEOUT"] = int(fulltext.get("timeout", 10))

        fetch = section("fetch")
        flask_config["FETCH_RETRIES"] = max(1, int(fetch.get("retries", 3)))
        flask_config["FETCH_TIMEOUT"] = int(fetch.get("timeout", 15))
        flask_config["FETCH_MAX_ENTRIES"] = int(fetch.get("max_entries", 50))
        flask_config["FETCH_USER_AGENT"] = fetch.get("user_agent", "RSSAggregator/1.0 (+feed reader)")

        log_section = section("logging")
        flask_config["LOG_LEVEL"] = str(log_section.get("level", "INFO")).upper()
        flask_config["LOG_FILE"] = log_section.get("file", "rss_aggregator.log")

        return flask_config
