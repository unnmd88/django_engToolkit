import asyncio
import aiohttp

from toolkit.sdp_lib import controller_management

ip = '10.179.107.129'
ip2 = '10.45.154.12'

h1 = controller_management.PeekWeb(ip2)

res = asyncio.run(h1.main_async2('USER_PARAMETERS',
                                 None,
                                 ))


