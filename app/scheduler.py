from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app import db, scheduler
from app.models import Source
from app.fetcher import fetch_source

def schedule_source(source):
    interval = source.interval or 30
    job_id = f"source_{source.id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    scheduler.add_job(
        fetch_source,
        trigger=IntervalTrigger(minutes=interval),
        id=job_id,
        args=[source.id],
        replace_existing=True
    )

def schedule_all():
    with scheduler.app.app_context():
        sources = Source.query.all()
        for source in sources:
            schedule_source(source)

def init_scheduler(app):
    scheduler.app = app
    scheduler.start()
    with app.app_context():
        schedule_all()