# switch to the flask app
cd ./flask

# setup virtualenv
source VENV/bin/activate

# run the flask server locally
#FLASK_APP=example/hello.py flask run

# run flask server locally with test coverage
coverage run --source example example/hello.py
