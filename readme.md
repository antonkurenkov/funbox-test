# flask-redis-api
## url accounter

This is a [Flask][flask] application for accounting and storing domain urls in [Redis][redis] database.

## Description

The app provides API methods for inserting an array of links into the database and getting back the domains 
collected within some determined period.

- POST method is available via `/visited_links` passing the array of links as data type of `application/json`
- GET method is available via `/visited_domains` passing the upper and lower timestamp thresholds as `from` and `to`
args

## Setup

The app is written in Python 3.7.4, so you need a proper version be installed.
You also need `flask` lib and `redis` lib for python to be installed previously.

For connecting to the databade you have to set up and run Redis database server.
Detailed description can be found [here] and [also here].

## Run

- Run Redis server with something like `redis-server /etc/redis/6379.conf`
- Run `api.py` for app server to start.
#
'Out of the box' app be accessed on `127.0.0.1:5000`.

## Usage

For example we use `curl`: 
- `curl -d '{"links":["https://ya.ru/123"]}' -H "Content-Type: application/json" -X POST '127.0.0.1:5000/visited_links'`

- `curl -d '{"links":["ya.ru?q=123"]}' -H "Content-Type: application/json" -X POST '127.0.0.1:5000/visited_links'`
#
The app returns json `{"status": "ok"}` if data array passed to `"links"` value placed into the database correctly, 
otherwise the error massage will appear in the `"status"` value. 

If we run the following command passing the `from` and `to` values as upper and lower time thresholds, we will get all 
the domains placed into the database within selected period. For example executed both our previous commands on 
2020-02-09 1:58pm (UTC), so the following command
- `curl -X GET 'http://127.0.0.1:5000/visited_domains?from=1581256643&to=1581256771'`

returns `{"domains": ["ya.ru"], "status": "ok"}` because it was the only one domain passed to the app 
during this period of time (of course, there were two requests, but both of them have the same domain `ya.ru`).

## Testing

Automated testing script provided in `testing.py` based on python `unittest` lib. 

[flask]: https://www.palletsprojects.com/p/flask/
[redis]: https://https://redis.io/
[here]: https://redis.io/topics/quickstart
[also here]: https://realpython.com/python-redis/