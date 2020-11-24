from datetime import datetime
import time

def grab(config):
    try:
        ts_file = open(config.TIME_STAMP, 'r')
        ts = datetime.fromtimestamp(int(ts_file.readline()))
        return ts
    except:
        return datetime.now()

def push(ts, config):
    ts_file = open(config.TIME_STAMP, 'w+')
    ts_file.write(str(time.mktime(ts.timetuple())))
