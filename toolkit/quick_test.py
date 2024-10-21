import asyncio
import sys
import time
from enum import Enum

from pysnmp.proto.rfc1902 import Unsigned32

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
    controller_management.Oids.swarcoUTCDetectorQty.value,

    controller_management.Oids.swarcoUTCTrafftechPhaseStatus.value,
    controller_management.Oids.swarcoUTCTrafftechPlanSource.value,
    controller_management.Oids.swarcoUTCTrafftechPlanSource.value,
    controller_management.Oids.swarcoUTCTrafftechPlanSource.value,
    controller_management.Oids.swarcoUTCTrafftechPlanSource.value,
    controller_management.Oids.swarcoUTCTrafftechPlanSource.value,
    controller_management.Oids.utcControlFF,
    controller_management.Oids.swarcoSoftIOStatus,
]



# h2 = controller_management.PotokP('10.179.102.65', host_id='Tetss1')
# errInd, varBinds = asyncio.run(h2.get_request(get_mode=True))
# h2 = controller_management.PotokS('10.179.109.41', host_id='Tetss1')
# h2 = controller_management.SwarcoSTCIP('10.179.106.89', host_id='Tetss2')
h2 = controller_management.PotokP('10.179.108.169', host_id='Tetss2')

errInd, varBinds = asyncio.run(h2.set_stage('0'))




# errInd, varBinds = asyncio.run(h2.set_request(
#     [(controller_management.Oids.swarcoUTCTrafftechPhaseCommand.value, '0')]
# ))

# oids_set = [
#     # ObjectType(ObjectIdentity(Oids.swarcoUTCTrafftechPhaseCommand.value), Unsigned32('0'))
#     (controller_management.Oids.swarcoUTCTrafftechPhaseCommand.value, Unsigned32('0')),
#     (controller_management.Oids.swarcoUTCTrafftechPhaseCommand.value, Unsigned32('0')),
#
# ]

# oids_set = {
#     controller_management.Oids.swarcoUTCTrafftechPhaseCommand.value: Unsigned32('0')
# }
# errInd, varBinds = asyncio.run(h3.set_request_base(
#     ip_adress=h3.ip_adress,
#     community='private',
#     oids=oids_set
# ))

#------------------------------------------------------------------#

# errInd, varBinds = asyncio.run(h3.get_request(get_mode=True))
# errInd, varBinds = asyncio.run(h3.set_stage('0'))
# errInd, varBinds = asyncio.run(h3.set_request({
#         controller_management.Oids.swarcoUTCTrafftechPhaseCommand: '0'
#     }))

    # [(controller_management.Oids.swarcoUTCTrafftechPhaseCommand.value, '0'),
    #  (controller_management.Oids.swarcoUTCTrafftechPlanCommand, '100')]

    # [(controller_management.Oids.swarcoUTCTrafftechPhaseCommand.value, '2')]





# async def main():
#     ip = [
#         '10.179.68.177', '10.179.58.105', '10.179.59.1', '10.179.112.233', '10.179.59.241',
#         '10.45.154.11', '10.45.154.11', '10.45.154.11', '10.45.154.11'
#     ]
#     hosts = [controller_management.PotokS(ip_) for ip_ in ip]
#     print('start')
#     start = time.time()
#     res = await asyncio.gather(*[host.get_request(get_mode=True) for host in hosts])
#     print(f'end_time = {time.time() - start}')
#     return hosts, res
# hosts, res = asyncio.run(main())
# start = time.time()
# print('start')
# for h, r in zip(hosts, res):
#     logger.debug(h.create_json(r[0], r[1]))
# print(f'end_time create_json= {time.time() - start}')



logger.debug(h2.create_json(errInd, varBinds, first_kwarg='первый kwarg', second_kw='ну а это второй'))








# res_json = h3.parse_varBinds_common(varBinds)
# res2 = h3.create_json(errInd, varBinds)
# logger.debug(res_json)
# for k, v in res_json:
#     if 'PhaseStatus' in k:
#         print(f'k: {k} ::: val: {v}, num_stage: {h3.get_val_stage.get(v)}')



