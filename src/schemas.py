from schema import Schema, And, Or, Use

tracking_base = {
    'tracking_id': And(basestring, len, error='tracking_id should be non-empty string'),
    'tracking_timestamp': Use(int, error='tracking_timestamp should be integer'),
    'lat': Or(int, float, error='lat should be either int or float'),
    'lon': Or(int, float, error='lon should be either int or float')
}

tracking_schema = Schema(tracking_base)

bulk_tracking_schema = Schema({
    'data': [tracking_base]
})
