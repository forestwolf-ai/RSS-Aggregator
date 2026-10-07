"""应用入口：建表/补索引 → 启动调度器 → 启动 Web 服务。

修复要点：
1. 引导逻辑放在模块层，不再只写在 `if __name__ == '__main__'` 里。
   原来用 gunicorn/uwsgi（`main:app`）或 `flask run` 启动时不会执行 db.create_all()，
   第一个请求就报「no such table」。
2. 调度器启动由 init_scheduler 统一负责（幂等、尊重配置、避开调试重载器父进程），
   避免重载器下起两个调度器重复抓取。
"""
from app import create_app
from app.scheduler import init_scheduler
from app.schema import ensure_schema

app = create_app()


def bootstrap():
    """幂等引导：建表 + 补索引 + 启动调度器。"""
    with app.app_context():
        ensure_schema(app)
    init_scheduler(app)
    return app


bootstrap()

if __name__ == "__main__":
    app.run(
        host=app.config.get("SERVER_HOST", "0.0.0.0"),
        port=int(app.config.get("SERVER_PORT", 5000)),
        debug=bool(app.config.get("SERVER_DEBUG", False)),
    )
