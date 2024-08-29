import asyncio
import time
import controller_management
# import tracemalloc
#
# tracemalloc.start()

import requests
from pysnmp.smi.rfc1902 import ObjectType, ObjectIdentity

from toolkit.sdp_lib import snmpmanagement_acync

class GetDataFromController:

    swarcoUTCTrafftechPhaseCommand = '1.3.6.1.4.1.1618.3.7.2.11.1.0'
    swarcoUTCCommandDark = '1.3.6.1.4.1.1618.3.2.2.2.1.0'
    swarcoUTCCommandFlash = '1.3.6.1.4.1.1618.3.2.2.1.1.0'
    swarcoUTCTrafftechPlanCommand = '1.3.6.1.4.1.1618.3.7.2.2.1.0'
    swarcoUTCStatusEquipment = '1.3.6.1.4.1.1618.3.6.2.1.2.0'
    swarcoUTCTrafftechPhaseStatus = '1.3.6.1.4.1.1618.3.7.2.11.2.0'
    swarcoUTCTrafftechPlanCurrent = '1.3.6.1.4.1.1618.3.7.2.1.2.0'
    swarcoUTCTrafftechPlanSource = '.1.3.6.1.4.1.1618.3.7.2.1.3'
    swarcoSoftIOStatus = '1.3.6.1.4.1.1618.5.1.1.1.1.0'
    swarcoUTCDetectorQty = '1.3.6.1.4.1.1618.3.3.2.2.2.0'

    protocols = ('Поток_UG405', 'Поток_STCIP', 'Swarco_STCIP', 'Peek_UG405')
    def __init__(self, ip_adress, protocol, num_host, scn):
        self.ip_adress = ip_adress
        self.protocol = protocol
        self.num_host = num_host
        self.scn = scn
        self.oids = None
        self.host = None


    def serialize_data(self):
        # print(f'serialize_data из GetDataFromController')
        if self.protocol == self.protocols[2]:
            self.host = snmpmanagement_acync.Swarco(self.ip_adress, timeout=5, retries=0)
            self.oids = [ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPhaseStatus),),
                ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPlanCurrent),),
                ObjectType(ObjectIdentity(self.swarcoUTCDetectorQty), ),
                ObjectType(ObjectIdentity(self.swarcoSoftIOStatus), ),
                ]

    async def get_data(self):
        # print(f'get_data из GetDataFromController')
        data = await self.host.get_multiple(self.oids)
        return data
############################################################


async def main(inner_data):
    protocols = ('Поток_UG405', 'Поток_STCIP', 'Swarco_STCIP', 'Peek_UG405')
    # print(inner_data)
    tasks = []
    for num_host, data in inner_data.items():
        # if num_host == 'num_hosts_in_request':
        #     num_hosts_in_request = data
        #     print(f'num_hosts_in_request: {num_hosts_in_request}')
        #     continue
        # print(f'num_host: {num_host}')
        data = data.split(';')
        if len(data) != 3:
            continue
        ip_adress, protocol, scn = data
        if protocol != protocols[3]:
            oids, community = snmp_managemement_v3.create_oids(protocol, scn)
            tasks.append(snmp_managemement_v3.get_data_for_toolkit_snmp(ip_adress, community, num_host, protocol, oids))
        else:
            tasks.append(snmp_managemement_v3.get_data_for_toolkit_http_peek(ip_adress, num_host))



    start_time = time.time()
    values = await asyncio.gather(*tasks)

    print(f'operation time = {time.time() - start_time}')


    # print(values)
    # await asyncio.create_task(test())
    return values

res = asyncio.run(main(
    {'6': '192.168.0.1;Swarco_STCIP;CO4',
'7': '192.168.0.1;Swarco_STCIP;CO4',
'8': '192.168.0.1;Swarco_STCIP;CO4',
'9': '192.168.0.1;Swarco_STCIP;CO4',
'10': '192.168.0.1;Swarco_STCIP;CO4',
'103': '10.179.92.193;Peek_UG405;CO4',
'11': '192.168.0.1;Swarco_STCIP;CO4',
'12': '192.168.0.1;Swarco_STCIP;CO4',

'122': '10.179.78.49;Peek_UG405;CO4',
'13': '192.168.0.1;Swarco_STCIP;CO4',
'14': '192.168.0.1;Swarco_STCIP;CO4',
     '1': '10.179.102.161;Swarco_STCIP;CO1',
     '4': '10.179.118.161;Swarco_STCIP;CO4',
'15': '10.179.119.81;Поток_UG405;CO4086',
'128': '10.179.85.105;Поток_UG405;CO221',




     'num_hosts_in_request': '2',
     '_': '1723120450273'}))


start_time = time.time()
print(res)


print(snmp_managemement_v3.processing_data_toolkit(res))

print(f'serialize time = {time.time() - start_time}')
# print(res)







# async def main():
#     s = snmpmanagement_acync.Swarco('sssss')
#     values = await asyncio.gather(s.get_test2(), s.get_test2(), s.get_test2(), s.get_test2())
#
#     print(f'values: {values}')
#
# asyncio.run(main())
