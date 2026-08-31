import yaml
import os

class ConfigLoader:
    _instance = None
    _config = None

    def __new__(cls, config_path="config.yaml"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config(config_path)
        return cls._instance

    def _load_config(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)

    @classmethod
    def get(cls, key, default=None):
        if cls._config is None:
            cls._instance = cls()
        keys = key.split('.')
        value = cls._config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    @classmethod
    def to_flask_config(cls):
        """将配置转换为 Flask 风格的大写键"""
        flask_config = {}
        if cls._config is None:
            cls._instance = cls()
        # 手动映射常用键
        if 'server' in cls._config:
            flask_config['SERVER_HOST'] = cls._config['server'].get('host', '0.0.0.0')
            flask_config['SERVER_PORT'] = cls._config['server'].get('port', 5000)
            flask_config['SERVER_DEBUG'] = cls._config['server'].get('debug', False)
        if 'database' in cls._config:
            flask_config['SQLALCHEMY_DATABASE_URI'] = cls._config['database'].get('url', 'sqlite:///rss.db')
        if 'scheduler' in cls._config:
            flask_config['SCHEDULER_ENABLED'] = cls._config['scheduler'].get('enabled', True)
            flask_config['SCHEDULER_DEFAULT_INTERVAL'] = cls._config['scheduler'].get('default_interval', 30)
        if 'app' in cls._config:
            flask_config['APP_NAME'] = cls._config['app'].get('name', 'RSS Aggregator')
            flask_config['APP_LANGUAGE'] = cls._config['app'].get('language', 'en')
            flask_config['APP_TIMEZONE'] = cls._config['app'].get('timezone', 'UTC')
        # 邮件配置
        if 'notifications' in cls._config and 'email' in cls._config['notifications']:
            flask_config['EMAIL_ENABLED'] = cls._config['notifications']['email'].get('enabled', False)
            flask_config['EMAIL_SMTP_SERVER'] = cls._config['notifications']['email'].get('smtp_server', '')
            flask_config['EMAIL_SMTP_PORT'] = cls._config['notifications']['email'].get('smtp_port', 587)
            flask_config['EMAIL_USERNAME'] = cls._config['notifications']['email'].get('username', '')
            flask_config['EMAIL_PASSWORD'] = cls._config['notifications']['email'].get('password', '')
            flask_config['EMAIL_FROM'] = cls._config['notifications']['email'].get('from_addr', '')
            flask_config['EMAIL_TO'] = cls._config['notifications']['email'].get('to_addr', '')
        return flask_config
