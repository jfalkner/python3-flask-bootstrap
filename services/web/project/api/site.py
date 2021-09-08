"""Web API for sites

This has a pattern of a custom tuple-to-dict and dict-to-tuple method that is used
with the `project/database/site.py` CRUD methods. 

See README.md for other notes about common RESTful patterns followed here.
"""
from flask import (
    Blueprint,
    jsonify,
    request,
    abort,
    make_response,
)

from project.database import site as db

site_api = Blueprint('site_api', __name__)


def site2dict(site_id, name, contact, address, state_or_region, country, postcode_or_zip):
    """Coverts a tuple of data representing a site to a dict with keys"""
    return {
        'id': site_id,
        'name': name,
        'contact': contact,
        'address': address,
        'state_or_region': state_or_region,
        'country': country,
        'postcode_or_zip': postcode_or_zip,
    }


def dict2site(site):
    """Converts a dictionary representation of a site back to a tuple of values

    This is the inverse of site2dict()
    """
    return (
        site['site_id'],
        site['name'],
        site['contact'],
        site['address'],
        site['state_or_region'],
        site['country'],
        str(site['postcode_or_zip'])
    )


@site_api.route("/site/<int:site_id>", methods=['GET'])
def get_site(site_id):
    site = db.read_site(site_id)

    return jsonify(site2dict(*site)) if site else abort(400)


@site_api.route("/sites/")
@site_api.route("/sites/<int:offset>/<int:limit>")
def get_sites(offset=0, limit=0):
    return jsonify([site2dict(*site) for site in db.list_sites(offset, limit)])


@site_api.route("/site/<int:site_id>", methods=['POST'])
def post_site(site_id):

    site = request.get_json()

    # validate that required fields exist
    required = ['name', 'contact', 'address', 'state_or_region', 'country', 'postcode_or_zip']
    for r in required:
        if r not in required:
            # could improve to send back a more helpful message
            return abort(400)

    db.update_site(*dict2site(site))
    return make_response('Site updated', 200)


@site_api.route("/site/<int:site_id>", methods=['DELETE'])
def delete_site(site_id):
    db.delete_site(site_id)
    return make_response(f'Site deleted: {site_id}', 200)
