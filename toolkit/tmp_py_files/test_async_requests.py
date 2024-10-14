import asyncio
import logging
from engineering_tools import settings
import textwrap
import time

import aiohttp

from toolkit.sdp_lib import controller_management

ip = '10.179.107.129'
ip3 = '10.179.86.209'
ip2 = '10.45.154.12'
ip4 = '10.45.154.11'

logger = logging.getLogger(__name__)

h1 = controller_management.PeekUG405(ip, scn='')
res = asyncio.run(h1.get_utcType2VendorID())

logger.debug(res)


