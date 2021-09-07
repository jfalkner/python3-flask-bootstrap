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
