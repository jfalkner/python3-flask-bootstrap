"""Container-specific database logic

See project/database/site/py for a more complete example. Not all of this was implemented.

This module purposely does not have access to underlying postgres DB connectivity. It
is limited to expressing the SQL required for the CRUD logic related to sites.

The `sql` module is used to ensure SQL injection attacks can't happen.
"""
from psycopg2 import sql

import project.database as db


def read_container(container_id):
    return db.read('container', container_id)


def list_containers(offset=0, limit=0):
    # build up a pagable query
    q, params = db.paginate('SELECT * FROM container', offset, limit)

    # ensure no SQL injection attacks or accidental bad formatting
    query = sql.SQL(q).format(**params)

    # stream result without buffering in memory
    for record in db.query(query):
        yield record
