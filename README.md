This library provides a wrapper for Yggdrasil Admin API.

# Installation
## for Linux
```pip3 install yggdrasilctl```
## for Windows
```pip install yggdrasilctl```

# Usage
## sync version
```python3
from pprint import pprint
from yggdrasilctl.sync import AdminAPI, APIError

api = AdminAPI() #unless otherwise specified it will connects to localhost:9001
try:
    info = api.getSelf()
except APIError as e:
    print(e)
else:
    pprint(info)
```
## async version
```python3
import asyncio
from pprint import pprint
from yggdrasilctl import AdminAPI, APIError

async def main():
    api = AdminAPI()
    try:
        info = await api.getSelf()
    except APIError as e:
        print(e)
    else:
        pprint(info)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
```

# Detailed description of API methods
For details see [documentation](https://yggdrasil-network.github.io/admin.html) of Admin API.

# Links
This library on [PyPI](https://pypi.org/project/yggdrasilctl/)