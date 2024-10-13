import asyncio
from toolkit.sdp_lib import controller_management

import logging


ip = '10.179.42.121'
ip2 = '10.45.154.11'
ip3 = '10.45.154.19'

# h1 = controller_management.PeekUG405(ip)
# res = asyncio.run(h1.get_utcReplyGn())
# print(f'res : {res}')
# res = asyncio.run(h1.get_utcType2OperationMode())
# print(f'res : {res}')
# res = asyncio.run(h1.set_stage('1'))

print(f'res : {res}')



# h2 = controller_management.SwarcoSTCIP(ip5, num_host=23)
# res = asyncio.run(h2.set_allred('0'))


# h2 = controller_management.PotokS(ip2, num_host=23)
# res = asyncio.run(h2.set_restartProgramm('1'))


logger = logging.getLogger(__name__)
# h6 = controller_management.PotokP(ip2)
# asyncio.run(h6.get_utcControlFn())
# print(h6.scn)

import math
# for r in res:
#     print(f'r: {r}')


# res = asyncio.run(h6.set_restartProgramm())
# print(res)

# res = asyncio.run(h6.get_flash())
# print(f'eres2: {res}')
# print(controller_management.PeekUG405.val_stages_UG405_peek('set'))
# print('-------------------')
# print(controller_management.PotokP.make_val_stages_for_get_stage_UG405_potok('set'))

