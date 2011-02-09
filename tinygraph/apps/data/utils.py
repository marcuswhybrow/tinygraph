import time

def datetime_to_timestamp(dt):
    return time.mktime(dt.timetuple())