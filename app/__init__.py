from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler

db = SQLAlchemy()
scheduler = BackgroundScheduler()

def create_app(config_path="config.yaml"):
    app = Flask(__name__)
    app.config.from_file(config_path, load=__import__("yaml").safe_load)
    db.init_app(app)
    
    from app.web.routes import web_bp
    app.register_blueprint(web_bp)
    
    # 启动调度器
    if app.config.get("SCHEDULER_ENABLED", True):
        scheduler.start()
    
    return app