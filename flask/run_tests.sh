# switch to the flask app
cd ./flask

# setup virtualenv
source VENV/bin/activate

# run flask server locally with test coverage
coverage run --source example -m unittest tests/*_test.py

# display text-based coverage report
echo ""
coverage report
