from mongoengine import (
    Document, StringField, FloatField, IntField, DateTimeField, BooleanField)
from datetime import datetime


class Tracking(Document):
    tracking_id = StringField(required=True)
    lat = FloatField(required=True)
    lon = FloatField(required=True)
    tracking_timestamp = IntField(required=True)
    created_at = DateTimeField(default=datetime.now)

    meta = {
        'indexes': [
            ('tracking_id', 'tracking_timestamp')
        ]
    }

    def as_dict(self):
        return {
            'id': str(self.id),
            'tracking_id': self.tracking_id,
            'tracking_timestamp': self.tracking_timestamp,
            'created_at': self.created_at,
            'lon': self.lon,
            'lat': self.lat
        }


class Zone(Document):
    name = StringField(required=True)
    description = StringField()
    image = StringField()
    lat = FloatField(required=True)
    lon = FloatField(required=True)
    radius = IntField(required=True)
    enabled = BooleanField(default=True)

    def as_dict(self):
        data = self.to_mongo()
        data['id'] = str(data.pop('_id'))
        return data
