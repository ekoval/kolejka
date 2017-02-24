from mongoengine import Document, StringField, FloatField, IntField, DateTimeField
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
