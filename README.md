# Python, Flask and Postgres

This is a bootstrap of a common Python3-based Web API dev stack and some example API. An update was
made in part using the code from [flask-on-docker](https://github.com/testdrivenio/flask-on-docker), which is another nice example!

Here are the assumptions and tools used.

* [Docker](https://docs.docker.com/) containers are used for everything with [docker-compose](https://docs.docker.com/compose/compose-file/) to simplify orchestration
* [Flask](https://flask.palletsprojects.com/en/2.0.x/) with the latest [Python 3](https://www.python.org/) is used for the web API 
* [Postgres](https://www.postgresql.org/) provides a relational database for everything
* [gunicorn](https://flask.palletsprojects.com/en/2.0.x/deploying/wsgi-standalone/#gunicorn)/[nginx](http://nginx.org/) for prod-style deployment
* Plain SQL datamodel (No ORM! -- more in the schema description)
* Follow [functional style Python](https://docs.python.org/3/howto/functional.html) coding and keeping the codebase trivial to debug. Functions are pure, easily debugged and any bug is isolated to very few lines of code -- simple, low maintenance. If you haven't watched [Simple Made Easy](https://www.youtube.com/watch?v=oytL881p-nQ), please watch that great talk by Rich Hickey. The style here is derived by applying those concepts. 

Extending the example to have a ReactJS for a single page app frontend will come next.
Along with that I'll add in using selenium/web-driver for end-to-end tests along with 
code coverage exports to the dev deployment.

## Running the Application

The entire repository can be run with normal `docker-compose` commands.

```
# run dev mode, which does real-time reloads in Flask
docker-compose up -d

# build and restart for latest images
docker-compose build
docker-compose restart

# tear down all resources related to the app (include postgres volumne for data)
docker-compose down
docker volume prune
```

Production mode can be done with the same commands above but by using `-f docker-compose.prod.yml`.
For example, `docker-compose -f docker-compose.prod.yml up -d` runs in production mode.

In development mode, there are just two services running: Flask using Python 3.9.5 and
Postgres. You can acess the dev server by visiting [http://localhost:5000/sites](http://localhost:5000/sites), etc.

In production mode, there are three services: nginx to serve static files and proxy to Flask,
`gunicorn` running Flask at scale, and Postgres as the database. You can acess the dev server by visiting [http://localhost:1337/sites](http://localhost:1337/sites), etc.

See [`docker-compose.yml`](./docker-compose.yml) for the dev config and [`docker-compose.prod.yml`](./docker-compose.prod.yml) for the production config. These files include all the extra mapped local directories that aren't strictly used here; however, generally helpful. For example, exposing static content via nginx (Flask is slow!) and have a space to stash uploaded media files.

## Example Data

Example data is provided in the `postgres_scripts` directory. You will find the main 
schema as well as a mock data script. These scripts are mounted to the postgres image
under `/var/postgres_scripts`.

Run the scripts as follows:

```
# drop old data and setup all tables
docker-compose exec db psql -U mock_dev_user -f /var/postgres_scripts/create_tables.sql postgres_dev

# populate with mock data
docker-compose exec db psql -U mock_dev_user -f /var/postgres_scripts/mock_data.sql postgres_dev
```

After data is populated, you can ad-hoc query the Postgres container to interact with
the relational database. For example, the SQL statements you will find the API use in 
`services/web/database/site.py` (and similar) can be run by hand. Some examples below.

```
# lauch psql in interactive mode
docker-compose exec  db psql -U mock_dev_user postgres_dev

# show the sites
postgres_dev=# SELECT * FROM site;
 id |  name  |  contact   |          address           | state_or_region | country | postcode_or_zip 
----+--------+------------+----------------------------+-----------------+---------+-----------------
  1 | Site 1 | John Smith | 123 Muffin Lane, Ann Arbor | MI              | USA     | 48103
  2 | Site 2 |            |                            |                 |         | 
  3 | Site 3 |            |                            |                 |         | 
(3 rows)

postgres_dev=# SELECT * FROM freezer;
 id | name | site_id 
----+------+---------
  1 | -20C |       1
  2 | -40C |       1
(2 rows)

postgres_dev=# SELECT * FROM computer;
 id |    name    | mac | site_id 
----+------------+-----+---------
  1 | Computer 1 |     |       1
  2 | Computer 2 |     |       1
(2 rows)

postgres_dev=# SELECT * FROM container;
 id | uuid | description | freezer_id 
----+------+-------------+------------
(0 rows)


# can also make the views used to show all "instruments"
postgres_dev=# (SELECT s.id, s.name as site_name, c.id AS computer_id, NULL as freezer_id, c.name AS instrument_name FROM site AS s FULL JOIN computer AS c ON s.id = c.site_id WHERE c.id IS NOT NULL ORDER BY s.id, c.id ASC)
postgres_dev-# UNION
postgres_dev-# (SELECT s.id, s.name as site_name, NULL AS computer_id, f.id AS freezer_id, f.name AS freezer_name FROM site AS s FULL JOIN freezer AS f ON s.id = f.site_id WHERE f.id IS NOT NULL ORDER BY s.id, f.id ASC);
 id | site_name | computer_id | freezer_id | instrument_name 
----+-----------+-------------+------------+-----------------
  1 | Site 1    |           1 |            | Computer 1
  1 | Site 1    |             |          2 | -40C
  1 | Site 1    |           2 |            | Computer 2
  1 | Site 1    |             |          1 | -20C
(4 rows)
```

## Database Schema

The goal of the schema is to model a set of labs that may have one or more sites. Each site having a name and address (handling addresses is non-trivial!). Sites can have named instrumentation that must be tracked. Instrument types are either computers or freezers. Computers have both a name and a unique MAC address. Freezers have both a name and containers. Each container has a UUID and description.

Here are main the design goals:
1. Keep both the Python and SQL simple and efficient -- not intertwined
2. Keep all SQL and database logic abstracted by the `project/database/...` modules' Python API
3. Keep the web API logic abstracted by the `project/api/...` modules' Python API

The interesting domain issues considered are as follows:
1. Addresses are non-trivial to model. There may be US and non-US addresses. Names are not simply first, last with a fixed max size -- there are many exceptions to that. Addresses are also only split to common international parts: address, state_or_region, country and postcode_or_zip. All are treated as `text` type in Postgres since performance is not impacted by this and it is most flexible. Extra validation of addresses is presumed to best be done at the level of Python logic and/or third party tools.
2. Instruments share a name but otherwise can have different fields. We need to be able to query and reason about all instrument types; however, still efficiently represent and update the raw data in the database.

Appyling the design goals to the domain issues resulted in the following two strategies.

This lead to purposely not using an Object Relational Mapper (ORM) because it tries to abstract a critical part of keeping the Python and SQL simple and efficient. ORMs are not an excuse to avoid learning SQL and how Postgres works. ORMs also aren't the desired application-specific interface for working with the database. The strategy here is to use pure Postgres-specific SQL to load schema (see [`./postgres_scripts/create_tables.sql`](./postgres_scripts/create_tables.sql) and [`mock_data.sql`](./postgres_scripts/mock_data.sql)). The exact Python API needed to support the web API is exposed and nothing more. e.g. see [`./project/database/sites.py`](services/web/project/database/site.py). If the dabase backing needs to be updated, even to switch to an ORM, it could be done and nothing outside of this module will need to change.

A second strategy was to not force the database to model the polymorphic representation of instruments, namely freezer vs computer. Yes, a field `name` is shared; however, it is not a requirement to have [extreme normalization](https://en.wikipedia.org/wiki/Database_normalization). In practice, there will be few types of instruments and each can be represented by a simple table that is very fast to edit, read and even provide a history table to audit changes. The intuitive view of showing all instruments is easily done with a SQL view (see [`project/database/instruments.py`](./services/web/project/database/instruments.py) -- true too of any view the Web UI might need. Generally, the intention is to give the Web UI as few as possible endpoints that return exactly what the view needs. Not API that could do anything and force logic in the JavaScript. JavaScript can't easily enforce atomic operations, efficient joins and queries like the Python code that uses the database.

A query to show containers wasn't included in this first pass. They are modeled in Postgres using appropriate types.

## RESTful API

A general RESTful theme was followed by endpoints. This is meant to mean the following:
* Endpoints have a simple URI and accept or return JSON and support pagination
   * e.g. GET `/site/1` returns the site with ID 1 as `{'id': 1, 'name': 'Site 1', .... }`
   * e.g. GET `/sites` returns a list of all sites
   * e.g. GET `/sites/0/10` returns the first 10 sites, `/sites/10/10` will show the next 10 sites, etc. 
* HTTP methods map to CRUD actions (create and update are combined to one UPSERT via POST)
   * e.g. GET `/site/1` to show a site by its ID
   * e.g. POST `/site/1` with a JSON payload to update or lazy-create the database entry for that site
   * e.g. DELETE `/site/1` to remove a site from the database by the ID
* GET endpoints are idempotent
* POST and DELETE are atomic operations
* HTTP response codes are used to signify if success (200) occurred or the URI was invalid (400) or missing (404) or if internal errors are preventing work (500)

No specific schema enforcing tool is used with this example. Adding extra Python validation would be the mechanism desired to layer that on in the `project/api/...` modules.

No extra caching is done to optimize GET requests that may be relatively expensive. That'd be done for large reports that only need to periodically change.

Web APIs return key-value pairs via JSON objects, not CSV-style results. This is mainly for simplicity in knowing what the values represent and accesing them via JavaScript's default parsing. Switching to show headers just once could be done later or for bigger results where size matters.

GZIP compression is not enabled for all endpoints by default. Adding it may be helpful, especially if caching larger reports along with the gzip'd form.

## Testing Manually

Manual testing is best done using `psql` directly (above notes in the "Example Data") and via `curl`. A browser works too, but it is hard to do POST and DELETE. Here are several examples.

```
# showing a site via ID
curl \
  --request GET \   
  http://localhost:5000/site/1
{
  "address": "123 Muffin Lane, Ann Arbor", 
  "contact": "John Smith", 
  "country": "USA", 
  "id": 1, 
  "name": "Site 1", 
  "postcode_or_zip": "48103", 
  "state_or_region": "MI"
}


# showing all sites
curl \
  --request GET \
  http://localhost:5000/sites/
[
  {
    "address": "123 Muffin Lane, Ann Arbor", 
    "contact": "John Smith", 
    "country": "USA", 
    "id": 1, 
    "name": "Site 1", 
    "postcode_or_zip": "48103", 
    "state_or_region": "MI"
  },
  ...
]


# removing a site by ID
curl \
  --request DELETE \
  http://localhost:5000/site/1

# updating (lazy-creating) a site
curl \
  --header "Content-Type: application/json" \
  --request POST \
  --data '{"site_id":2,"name":"Site 2000", "contact": "Bruce Campbell", "address": "555 Update Ave, Ann Arbor", "state_or_region": "MI", "country": "US", "postcode_or_zip": 48104}' \
  http://localhost:5000/site/2
  

# larger view for looking at all instrument types
curl \
  --request GET \
  http://localhost:5000/instruments/
[
  {
    "computer_id": 1, 
    "freezer_id": null, 
    "name": "Computer 1", 
    "site_id": 1, 
    "site_name": "Site 1"
  }, 
  {
    "computer_id": null, 
    "freezer_id": 2, 
    "name": "-40C", 
    "site_id": 1, 
    "site_name": "Site 1"
  }, 
  {
    "computer_id": 2, 
    "freezer_id": null, 
    "name": "Computer 2", 
    "site_id": 1, 
    "site_name": "Site 1"
  }, 
  {
    "computer_id": null, 
    "freezer_id": 1, 
    "name": "-20C", 
    "site_id": 1, 
    "site_name": "Site 1"
  }
]
```

Web endpoint for freezers, computers and containers were not added; however, place holder modules were. The implementation of these is very similar to site and less interesting for the sake of an initial example. Later on, these could be rounded out.

### Unit Tests and Integration Tests

No unit or integration tests were kept in the latest update of this repo. The example focuses more-so on data modeling a specific problem. Adding back in `coverage` for Python's dev mode and selenium/web-driver based integration tests will be done in the near future. See old commits for examples.
