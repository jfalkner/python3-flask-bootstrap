#!/bin/bash

# setup venv
cd integration
source VENV/bin/activate

# set path to `geckodriver`. assume a copy is in local dir
export PATH=.:$PATH

# run the tests
python3 -m unittest tests/selenium_test.py

