import asyncio
import time

from toolkit.sdp_lib import conflicts, controller_management

import requests
import aiohttp
import inspect



class Test:

    def __init__(self):
        self.scn = self.test

    async def test(self):
        await asyncio.sleep(2)
        print('выспался')
    def t2(self):
        print(await self.scn())

obj = Test()
obj.t2()

# print((getattr(controller_management.Oids, 'swarcoUTCDetectorQty')).name)





if __name__ == '__main__':
    pass
    # start_time = time.time()
    # asyncio.run(main())
