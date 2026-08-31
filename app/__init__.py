import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler

db = SQLAlchemy()
scheduler = BackgroundScheduler()

def create_app(config_path="config.yaml"):
    app = Flask(__name__)

    # 加载配置
    from app.config import ConfigLoader
    ConfigLoader(config_path)  # 初始化单例
    app.config.update(ConfigLoader.to_flask_config())

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('rss_aggregator.log'),
            logging.StreamHandler()
        ]
    )

    # 初始化数据库
    db.init_app(app)

    # 注册蓝图
    from app.web.routes import web_bp
    app.register_blueprint(web_bp)

    # 启动调度器
    if app.config.get('SCHEDULER_ENABLED', True):
        if not scheduler.running:
            scheduler.start()
        # 设置 app 引用供调度器使用
        scheduler.app = app

    return app
