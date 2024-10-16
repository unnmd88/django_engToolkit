import asyncio
import time

from toolkit.sdp_lib import controller_management
from engineering_tools import settings

import logging

logger = logging.getLogger(__name__)

ip = '10.179.15.97'
ip2 = '10.45.154.11'
ip3 = '10.45.154.19'
ip4 = '10.179.107.129'
ip5 = '10.179.65.89'
ip6 = '10.179.72.129'

ip8 = '10.179.72.129'
CO2385 = '10.179.16.81'
swarco16 = '10.45.154.16'

# async def main():
#     start_time = time.time()
#     h1 = controller_management.SwarcoSTCIP('10.179.60.9')
#     h2 = controller_management.SwarcoSTCIP('10.179.60.33')
#     h3 = controller_management.SwarcoSTCIP('10.179.60.81')
#     h4 = controller_management.SwarcoSTCIP('10.179.118.185')
#     h5 = controller_management.SwarcoSTCIP('10.179.70.41')
#
#     tasks = [
#         h1.get_current_state(), h2.get_current_state(), h3.get_current_state(), h4.get_current_state(),
#         h5.get_current_state(),
#     ]
#
#     result = await asyncio.gather(*tasks)
#     logger.debug(f'End_time get_current_state Swarco: {time.time() - start_time}')
#     json_responce = {}
#     for item in result:
#         json_responce.update(item)
#     print(json_responce)
#     # print({k: v for k, v in result})

# h1 = controller_management.SwarcoSTCIP(ip)



# h4 = controller_management.PeekWeb(ip4)
# res = asyncio.run(h4.set_stage('2'))
# res = asyncio.run(h4.get_current_state())
# res = asyncio.run(h4.set_val_to_web_common('SET_USER_PARAMETERS', data='UTC_ON=0;FIX_TIME=1'))
# res = asyncio.run(h4.set_val_to_web_common('SET_INPUTS', data=';'.join([f'MPP_PH{i}=ВФ' for i in range(1, 9)])))


# print(f'res : {res}')
# print(f'res : {h4.parse_inps_and_user_param_content(res)}')

# h2 = controller_management.PeekWeb(ip3, host_id='Testoviy PEEK')
# res = asyncio.run(h2.get_current_state())

oids = [
    controller_management.Oids.swarcoUTCDetectorQty,
    controller_management.Oids.swarcoUTCTrafftechPhaseStatus,
    controller_management.Oids.swarcoUTCTrafftechPlanSource,
    controller_management.Oids.swarcoSoftIOStatus,
]

# h2 = controller_management.PeekWeb('10.179.16.81', host_id='Testovi')
# res = asyncio.run(h2.set_val_to_web_common('SET_INPUTS', 'MPP_FL=ВКЛ'))
# h3 = controller_management.PeekWeb(ip3)
h3 = controller_management.PotokP('10.179.60.217', scn='CO3127')
errInd, varBinds = asyncio.run(h3.get_current_state())
res_json = h3.create_json(errInd, varBinds)
# res2 = h3.create_json(errInd, varBinds)
logger.debug(res_json)
for k, v in res_json.get(h3.ip_adress).items():
    print(f'k: {k} ::: v: {v}')



# h6 = controller_management.PotokP(ip2)
# asyncio.run(h6.get_utcControlFn())


