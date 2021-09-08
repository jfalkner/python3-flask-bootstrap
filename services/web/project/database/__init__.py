"""Core Postgres database logic

These are core features related to using Postgres. They are kept here in one place so
that the other database API don't need to remake them and use them consistently.

* query() ensures that connections and cursors are correctly opened and closed. It also
  ensures queries that modify the database correctly commit results.

* paginate() modifies queries to allow paging through results to ensure not too much
  memory is used during queries and that the web UI can load and show partial results
  quickly while loading full data.

* read(), delete() and update() abstract the main CRUD actions that are later
  used for the various tables: site, computer, freezer and container.
"""
import os

from psycopg2 import connect, sql


def update(sql):
    list(query(sql, update=True))


def query(sql, update=False):
    postgres_url = os.environ['DATABASE_URL']
    conn = connect(postgres_url)
    try:
        cur = conn.cursor()
        try:
            cur.execute(sql)
            if not update:
                for record in cur:
                    yield record
            if update:
                conn.commit()
        finally:
            cur.close()
    finally:
        conn.close()


def paginate(q, offset=0, limit=0):
    q += ' ORDER BY id ASC OFFSET {offset}'
    params = {'offset': sql.Literal(offset)}
    if limit:
        q += 'LIMIT {limit}'
        params['limit'] = sql.Literal(limit)
    return q, params


def read(table, row_id):
    q = 'SELECT * FROM {} WHERE id = {}'

    # ensure no SQL injection attacks or accidental bad formatting
    q = sql.SQL(q).format(sql.Identifier(table), sql.Literal(row_id))

    # return the only entry, if it exists
    for record in query(q):
        return record


def delete(table, row_id):
    q = 'DELETE FROM {} WHERE id = {};'

    # ensure no SQL injection attacks or accidental bad formatting
    query = sql.SQL(q).format(sql.Identifier(table), sql.Literal(row_id))
    update(query)
