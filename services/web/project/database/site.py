"""Site-specific database logic

This module purposely does not have access to underlying postgres DB connectivity. It
is limited to expressing the SQL required for the CRUD logic related to sites.

The `sql` module is used to ensure SQL injection attacks can't happen.
"""
from psycopg2 import sql

import project.database as db


def read_site(site_id):
    return db.read('site', site_id)


def delete_site(site_id):
    db.delete('site', site_id)


def update_site(site_id, name, contact, address, state_or_region, country, postcode_or_zip):
    q = (
        'INSERT INTO site (id, name, contact, address, state_or_region, country, postcode_or_zip) '
        '    VALUES ({site_id}, {name}, {contact}, {address}, {state_or_region}, {country}, {postcode_or_zip}) '
        'ON CONFLICT (id) DO UPDATE SET'
        '    name = {name},'
        '    contact = {contact},'
        '    address = {address},'
        '    state_or_region = {state_or_region},'
        '    country = {country},'
        '    postcode_or_zip = {postcode_or_zip};'
    )

    # ensure no SQL injection attacks or accidental bad formatting
    query = sql.SQL(q).format(
        site_id=sql.Literal(site_id),
        name=sql.Literal(name),
        contact=sql.Literal(contact),
        address=sql.Literal(address),
        state_or_region=sql.Literal(state_or_region),
        country=sql.Literal(country),
        postcode_or_zip=sql.Literal(postcode_or_zip),
    )

    db.update(query)


def list_sites(offset=0, limit=0):
    # build up a pagable query of sites
    q, params = db.paginate('SELECT * FROM site', offset, limit)

    # ensure no SQL injection attacks or accidental bad formatting
    query = sql.SQL(q).format(**params)

    # stream result without buffering in memory
    for record in db.query(query):
        yield record
