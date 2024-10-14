import asyncio
from toolkit.sdp_lib import controller_management
from engineering_tools import settings

import logging

logger = logging.getLogger(__name__)

ip = '10.179.42.121'
ip2 = '10.45.154.11'
ip3 = '10.45.154.19'
ip4 = '10.179.107.129'
ip5 = '10.179.65.89'
ip6 = '10.179.19.81'


# h1 = controller_management.PeekUG405(ip)
# res = asyncio.run(h1.get_utcReplyGn())
# print(f'res : {res}')

h4 = controller_management.PeekWeb(ip4)
# res = asyncio.run(h4.set_stage('2'))
# res = asyncio.run(h4.set_val_to_web_common('SET_USER_PARAMETERS', data='UTC_ON=0;FIX_TIME=1'))
res = asyncio.run(h4.set_val_to_web_common('SET_INPUTS', data=';'.join([f'MPP_PH{i}=ВФ' for i in range(1, 9)])))


# print(f'res : {res}')
# print(f'res : {h4.parse_inps_and_user_param_content(res)}')



logger.debug(res)



# h6 = controller_management.PotokP(ip2)
# asyncio.run(h6.get_utcControlFn())


