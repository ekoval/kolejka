from mongoengine import (
    Document, ObjectIdField, StringField, FloatField, IntField, DateTimeField,
    BooleanField)
from datetime import datetime

from constants import DATA_TYPES, ZONE_TYPES


class Tracking(Document):
    tracking_id = StringField(required=True)
    data_type = StringField(max_length=5, choices=DATA_TYPES, required=True)
    zone_id = ObjectIdField(required=True)
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
            'data_type': self.data_type,
            'zone_id': str(self.zone_id),
            'tracking_timestamp': self.tracking_timestamp,
            'created_at': self.created_at,
            'lon': self.lon,
            'lat': self.lat
        }


class Zone(Document):
    name = StringField(required=True)
    description = StringField()
    zone_type = StringField(choices=ZONE_TYPES, required=True)
    image = StringField()
    lat = FloatField(required=True)
    lon = FloatField(required=True)
    radius = IntField(required=True)
    enabled = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)

    def as_dict(self):
        data = self.to_mongo()
        data['id'] = str(data.pop('_id'))
        return data
