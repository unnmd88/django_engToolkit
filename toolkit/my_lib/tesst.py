import asyncio
import os
import socket
import sys

import requests

from pysnmp.hlapi.asyncio import *


import requests
# import fake_useragent

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
           }

login_data = {
    'name': 'uic',
    'value': '3333',
}
# session = requests.Session()
# session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'})
# session.headers.update(headers)

community = 'private'
ip_adress = '10.179.8.113'
swarcoUTCTrafftechPhaseCommand = '1.3.6.1.4.1.1618.3.7.2.11.1.0'
swarcoUTCTrafftechPhaseStatus = '1.3.6.1.4.1.1618.3.7.2.11.2.0'

async def run():
    errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip_adress, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(swarcoUTCTrafftechPhaseCommand), Unsigned32(0))
    )
    print(errorIndication, errorStatus, errorIndex, varBinds)
asyncio.run(run())


async def run():
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip_adress, 161)),
        ContextData(),
        ObjectType(ObjectIdentity(swarcoUTCTrafftechPhaseStatus),)
    )
    print(errorIndication, errorStatus, errorIndex, varBinds)
    for oid, val in varBinds:
        print(f'{oid.prettyPrint()} = {val.prettyPrint()}')
asyncio.run(run())

# print(response.content)

print(sys.platform)


