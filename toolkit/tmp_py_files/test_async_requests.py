import asyncio
import logging
from engineering_tools import settings
import textwrap
import time

import aiohttp
from enum import Enum
from toolkit.sdp_lib import controller_management

ip = '10.179.107.129'
ip3 = '10.179.86.209'
ip2 = '10.45.154.12'
ip4 = '10.45.154.11'

logger = logging.getLogger(__name__)

class A(Enum):

    TEST = 'Test'
    data = {
        1: 2,
        '3': 'pfnsp'
    }

class B(A):

    clllls = 'class B'

print(B.TEST.value)
# print(controller_management.EntityJsonResponce.statusMode.value.get('3'))