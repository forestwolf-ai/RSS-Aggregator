from app import create_app, db
from app.scheduler import init_scheduler

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    init_scheduler(app)
    app.run(host=app.config['SERVER_HOST'], port=app.config['SERVER_PORT'], debug=app.config['SERVER_DEBUG'])