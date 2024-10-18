from enum import Enum

import fake_useragent
import requests
import certifi
from requests.auth import HTTPBasicAuth
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from pysnmp.hlapi.asyncio import *
import asyncio

class Test(Enum):
    swarcoUTCTrafftechPhaseCommand = '1.3.6.1.4.1.1618.3.7.2.11.1.0'
    swarcoUTCCommandDark = '1.3.6.1.4.1.1618.3.2.2.2.1.0'
    swarcoUTCCommandFlash = '1.3.6.1.4.1.1618.3.2.2.1.1.0'
    swarcoUTCTrafftechPlanCommand = '1.3.6.1.4.1.1618.3.7.2.2.1.0'
    swarcoUTCStatusEquipment = '1.3.6.1.4.1.1618.3.6.2.1.2.0'
    swarcoUTCTrafftechPhaseStatus = '1.3.6.1.4.1.1618.3.7.2.11.2.0'
    swarcoUTCTrafftechPlanCurrent = '1.3.6.1.4.1.1618.3.7.2.1.2.0'
    swarcoUTCTrafftechPlanSource = '1.3.6.1.4.1.1618.3.7.2.1.3.0'
    swarcoSoftIOStatus = '1.3.6.1.4.1.1618.5.1.1.1.1.0'
    swarcoUTCDetectorQty = '1.3.6.1.4.1.1618.3.3.2.2.2.0'
    swarcoUTCSignalGroupState = '1.3.6.1.4.1.1618.3.5.2.1.6.0'
    swarcoUTCSignalGroupOffsetTime = '1.3.6.1.4.1.1618.3.5.2.1.3.0'

# ooidds = {
#     '1.3.6.1.4.1.1618.3.6.2.1.2.0': 'swarcoUTCStatusEquipment',
#     '1.3.6.1.4.1.1618.3.3.2.2.2.0': 'swarcoUTCDetectorQty'
# }

async def get_oids(oids):
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        SnmpEngine(),
        CommunityData('private'),
        UdpTransportTarget(('10.179.56.73', 161), timeout=2, retries=1),
        ContextData(),
        *oids
    )
    res = []
    for oid, val in varBinds:
        res.append((Test(oid.__str__()).name, val.prettyPrint()))
    return res

oids = [ObjectType(ObjectIdentity(Test.swarcoUTCStatusEquipment.value)),
        ObjectType(ObjectIdentity(Test.swarcoUTCCommandDark.value)),
        ObjectType(ObjectIdentity(Test.swarcoUTCTrafftechPlanSource.value)),
ObjectType(ObjectIdentity(Test.swarcoUTCDetectorQty.value)),
ObjectType(ObjectIdentity(Test.swarcoUTCSignalGroupState.value)),
ObjectType(ObjectIdentity(Test.swarcoUTCSignalGroupOffsetTime.value)),
        ]


res = asyncio.run(get_oids(oids))

for oid, val in res:
    # print(f'oid: {oid.prettyPrint()}')
    print(f'oid: {type(oid.__str__())}')
    print(f'val: {val}')
print(res)

