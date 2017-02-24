import json
import unittest
from mongoengine.connection import _get_db
from app import app


class KolejkaTest(unittest.TestCase):
    def setUp(self):
        app.debug = True
        self.app = app.test_client()
        _get_db().tracking.remove()
        _get_db().zone.remove()

    def tearDown(self):
        pass

    def test_wrong_content_type(self):
        res = self.app.post('/v1/tracking')
        body = json.loads(res.data)
        self.assertEquals(res.status_code, 400)
        self.assertEquals(body['status'], 'error')
        self.assertEquals(
            body['data'], 'content-type header should be application/json')

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
        self.assertEquals(
            body['data'],
            "Missing keys: 'lat', 'lon', 'tracking_id', 'tracking_timestamp'"
        )

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
        self.assertEquals(
            body['data'], 'tracking_id should be non-empty string')

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
        payload['data'] = [1, 2]
        res = self.app.post('/v1/bulk_tracking',
                            data=json.dumps(payload),
                            content_type='application/json')
        self.assertEquals(res.status_code, 400)

    def test_empty_zones_get(self):
        res = self.app.get('/v1/zones')
        self.assertEquals(res.status_code, 200)
        body = json.loads(res.data)
        self.assertEquals(body['data'], [])

    def test_add_zone_validation(self):
        payload = {}
        res = self.app.post('/v1/zones',
                            data=json.dumps(payload),
                            content_type='application/json')
        self.assertEquals(res.status_code, 400)
        body = json.loads(res.data)
        self.assertEquals(
            body['data'],
            "Missing keys: 'description', 'image', 'lat', 'lon', 'name', 'radius'"
        )

    def test_add_delete_zone(self):
        payload = {
            'name': 'Grushiv',
            'description': 'Kolejka inodi',
            'image': '',
            'lat': 10.5,
            'lon': 20,
            'radius': 3000
        }
        res = self.app.post('/v1/zones',
                            data=json.dumps(payload),
                            content_type='application/json')
        self.assertEquals(res.status_code, 200)
        body = json.loads(res.data)

        self.assertEquals(body['data']['name'], 'Grushiv')
        self.assertEquals(body['data']['description'], 'Kolejka inodi')
        self.assertEquals(body['data']['image'], '')
        self.assertEquals(body['data']['lat'], 10.5)
        self.assertEquals(body['data']['lon'], 20)
        self.assertEquals(body['data']['radius'], 3000)

        res = self.app.get('/v1/zones')
        body = json.loads(res.data)

        self.assertEquals(len(body['data']), 1)

        self.assertEquals(body['data'][0]['name'], 'Grushiv')
        self.assertEquals(body['data'][0]['description'], 'Kolejka inodi')
        self.assertEquals(body['data'][0]['image'], '')
        self.assertEquals(body['data'][0]['lat'], 10.5)
        self.assertEquals(body['data'][0]['lon'], 20)
        self.assertEquals(body['data'][0]['radius'], 3000)

        zone_id = body['data'][0]['id']

        res = self.app.delete('/v1/zones/{id}'.format(id=zone_id))
        self.assertEquals(res.status_code, 200)

        res = self.app.get('/v1/zones')
        body = json.loads(res.data)
        self.assertEquals(body['data'], [])
