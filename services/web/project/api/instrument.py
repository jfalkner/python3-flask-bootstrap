from flask import (
    Blueprint,
    jsonify,
)

from project.database import instruments as db

instrument_api = Blueprint('instrument_api', __name__)


def instrument2dict(site_id, site_name, computer_id, freezer_id, name):
    return {
        'site_id': site_id,
        'site_name': site_name,
        'computer_id': computer_id,
        'freezer_id': freezer_id,
        'name': name,
    }


def dict2instrument(site):
    return (
        site['site_id'],
        site['computer_id'],
        site['freezer_id'],
        site['name'],
    )


@instrument_api.route("/instruments/")
@instrument_api.route("/instruments/<int:offset>/<int:limit>")
def get_instruments(offset=0, limit=0):
    return jsonify([instrument2dict(*i) for i in db.list_instruments(offset, limit)])
