import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app import db, scheduler
from app.models import Source
from app.fetcher import fetch_source

logger = logging.getLogger(__name__)

def schedule_source(source, notify=True):
    interval = source.interval or 30
    job_id = f"source_{source.id}"
    if scheduler.get_job(job_id):
        scheduler.remove_job(job_id)
    scheduler.add_job(
        fetch_source,
        trigger=IntervalTrigger(minutes=interval),
        id=job_id,
        args=[source.id, notify],
        replace_existing=True
    )
    logger.info(f"Scheduled source {source.id} every {interval} min, notify={notify}")

def schedule_all(notify=True):
    with scheduler.app.app_context():
        sources = Source.query.all()
        for source in sources:
            schedule_source(source, notify)

def init_scheduler(app):
    scheduler.app = app
    if not scheduler.running:
        scheduler.start()
    with app.app_context():
        schedule_all()
