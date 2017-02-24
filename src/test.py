import json
import unittest
from mongoengine.connection import _get_db
from app import app

class KolejkaTest(unittest.TestCase):
    def setUp(self):
        app.debug = True
        self.app = app.test_client()
        _get_db().tracking.remove()

    def tearDown(self):
        pass

    def test_wrong_content_type(self):
        res = self.app.post('/v1/tracking')
        body = json.loads(res.data)
        self.assertEquals(res.status_code, 400)
        self.assertEquals(body['status'], 'error')
        self.assertEquals(body['data'], 'content-type header should be application/json')

    def test_wrong_json_payload(self):
        res = self.app.post('/v1/tracking',
                            data='{wrong payload}',
                            content_type='application/json')
        body = json.loads(res.data)
        self.assertEquals(res.status_code, 400)
        self.assertEquals(body['status'], 'error')
        self.assertEquals(body['data'], 'please provide valid json payload')

    def test_missing_fields(self):
        res = self.app.post('/v1/tracking',
                            data='{}',
                            content_type='application/json')
        body = json.loads(res.data)
        self.assertEquals(res.status_code, 400)
        self.assertEquals(body['status'], 'error')
        self.assertEquals(body['data'], "Missing keys: 'lat', 'lon', 'tracking_id', 'tracking_timestamp'")

    def test_tracking_field_validation(self):
        payload = {
            'tracking_id': '',
            'tracking_timestamp': 0,
            'lat': 0.0,
            'lon': 0.0
        }
        res = self.app.post('/v1/tracking',
                            data=json.dumps(payload),
                            content_type='application/json')
        body = json.loads(res.data)
        self.assertEquals(res.status_code, 400)
        self.assertEquals(body['status'], 'error')
        self.assertEquals(body['data'], "tracking_id should be non-empty string")

        payload = {
            'tracking_id': '123',
            'tracking_timestamp': 100000,
            'lat': '0.0',
            'lon': 0.0
        }
        res = self.app.post('/v1/tracking',
                            data=json.dumps(payload),
                            content_type='application/json')
        body = json.loads(res.data)
        self.assertEquals(res.status_code, 400)
        self.assertEquals(body['status'], 'error')
        self.assertEquals(body['data'], "lat should be either int or float")

        payload = {
            'tracking_id': '123',
            'tracking_timestamp': 100000,
            'lat': 0.0,
            'lon': '0.0'
        }
        res = self.app.post('/v1/tracking',
                            data=json.dumps(payload),
                            content_type='application/json')
        body = json.loads(res.data)
        self.assertEquals(res.status_code, 400)
        self.assertEquals(body['status'], 'error')
        self.assertEquals(body['data'], "lon should be either int or float")

    def test_tracking_post(self):
        payload = {
            'tracking_id': 'track_id',
            'tracking_timestamp': 100000,
            'lat': 10.0,
            'lon': 20.0
        }
        res = self.app.post('/v1/tracking',
                            data=json.dumps(payload),
                            content_type='application/json')
        self.assertEquals(res.status_code, 200)
        body = json.loads(res.data)
        self.assertEquals(body['status'], 'success')
        self.assertEquals(body['data']['tracking_id'], "track_id")
        self.assertEquals(body['data']['tracking_timestamp'], 100000)
        self.assertEquals(body['data']['lat'], 10.0)
        self.assertEquals(body['data']['lon'], 20.0)

    def test_bulk_tracking_post(self):
        payload = {
            'data': [
                {
                    'tracking_id': 'track_id',
                    'tracking_timestamp': 100000,
                    'lat': 10.0,
                    'lon': 20.0
                },
                {
                    'tracking_id': 'track_id',
                    'tracking_timestamp': 100001,
                    'lat': 10.5,
                    'lon': 20.5
                }
            ]}
        res = self.app.post('/v1/bulk_tracking',
                            data=json.dumps(payload),
                            content_type='application/json')
        self.assertEquals(res.status_code, 200)
        body = json.loads(res.data)
        self.assertEquals(body['status'], 'success')

        self.assertEquals(body['data'][0]['tracking_id'], "track_id")
        self.assertEquals(body['data'][0]['tracking_timestamp'], 100000)
        self.assertEquals(body['data'][0]['lat'], 10.0)
        self.assertEquals(body['data'][0]['lon'], 20.0)

        self.assertEquals(body['data'][1]['tracking_id'], "track_id")
        self.assertEquals(body['data'][1]['tracking_timestamp'], 100001)
        self.assertEquals(body['data'][1]['lat'], 10.5)
        self.assertEquals(body['data'][1]['lon'], 20.5)

    def test_bulk_tracking_validation(self):
        payload = {
            'data': [
                {
                    'tracking_id': 'track_id',
                    'tracking_timestamp': 100000,
                    'lat': 10.0,
                    'lon': 20.0
                },
                {
                    'tracking_id': 'track_id',
                    'tracking_timestamp': 100001,
                    'lat': 10.5,
                    'lon': 20.5
                }
            ]}
        payload['data'] = [1,2]
        res = self.app.post('/v1/bulk_tracking',
                            data=json.dumps(payload),
                            content_type='application/json')
        self.assertEquals(res.status_code, 400)
