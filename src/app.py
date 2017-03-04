import os
from flask import Flask, abort, request
from flask_mongoengine import DoesNotExist, MongoEngine
from helpers import api_response
from models import Tracking, Zone
from schemas import tracking_schema, bulk_tracking_schema, zone_schema


MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/test')

db = MongoEngine()
app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': MONGODB_URI.split('/')[-1],
    'host': MONGODB_URI
}
db.init_app(app)


@app.route('/')
@api_response()
def index():
    return {'app': 'kolejka'}


@app.route('/v1/tracking', methods=['POST'])
@api_response(schema=tracking_schema)
def tracking(data):
    obj = Tracking(**data).save()
    return obj.as_dict()


@app.route('/v1/bulk_tracking', methods=['POST'])
@api_response(schema=bulk_tracking_schema)
def bulk_tracking(bulk_data):
    res = []
    for tracking_data in bulk_data['data']:
        obj = Tracking(**tracking_data).save()
        res.append(obj.as_dict())
    return res


@app.route('/v1/zones', methods=['GET'])
@api_response()
def get_zones():
    return [zone.as_dict() for zone in Zone.objects.all()]


@app.route('/v1/zones', methods=['POST'])
@api_response(schema=zone_schema)
def post_zone(data):
    zone = Zone(**data).save()
    return zone.as_dict()


@app.route('/v1/zones/<zone_id>/set-pair-zone', methods=['POST'])
def set_zone_pair(zone_id):
    pair_zone_id = request.json['pair_zone_id']

    try:
        zone = Zone.objects.get(pk=zone_id)
        pair_zone = Zone.objects.get(pk=pair_zone_id)
    except DoesNotExist:
        raise abort(404)

    zone.pair_zone_id = pair_zone.id
    zone.save()

    pair_zone.pair_zone_id = zone.id
    pair_zone.save()
    return 'Pair set: {} <-> {}'.format(zone.id, pair_zone.id)


@app.route('/v1/zones/<id>', methods=['DELETE'])
@api_response()
def delete_zone(id):
    zone = Zone.objects.get(pk=id)
    zone.enabled = False
    zone.save()


@app.route('/v1/tracking-data/<tracking_id>', methods=['GET'])
@api_response()
def get_tracking_data(tracking_id):
    data = Tracking.objects.filter(
        tracking_id=tracking_id).order_by('tracking_timestamp')
    return [point.as_dict() for point in data]


if __name__ == '__main__':
    app.run(debug=True)
