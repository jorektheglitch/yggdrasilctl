from datetime import datetime as dt, timedelta as td

def human_readable(size:int, suffix='B')->str:
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def preprocess(**kwargs)->dict:
    if 'proto' in kwargs and 'endpoint' in kwargs:
        kwargs['faddr'] = '{}://{}'.format(kwargs['proto'], kwargs['endpoint'])
    if 'uptime' in kwargs:
        sec = round(kwargs['uptime'])
        kwargs['uptime'] = td(seconds=sec)
    if 'last_seen' in kwargs:
        sec = round(kwargs['last_seen'])
        date = dt.now() - td(seconds=sec)
        kwargs['last_seen'] = date
    return kwargs
