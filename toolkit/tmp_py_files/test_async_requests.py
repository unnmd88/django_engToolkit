import asyncio
import textwrap
import time

import aiohttp

from toolkit.sdp_lib import controller_management

ip = '10.179.107.129'
ip3 = '10.179.86.209'
ip2 = '10.45.154.12'
ip4 = '10.45.154.11'

# h1 = controller_management.PeekWeb(ip2)
#
# res = asyncio.run(h1.main_async2('USER_PARAMETERS',
#                                  None,
#                                  ))

# h2 = controller_management.PotokP(ip3, scn='CO4840')
# print(f'dd 2: {asyncio.run(h2.get_potok_utcReplyPlanStatus())}')

# h3 = controller_management.PotokS(ip4)
# print(f'dd 3: {asyncio.run(h3.get_stage())}')

try:
    potok12 = controller_management.PotokP(ip2, scn='CO1111')
    print(';2')
except Exception as err:
    print(f'err: {err}')


counts = set()
while True:

    res = asyncio.run(potok12.get_utcReplyVSn())
    print(f'res: <{res[0]}>')
    try:
        splited_string = textwrap.wrap(res[0], 2)
        print(f'splited_string: {splited_string}')
        print(f'len splited_string: {len(splited_string)}')
        counts.add(len(splited_string))
        print(f'counts: {counts}')

    except:
        pass


    time.sleep(1)
# print(controller_management.BaseUG405.convert_scn('CO1111'))

