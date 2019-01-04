# The App

## Description

This is a small app that provides an API that fetches and stores webpages. If a webpage has been stored within the last hour, a request to re-fetch the same page will fail. The fetching of webpages happens asynchronously after you make a request to the /fetch endpoint, and you can check on the status of the request by using the /fetch/status endpoint.


## Installation 

You will need to install Python2, RabbitMQ, and Postgres. Postgres can be installed with `brew install postgres` and RabbitMQ can be installed with `brew install rabbitmq`.

`cd` into the source directory and run `virtualenv --python=/usr/bin/python venv` to create a new virtual environment (I'm assuming here that /usr/bin/python is pointing to a version of python2 - if it's not doing so by default, please use the right path to the Python2 binary in the command). Once you have created the virtual environment, activate it with `. venv/bin/activate`, and then install the requirements for the application using `pip install -r requirements.txt`. Log into Postgres using psql and run `create database urls;` from the PSQL shell. The table in the database needed by the app can be created by running models.py directly (`python models.py`).

Once the requirements have been installed, start Celery with `celery -A task_queue worker --loglevel=info`. You can then finally start the main app with `FLASK_APP=main.py flask run`. 

The API:

`GET /fetch`

Takes a `url` parameter which should have a string argument. It then checks to see if the URL supplied matches any of the websites whose data has previously been fetched by the API, and if so, returns the content of that website. If the URL supplied does not match a URL the API has previously fetched data for, an unsuccessful response is returned.

Example call:

`curl -X GET http://localhost:5000/fetch -d 'url=https://citibank.com'`

Example successful response:

`{"data": "<!DOCTYPE html>\r\n \r\n\r\n<html xmlns=\"http://www.w3.org/1999/xhtml\" xmlns:tcdl=\"http://www.tridion.com/ContentDelivery/5.3/TCDL\"  class=\"no-js\" lang=\"en\">\r\n\r\n\r\n\r\n\r\n<head>\r\n    \r\n    ...."}`

Example unsuccessful response:

`{"response": "Resource not found"}`

`POST /fetch`

Takes a `url` parameter which should have a string argument. It then checks to see if any requests for the URL were made within the last hour. If so, an unsuccessful response is returned. Otherwise, a request for the URL is queued with a Celery worker, and a reference to the job ID is returned. The job ID can be passed as an argument to the /fetch/status API to check on the status of the request.

Example call:

`curl -X POST http://localhost:5000/fetch -d 'url=monkey.com'`

Example successful response:

`{"ID": "ffd217e7-3023-446a-8e4b-49a0017f2b87"}`

Example unsuccessful response:

`{"response": "Request made less than an hour ago"}`

`GET /fetch/status/<request_id>`

The request ID should be included in the endpoint. Request IDs are returned by the /fetch endpoint's POST method when a URL request is successfully queued. If a request ID that does not exist in the database is supplied as an argument, an error response with a 404 HTTP status is returned. If the ID is found, the status of the request is returned.

Example call:

`curl -X GET http://localhost:5000/fetch/status/ffd217e7-3023-446a-8e4b-49a0017f2b87`

Example unsuccessful response:

`{"Status": "ID not found", "ID": "foo"}`

Example successful responses:

`{"Status": "Pending", "ID": "ffd217e7-3023-446a-8e4b-49a0017f2b87"}`

`{"Status": "Complete", "ID": "ffd217e7-3023-446a-8e4b-49a0017f2b87"}`

