#!/usr/local/bin/python3.4

import logging
import asyncio

from aiocoap import *

logging.basicConfig(level=logging.INFO)

# thread safe queue to store the results
from collections import deque
results = deque()

@asyncio.coroutine
def get_temp():
    protocol = yield from Context.create_client_context()

    request = Message(code=GET)
    request.set_request_uri('coap://[fdfd::221:2eff:ff00:228b]/sensors/temperature')
    
    try:
        response = yield from protocol.request(request).response
    except Exception as e:
        print('Failed to fetch resource:')
        print(e)
    else:
        # print(vars(response))
        #  'code': <Successful Response Code 69 "2.05 Content">
        # what kind of thing is response.code?
        
        # parse response code parts: https://tools.ietf.org/html/rfc7252#section-3
        response_code_class = response.code // 32
        response_code_detail = response.code % 32
        
        # compose response code
        #response_code = response_code_class + response_code_detail / 100;
        response_code = str(response_code_class) + ".{:02d}".format(response_code_detail)
        # print(response_code)
        print('Response: %s\n%r'%(response.code, float(response.payload)))
        
        temperature = float(response.payload)
        results.append(temperature)

def main():
    # run multiple tasks in parallel
    tasks = [
        asyncio.async(get_temp()),
        asyncio.async(get_temp())]
    asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
    for r in results:
        print("Result: " + str(r))
    
    results.clear()
    
    # single asynchronous task
    asyncio.get_event_loop().run_until_complete(get_temp())
    print ("Result: " + str(results[0]))
    
if __name__ == "__main__":
    main()
