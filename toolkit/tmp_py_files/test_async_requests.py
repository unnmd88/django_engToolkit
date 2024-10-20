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
h1 = controller_management.PeekUG405(CO2385)


def convert_datetime(string):
    return (string[:4] + ':' + string[4:6] + ':' + string[6:8] + ':' + string[8:10]
            + ':' + string[10:12] + ':' + string[12:14])


while True:
    errInd, varBinds = asyncio.run(h1.get_request([
        controller_management.Oids.utcType2ScootDetectorCount,
        controller_management.Oids.utcType2OutstationTime,
        controller_management.Oids.utcReplyVSn
    ]))

    if varBinds:
        for vb in varBinds:
            oid = vb[0].__str__()
            val = vb[1].prettyPrint()
            if h1.scn in oid:
                oid = oid.replace(h1.scn, '')
            if controller_management.Oids(oid).name == controller_management.Oids.utcType2OutstationTime.name:
                # print(f'Время ДК2: {convert_datetime(res[1])}')
                print(f'{controller_management.Oids(oid).name}: {convert_datetime(val)}')
            if controller_management.Oids(oid).name == controller_management.Oids.utcReplyVSn.name:
                octet_str = val.replace("0x", '')
                logger.debug(octet_str)
                print(f'{controller_management.Oids(oid).name}: {":".join([octet_str[i:i+2] for i in range(0, len(octet_str), 2)])}')
                print(
                    f'{controller_management.Oids(oid).name}: {val}')
            if controller_management.Oids(oid).name == controller_management.Oids.utcType2ScootDetectorCount.name:
                print(f'{controller_management.Oids(oid).name}: {val}')
    time.sleep(3)


    # res = [data[1].prettyPrint() for data in varBinds]
    # print(h1.scn)
    # print(len(res[1] - 2))

    # if varBinds and len(res) == 3:
    #     print(f'Все данные: {res}')
    #     print(f'Кол-во блоков: {res[0]}')
    #     print(f'Время ДК: {res[1]}')
    #     print(f'Время ДК2: {convert_datetime(res[1])}')
    #     print(f'Cостояние: {res[2]}')
    #     octet_str = res[2].replace("0x", '')
    #     print(f'Cостояние: {":".join([octet_str[i:i+2] for i in range(0, len(octet_str), 2)])}')
    # logging.debug(res)
    # time.sleep(1)





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

