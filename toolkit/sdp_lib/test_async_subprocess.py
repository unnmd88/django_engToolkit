from sys import argv
import asyncio

from pysnmp.hlapi.asyncio import *


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
swarcoUTCSignalGroupState = '.1.3.6.1.4.1.1618.3.5.2.1.6.0'
swarcoUTCSignalGroupOffsetTime = '.1.3.6.1.4.1.1618.3.5.2.1.3.0'

# print('я subprocess')
# print('я subprocess2')
# print('я subprocess3')
# print(f'argv: {argv[1]}')



async def get_data_frozen_controller(ip_adress, timeout=0, retries=0):
    # print('Перед await')
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        SnmpEngine(),
        CommunityData('public'),
        UdpTransportTarget((ip_adress, 161), timeout=timeout, retries=retries),
        ContextData(),
        ObjectType(ObjectIdentity(swarcoUTCSignalGroupState),),
        ObjectType(ObjectIdentity(swarcoUTCSignalGroupOffsetTime),),
    )
    # print('Перед return')
    if varBinds:
        return f'{ip_adress},{varBinds[0][1].prettyPrint()},{varBinds[1][1].prettyPrint()};'
    return f'{ip_adress},null;'

    return f'{ip_adress}:{varBinds};'


async def main(hosts):

    # print(f'hosts --- > {hosts}')
    tasks = []
    for i, host in enumerate(hosts):
        tasks.append(asyncio.create_task(get_data_frozen_controller(host)))

    values = await asyncio.gather(*tasks)
    # print(values)
    # print(f'values subproces = {values}')
    # val = "|".join(values)
    # val = val.replace("|")
    # print(f'type values subproces = {"".join(values)}')
    print(f'{"".join(values)}')
    return values


# asyncio.run(main(['10.179.20.137', '10.179.116.1', '10.179.64.97']))
asyncio.run(main(hosts=argv[1].split(',')))
