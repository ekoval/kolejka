class DataTypes(object):
    enter = 'enter'
    leave = 'leave'
    track = 'track'


class ZoneTypes(object):
    control = 'control'
    checkpoint = 'checkpoint'


DATA_TYPES = (
    (DataTypes.enter, DataTypes.enter),
    (DataTypes.leave, DataTypes.leave),
    (DataTypes.track, DataTypes.track),
)


ZONE_TYPES = (
    (ZoneTypes.control, ZoneTypes.control),
    (ZoneTypes.checkpoint, ZoneTypes.checkpoint),
)
