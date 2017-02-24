import os
from flask import Flask, jsonify, request
from flask_mongoengine import MongoEngine
from helpers import api_response
from models import Tracking
from schemas import tracking_schema, bulk_tracking_schema


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


if __name__ == '__main__':
    app.run(debug=True)
