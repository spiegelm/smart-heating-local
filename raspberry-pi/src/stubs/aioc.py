#!/usr/local/bin/python3.4

import logging
import asyncio

from aiocoap import *

logging.basicConfig(level=logging.INFO)

@asyncio.coroutine
def main():
    protocol = yield from Context.create_client_context()

    request = Message(code=GET)
    request.set_request_uri('coap://[fdfd::221:2eff:ff00:22dc]/sensors/temperature')

    try:
        response = yield from protocol.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        print('Result: %s\n%r'%(response.code, response.payload))

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
