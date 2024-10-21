import asyncio
from enum import Enum
from toolkit.sdp_lib import controller_management
from engineering_tools import settings

import logging

logger = logging.getLogger(__name__)
from toolkit.sdp_lib import controller_management

# print(controller_management.BaseUG405.convert_scn('CO381'))

async def test(par1):
    print('par1')
    await asyncio.sleep(1)
par1 = 'par1'
test(par1)

print('22222')