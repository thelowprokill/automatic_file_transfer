from datetime import datetime
import time

def grab(config, message):
    try:
        ts_file = open(config.TIME_STAMP, 'r')
        ts = datetime.fromtimestamp(float(ts_file.readline()))
        message(2, "Time stamp grabbed {}".format(ts))
        return ts
    except:
        message(0, "Error: Failed to read timestamp")
        return datetime.now()

def push(ts, config, message):
    ts_file = open(config.TIME_STAMP, 'w+')
    ts_file.write(str(time.mktime(ts.timetuple())))
    message(2, "Time stamp written {}".format(ts))
