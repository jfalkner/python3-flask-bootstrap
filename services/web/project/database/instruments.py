"""Instrument Database View Logic

This module purposely does not have access to underlying postgres DB connectivity. It
is limited to expressing the SQL required for the CRUD logic related to sites.

The `sql` module is used to ensure SQL injection attacks can't happen.

This module is interesting because it exposes a view from the database so that a
logical grouping of "instruments" (computers and freezers) can be displayed to the UI.
By abstracting this logic via a Python method we keep the Python API simple as well
as the database modeling. It is easy to directly see, edit and optimize what the SQL is
doing here compared to trying to reason about how an ORM is implementing polymorphism
and if it is being efficient about it.
"""
from psycopg2 import sql

import project.database as db


def list_instruments(offset=0, limit=0):
    """Supports a view of all 'instruments' at the company

    This is an example of how a custom view can be made for a Web UI widget that is
    trying to show all instrumennts. e.g. an equipment auditing page. Any subsequent
    edits or deletes to entries would call the respecting freezer or computer API.
    """
    q, params = db.paginate(
        # show all computer "instruments" first
        '(SELECT'
        '    s.id, s.name as site_name,'
        '    c.id AS computer_id,'
        '    NULL as freezer_id,'
        '    c.name AS instrument_name'
        ' FROM site AS s FULL JOIN computer AS c ON s.id = c.site_id'
        ' WHERE c.id IS NOT NULL ORDER BY s.id, c.id ASC)'
        'UNION '
        # show all freezer "instruments" second
        '(SELECT'
        '   s.id, s.name as site_name,'
        '   NULL AS computer_id,'
        '   f.id AS freezer_id,'
        '   f.name AS freezer_name'
        ' FROM site AS s FULL JOIN freezer AS f ON s.id = f.site_id'
        ' WHERE f.id IS NOT NULL ORDER BY s.id, f.id ASC)',
        offset, limit
    )

    # ensure no SQL injection attacks or accidental bad formatting
    query = sql.SQL(q).format(**params)

    # stream result without buffering in memory
    for record in db.query(query):
        yield record
