import asyncio
from toolkit.sdp_lib import controller_management

import logging


ip = '10.179.107.129'
ip2 = '10.45.154.11'
ip3 = '10.45.154.19'
ip4 = '10.179.22.129'
ip5 = '10.179.19.81'
ip6 = '10.179.63.57'




# h1 = controller_management.PeekUG405(ip3)
# res = asyncio.run(h1.get_utcReplyGn())
# res = asyncio.run(h1.get_utcReplyGn())
# res = asyncio.run(h1.get_utcType2OperationMode())
# res = asyncio.run(h1.set_stage('2'))



# h2 = controller_management.SwarcoSTCIP(ip5, num_host=23)
# res = asyncio.run(h2.set_allred('0'))


# h2 = controller_management.PotokS(ip2, num_host=23)
# res = asyncio.run(h2.set_restartProgramm('1'))


logger = logging.getLogger(__name__)
h6 = controller_management.PotokP(ip2)
# asyncio.run(h6.get_utcControlFn())
# print(h6.scn)
res = asyncio.run(h6.set_stage(31))
import math
# for r in res:
#     print(f'r: {r}')
print(res)

res = asyncio.run(h6.get_stage())
print(f'res2: {res}')


