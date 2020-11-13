This library provides a wrapper for Yggdrasil Admin API.

# Installation
## for Linux
```pip3 install yggdrasilctl```
## for Windows
```pip install yggdrasilctl```

# Usage
## sync version
```from pprint import pprint
from yggdrasilctl.sync import AdminAPI, APIError

api = AdminAPI() #unless otherwise specified it will connects to localhost:9001
try:
    pprint(api.getSelf())
except APIError as e:
    print(e)```
## async version
```import asyncio
from pprint import pprint
from yggdrasilctl import AdminAPI, APIError

async def main():
    api = AdminAPI()
    try:
        pprint(await api.getSelf())
    except APIError as e:
        print(e)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())```

# Detailed description of API methods
For deatails see [documentation](https://yggdrasil-network.github.io/admin.html) of Admin API.
