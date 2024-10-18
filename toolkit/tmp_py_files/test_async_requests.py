import asyncio
import logging
from engineering_tools import settings
import textwrap
import time

import aiohttp
from enum import Enum
from toolkit.sdp_lib import controller_management
from datetime import datetime
ip = '10.179.107.129'
ip3 = '10.179.86.209'
ip2 = '10.45.154.12'
ip4 = '10.45.154.11'
ip4 = '10.45.154.19'

logger = logging.getLogger(__name__)


CO2385 = '10.179.16.81'
h1 = controller_management.PeekUG405(ip2, scn='CO1111')


def convert_datetime(string):
    return (string[:4] + ':' + string[4:6] + ':' + string[6:8] + ':' + string[8:10]
            + ':' + string[10:12] + ':' + string[12:14])


while True:
    res1, res = asyncio.run(h1.get_data_scoot())
    res = [data[1].prettyPrint() for data in res]
    print(h1.scn)
    # print(len(res[1] - 2))

    if res and len(res) == 3:
        print(f'Все данные: {res}')
        print(f'Кол-во блоков: {res[0]}')
        print(f'Время ДК: {res[1]}')
        print(f'Время ДК2: {convert_datetime(res[1])}')
        print(f'Cостояние: {res[2]}')
        octet_str = res[2].replace("0x", '')
        print(f'Cостояние: {":".join([octet_str[i:i+2] for i in range(0, len(octet_str), 2)])}')
    logging.debug(res)
    time.sleep(1)

