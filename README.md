# Python, Flask and Postgres

This is a bootstrap of a common Python3-based Web API dev stack. It has bits of code
for writing a backend, unit tests, integration tests and code coverage. An update was
made in part using the code from [flask-on-docker](https://github.com/testdrivenio/flask-on-docker), which is another nice example!

Here are the assumptions.

* Docker containers are used for everything and docker-compose makes it easy to run them
* Python/Flask used for one or more backend services
* Postgres is the database
* gunicorn/nginx for prod-style deployment
* Selenium integration tests
* Plain SQL datamodel (No ORM! -- more on this later)

Extending the example to have a ReactJS for a single page app frontend will come next.
Along with that I'll add in using selenium/web-driver for end-to-end tests along with 
code coverage exports to the dev deployment.

## `docker-compose` and the app

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

## Testing Manually

You can still test and run each part of the app manually. This isn't preferred, but the instructions may be helpful for one-off tests or otherwise copying this work.


### Backend/Flask

The backend setup is based on using [Flask](http://flask.pocoo.org/docs/0.12/installation/) and can be run in a [Python3 venv](https://docs.python.org/3/library/venv.html#module-venv).

```
# create the venv to keep all installed libs local
python3 -m venv VENV

# enable venv
source VENV/bin/activate

# install all of the needed python libs
pip3 install -r requirements.txt

# launch the server
FLASK_APP=example/hello.py flask run
```

Open http://127.0.0.1:5000/ and you'll see the content sent by the Flask route bound to `/`.


### Unit Tests

Tests are run using Python3's standard unittest.

```
# coverage of just these tests
coverage run --source tests -m unittest tests/*.py

# show the test output
coverage report
```

Or run the tests individually or without coverage.

```
# run individual test file
python3 tests/flaskr_test.py

# run all using unittest
python3 -m unittest -v tests/*_test.py
```


## Integration Tests

Testing what a user sees when everything is together is arguably as or more important than the unit tests bundled with the backend. It is helpful to ensure that everything is correctly configured. It is also required for tests that rely on browser rendering of data provided by the backend.

Selenium and the [python bindings](http://selenium-python.readthedocs.io/installation.html) are used for these tests. It uses the [WebDriver](https://www.w3.org/TR/webdriver/) standard to connect and interact similar to a user on browsers such as Firefox, Chrome or Edge. 


```
# create the venv to keep all installed libs local
python3 -m venv VENV

# enable venv
source VENV/bin/activate

# install all of the needed python libs
pip3 install -r requirements.txt

# manually install the latest `geckodriver` for Firefox
# https://github.com/mozilla/geckodriver

# run all of the integration tests
python3 -m unittest tests/selenium_test.py
```

This above example assumes the Flask server is running and uses Firefox. You must manually download the latest [`geckodriver`]( https://github.com/mozilla/geckodriver/releases/tag/v0.19.0) and ensure it is in the environment path.


### Coverage Reports

There are two coverage reports of interest:

* Unit test coverage. Lines of code tested in isolated modules. If all is covered here, there is higher confidence it'll work.
* Integration test coverage. Lines of code used when testing user flows. If this works, things are wired together correctly and users should be able to successfuly use the tool.

Both of the above reports can be generated by `coverage`. The first is run whenever code changes in `flask`, and it doesn't rely on anything else. The integration tests are run after a full deploy of the project is done in the test environment. 

```
# run the server with coverage
flask/run_server.sh &

# run integration tests
integration/run_tests.sh

# now close the server
fg
ctrl+C

# generate the coverage report
pushd flask
coverage report
```
