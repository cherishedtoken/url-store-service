from config import app
import datetime
from flask_restful import Resource, Api
from models import FetchedUrl
from task_queue import fetch_url

api = Api(app)
url_requests = []

# Create a service containing a queue of tasks with workers whose job is to fetch data from a URL and store the results.
# The service should expose REST or GraphQL API endpoints for adding a new job via URL, checking the status of an existing job, and retrieving the results of a completed job.
# If a URL has been submitted within the last hour, do not fetch the data again.

# Utility subroutines
def check_for_protocol(url):
    if not url.startswith('http'):
        # Requests requires a protocol to be included
        url = 'http://' + url
    return url

def request_is_from_last_hour(req):
    one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    return req.added_at >= one_hour_ago

def get_previous_requests(url):
    return FetchedUrl.query.filter_by(url = url).first()

class FetchUrl(Resource):
    def get(self, url):
        url = check_for_protocol(url)
        # Retrieve results from a previous job that used a given URL.
        return get_previous_requests(url)

    def post(self, url):
        url = check_for_protocol(url)
        # Only fetch data from this URL if we haven't yet done so within the
        # last hour.
        previous_request = get_previous_requests(url)
        if previous_request and request_is_from_last_hour(previous_request):
            print("found a request")
            return
        result = fetch_url.delay(url)
        url_requests.append(result)
        return result.id

class RequestStatus(Resource):
    def get(self, request_id):
        if not any([request.id == request_id for request in url_requests]):
            return {"ID" : request_id, "Status" : "ID not found" }, 404
        for req in url_requests:
            if req.id == request_id:
                status = req.ready()
                return_status = "Complete" if True else "Pending"
                return {"ID" : request_id, "Status": return_status }, 200
        

api.add_resource(FetchUrl, '/fetch_url/<url>')
api.add_resource(RequestStatus, '/fetch_url/status/<request_id>')
