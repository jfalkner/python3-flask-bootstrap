import os
from flask import Flask
from example import hello
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):


    def setUp(self):
        hello.app.testing = True
        self.app = hello.app.test_client()

    def test_hello(self):
        rv = self.app.get('/')
        assert rv.mimetype == 'text/html'
        assert rv.data == b'Hello, World!'
        assert rv.status_code == 200
        

    def test_nothing(self):
        assert 1 == 1


if __name__ == '__main__':
    unittest.main()
