import asyncio
from contextlib import asynccontextmanager
from datetime import datetime as dt, timedelta as td

from .errors import APIUnreachable

def human_readable(size:int, unit='B')->str:
    for prefix in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(size) < 1024.0:
            break
        size = round(size/1024, 2)
    return "{}{}{}".format(size, prefix, unit)

@asynccontextmanager
async def connect(host, port):
    try:
        reader, writer = await asyncio.open_connection(host, port)
    except OSError as e:
        raise APIUnreachable(str(e))
    try:
        yield reader, writer
    finally:
        writer.close()
        await writer.wait_closed()

def preprocess(**kwargs)->dict:
    if 'uptime' in kwargs:
        sec = round(kwargs['uptime'])
        kwargs['uptime'] = td(seconds=sec)
    if 'last_seen' in kwargs:
        sec = round(kwargs['last_seen'])
        date = dt.now() - td(seconds=sec)
        kwargs['last_seen'] = date
    return kwargs
