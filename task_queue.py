from celery import Celery
from config import db
import datetime
from models import FetchedUrl
import requests

queue = Celery('task_queue', backend='rpc://', broker='amqp://localhost')

@queue.task
def fetch_url(url):
    res = requests.get(url)
    # If we have an older row with the same URL, update that row.
    # Otherwise insert a new row.
    prev_row = FetchedUrl.query.filter_by(url = url).first()
    if prev_row:
        prev_row.added_at = datetime.datetime.now()
        prev_row.data = res.content
    else:
        url_obj = FetchedUrl(url = url, data = res.content)
        db.session.add(url_obj)
    db.session.commit()
