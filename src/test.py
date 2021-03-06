import json
import time
import unittest
from mongoengine.fields import ObjectId
from mongoengine.connection import _get_db
from app import app
from models import Tracking, Zone

from constants import DataTypes, ZoneTypes


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
            "Missing keys: 'data_type', 'lat', 'lon', 'tracking_id', 'tracking_timestamp', 'zone_id'"
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

        payload = {
            'tracking_id': '123',
            'tracking_timestamp': 100000,
            'lat': 0.0,
            'lon': 0.0,
            'zone_id': ''
        }
        res = self.app.post('/v1/tracking',
                            data=json.dumps(payload),
                            content_type='application/json')
        body = json.loads(res.data)
        self.assertEquals(res.status_code, 400)
        self.assertEquals(body['status'], 'error')
        self.assertEquals(body['data'], "zone_id should be non-empty string")

        payload = {
            'tracking_id': '123',
            'tracking_timestamp': 100000,
            'lat': 0.0,
            'lon': 0.0,
            'zone_id': 'zone-id',
            'data_type': 'wrong'
        }
        res = self.app.post('/v1/tracking',
                            data=json.dumps(payload),
                            content_type='application/json')
        body = json.loads(res.data)
        self.assertEquals(res.status_code, 400)
        self.assertEquals(body['status'], 'error')
        self.assertEquals(
            body['data'],
            'possible data_type values are: enter, leave, track'
        )

    def test_tracking_post(self):
        payload = {
            'zone_id': str(ObjectId()),
            'data_type': DataTypes.enter,
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
                    'data_type': DataTypes.enter,
                    'zone_id': str(ObjectId()),
                    'tracking_timestamp': 100000,
                    'lat': 10.0,
                    'lon': 20.0
                },
                {
                    'tracking_id': 'track_id',
                    'data_type': DataTypes.leave,
                    'zone_id': str(ObjectId()),
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
            "Missing keys: 'lat', 'lon', 'name', 'radius', 'zone_type'"
        )

    def test_add_delete_zone(self):
        payload = {
            'name': 'Grushiv',
            'description': 'Kolejka inodi',
            'zone_type': ZoneTypes.control,
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

        zone = body['data'][0]
        self.assertEquals(zone['name'], 'Grushiv')
        self.assertEquals(zone['description'], 'Kolejka inodi')
        self.assertEquals(zone['image'], '')
        self.assertEquals(zone['lat'], 10.5)
        self.assertEquals(zone['lon'], 20)
        self.assertEquals(zone['radius'], 3000)
        self.assertIn('created_at', zone)

        res = self.app.delete('/v1/zones/{id}'.format(id=zone['id']))
        self.assertEquals(res.status_code, 200)

        res = self.app.get('/v1/zones?show_inactive=1')
        body = json.loads(res.data)
        self.assertEquals(body['data'][0]['enabled'], False)


class TestGetTrackingDataForTrackingID(unittest.TestCase):
    def setUp(self):
        app.debug = True
        self.app = app.test_client()
        _get_db().tracking.remove()
        _get_db().zone.remove()

        tracking_time = time.time()

        self.points = [
            Tracking.objects.create(
                tracking_id='phone1',
                zone_id=str(ObjectId()),
                data_type=DataTypes.enter,
                lat=10.1,
                lon=10.2,
                tracking_timestamp=tracking_time
            ),

            Tracking.objects.create(
                tracking_id='phone1',
                zone_id=str(ObjectId()),
                data_type=DataTypes.track,
                lat=10.3,
                lon=10.4,
                tracking_timestamp=tracking_time+1
            ),

            Tracking.objects.create(
                tracking_id='phone2',
                zone_id=str(ObjectId()),
                data_type=DataTypes.track,
                lat=10.5,
                lon=10.6,
                tracking_timestamp=tracking_time+2
            )
        ]

        self.results = json.loads(
            self.app.get('/v1/tracking-data/phone1').data)
        self.results_filtered = json.loads(self.app.get(
            '/v1/tracking-data/phone1?data_type=enter').data)

    def test_returns_correct_data(self):
        self.assertEqual(self.results['status'], 'success')
        data = self.results['data']
        self.assertEqual(len(data), 2)

        # TODO: improve tests. Now we have mess with `created_at`, so it's
        # hard to check data comprehensively.
        for point in data:
            self.assertEqual(point['tracking_id'], 'phone1')
            for key in (
                    'tracking_id', 'lat', 'lon',
                    'created_at', 'tracking_timestamp'):
                self.assertIn(key, point)

    def test_returns_correct_data_filtered_by_data_type(self):
        self.assertEqual(self.results_filtered['status'], 'success')
        data = self.results_filtered['data']
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['data_type'], DataTypes.enter)


class TestGetTrackingDataForAllIDs(unittest.TestCase):
    def setUp(self):
        app.debug = True
        self.app = app.test_client()
        _get_db().tracking.remove()
        _get_db().zone.remove()

        tracking_time = time.time()

        self.points = [
            Tracking.objects.create(
                tracking_id='phone1',
                zone_id=str(ObjectId()),
                data_type=DataTypes.enter,
                lat=10.1,
                lon=10.2,
                tracking_timestamp=tracking_time
            ),

            Tracking.objects.create(
                tracking_id='phone1',
                zone_id=str(ObjectId()),
                data_type=DataTypes.enter,
                lat=10.3,
                lon=10.4,
                tracking_timestamp=tracking_time+1
            ),

            Tracking.objects.create(
                tracking_id='phone2',
                zone_id=str(ObjectId()),
                data_type=DataTypes.enter,
                lat=10.5,
                lon=10.6,
                tracking_timestamp=tracking_time+2
            )
        ]

        self.results = json.loads(self.app.get('/v1/tracking-data/ALL').data)

    def test_returns_correct_data(self):
        self.assertEqual(self.results['status'], 'success')
        data = self.results['data']
        self.assertEqual(len(data), 3)


class TestDeleteTrackingDataForAllIDs(unittest.TestCase):
    def setUp(self):
        app.debug = True
        self.app = app.test_client()
        _get_db().tracking.remove()
        _get_db().zone.remove()

        tracking_time = time.time()

        Tracking.objects.create(
            tracking_id='phone1',
            zone_id=str(ObjectId()),
            data_type=DataTypes.enter,
            lat=10.1,
            lon=10.2,
            tracking_timestamp=tracking_time
        )

        Tracking.objects.create(
            tracking_id='phone2',
            zone_id=str(ObjectId()),
            data_type=DataTypes.enter,
            lat=10.1,
            lon=10.2,
            tracking_timestamp=tracking_time
        )
        self.assertEqual(len(Tracking.objects.all()), 2)
        self.result = self.app.delete('/v1/tracking-data/ALL')

    def test_returns_correct_data(self):
        self.assertEqual(len(Tracking.objects.all()), 0)


class TestGetActiveZones(unittest.TestCase):
    def setUp(self):
        app.debug = True
        self.app = app.test_client()
        _get_db().tracking.remove()
        _get_db().zone.remove()

        self.zone = Zone.objects.create(
            name='test', zone_type=ZoneTypes.control, lat=10, lon=10,
            radius=10, enabled=False
        )
        self.result = json.loads(self.app.get('/v1/zones').data)
        self.assertEqual(len(self.result['data']), 0)

    def test_inactive_zones_are_shown_if_flag_passed(self):
        self.result = json.loads(
            self.app.get('/v1/zones?show_inactive=True').data)
        self.assertEqual(len(self.result['data']), 1)


class TestCanCreateZoneWithoutOptionalFields(unittest.TestCase):
    def setUp(self):
        payload = {
            'name': 'test',
            'zone_type': ZoneTypes.control,
            'lat': 10.5,
            'lon': 20,
            'radius': 3000
        }
        self.result = app.test_client().post(
            '/v1/zones', data=json.dumps(payload),
            content_type='application/json'
        )

    def test_zone_is_created(self):
        self.assertEquals(self.result.status_code, 200)
