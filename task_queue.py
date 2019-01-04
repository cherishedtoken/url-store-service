from celery import Celery
from config import db
import datetime
from models import FetchedUrl
import requests
import unicodedata

queue = Celery('task_queue', backend='rpc://', broker='amqp://localhost')

@queue.task
def fetch_url(url):
    try:
        res = requests.get(url)
        res = normalize_unicode(res)
        # If we have an older row with the same URL, update that row.
        # Otherwise insert a new row.
        prev_row = FetchedUrl.query.filter_by(url = url).first()
        if prev_row:
            prev_row.added_at = datetime.datetime.now()
            prev_row.data = res
        else:
            url_obj = FetchedUrl(url = url, data = res)
            db.session.add(url_obj)
        db.session.commit()
    except requests.exceptions.ConnectionError as err:
        # If you pass a URL to a nonexistent website, this exception will
        # eventually get thrown. Not much we can do about it, so print
        # the error and try to move on.
        print err

def normalize_unicode(response):
    # The Postgres driver can throw errors if it gets weird character data.
    # For example, '\xa0', the Latin1 encoding for a nonbreaking space, which
    # is on google.com, will cause problems. Normalize the text to fix this.
    return unicodedata.normalize("NFKD", response.text)
    
