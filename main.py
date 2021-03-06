from config import app
import datetime
from flask_restful import reqparse, Resource, Api
from models import FetchedUrl
from task_queue import fetch_url

api = Api(app)
url_requests = []

parser = reqparse.RequestParser()
parser.add_argument('url')

# Create a service containing a queue of tasks with workers whose job is to fetch
# data from a URL and store the results.
# The service should expose REST or GraphQL API endpoints for adding a new job via
# URL, checking the status of an existing job, and retrieving the results of a
# completed job.
# If a URL has been submitted within the last hour, do not fetch the data again.

# Utility subroutines
def check_for_protocol(url):
    if not url.startswith('http'):
        # Requests requires a protocol to be included. Add it if it's missing
        url = 'http://' + url
    return url

def request_is_from_last_hour(req):
    one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    return req.added_at >= one_hour_ago

def get_previous_request(url):
    # Check if a previous request for a given URL exists in the database.
    return FetchedUrl.query.filter_by(url = url).first()

class FetchUrl(Resource):
    def get(self):
        args = parser.parse_args()
        url = args['url']
        url = check_for_protocol(url)
        prev = get_previous_request(url)
        if prev:
            return {"data" : prev.data}, 200
        else:
            return {"response" : "Resource not found"}, 404

    def post(self):
        args = parser.parse_args()
        url = args['url']
        url = check_for_protocol(url)
        # Only fetch data from this URL if we haven't yet done so within the
        # last hour.
        previous_request = get_previous_request(url)
        if previous_request and request_is_from_last_hour(previous_request):
            return {"response" : "Request made less than an hour ago"}, 400
        result = fetch_url.delay(url)
        url_requests.append(result)
        return {"ID": result.id}, 200

class RequestStatus(Resource):
    def get(self, request_id):
        if not any([request.id == request_id for request in url_requests]):
            return {"ID" : request_id, "Status" : "ID not found" }, 404
        for req in url_requests:
            if req.id == request_id:
                status = req.ready()
                return_status = "Complete" if True else "Pending"
                return {"ID" : request_id, "Status" : return_status }, 200

api.add_resource(FetchUrl, '/fetch')
api.add_resource(RequestStatus, '/fetch/status/<request_id>')
