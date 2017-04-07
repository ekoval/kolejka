from schema import Schema, And, Optional, Or, Use, Regex

tracking_base = {
    'tracking_id': And(
        basestring, len, error='tracking_id should be non-empty string'),
    'zone_id': And(
        basestring, len, error='zone_id should be non-empty string'),
    'data_type': Regex(
        '(enter|leave|track)',
        error='possible data_type values are: enter, leave, track'),
    'tracking_timestamp': Use(
        int, error='tracking_timestamp should be integer'),
    'lat': Or(int, float, error='lat should be either int or float'),
    'lon': Or(int, float, error='lon should be either int or float')
}

tracking_schema = Schema(tracking_base)

bulk_tracking_schema = Schema({
    'data': [tracking_base]
})

zone_schema = Schema({
    'name': And(basestring, len, error='name should be non-empty string'),
    Optional('description'): And(basestring, len),
    'zone_type': Regex(
        '(control|checkpoint)',
        error='possible zone_type values are: control, checkpoint'),
    Optional('image'): And(basestring),
    'lat': Or(int, float, error='lat should be either int or float'),
    'lon': Or(int, float, error='lon should be either int or float'),
    'radius': Or(int, error='radius should be int')
})
