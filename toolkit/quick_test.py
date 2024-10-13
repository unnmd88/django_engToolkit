import asyncio
from toolkit.sdp_lib import controller_management
from engineering_tools import settings

import logging

logger = logging.getLogger(__name__)

ip = '10.179.42.121'
ip2 = '10.45.154.11'
ip3 = '10.45.154.19'
ip4 = '10.179.65.89'


# h1 = controller_management.PeekUG405(ip)
# res = asyncio.run(h1.get_utcReplyGn())
# print(f'res : {res}')
# res = asyncio.run(h1.get_utcType2OperationMode())
# print(f'res : {res}')
# res = asyncio.run(h1.set_stage('1'))
h4 = controller_management.PeekWeb(ip4)
res = asyncio.run(h4.get_content_from_web('GET_USER_PARAMETERS'))
print(f'res : {res}')
print(f'res : {h4.parse_inps_and_user_param_content(res)}')

# logger.info('НУ НАКОНЕЦ ТО')
# res = [
#     line.split(';')[3:][0] for line in res.replace(" ", '').splitlines() if line.startswith(':D')
# ]
# print(f'res : {res}')
# mode, stage = res[6].split('(')
# parsed_data = {
#     'current_plan': res[0],
#     'current_parameter_plan': res[1],
#     'current_time': res[2],
#     'current_errors': res[3] if res[3] else None,
#     'current_state': res[4],
#     'current_mode': mode,
#     'current_stage': stage.replace(')', '')
# }

logger.debug(res)
# h2 = controller_management.SwarcoSTCIP(ip5, num_host=23)
# res = asyncio.run(h2.set_allred('0'))


# h2 = controller_management.PotokS(ip2, num_host=23)
# res = asyncio.run(h2.set_restartProgramm('1'))



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

