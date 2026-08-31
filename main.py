from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    from app.scheduler import init_scheduler
    init_scheduler(app)
    app.run(
        host=app.config.get('SERVER_HOST', '0.0.0.0'),
        port=app.config.get('SERVER_PORT', 5000),
        debug=app.config.get('SERVER_DEBUG', False)
    )
