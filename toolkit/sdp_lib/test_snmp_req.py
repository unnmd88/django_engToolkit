import asyncio
import os
import socket
import subprocess
import sys
import time
import controller_management
import aiohttp
import requests

from pysnmp.hlapi.asyncio import *

import openpyxl
path = 'hosts.xlsx'

wb = openpyxl.load_workbook(path)
sheet1 = wb['Лист1']

hosts_to_check = []


for cell in sheet1['B']:
    value = cell.value
    if value is None or len(value) < 10:
        continue
    hosts_to_check.append(value)


print('сейчас будут ip')
# print(f'количество хостов = {len(hosts_to_check)}')
print(hosts_to_check)

async def main(inner_data):
    all_hosts = []
    proc1 = await asyncio.create_subprocess_exec(
                                                'test_async_subprocess.exe', f'{",".join(hosts_to_check[:30])}',
                                                stdout=asyncio.subprocess.PIPE)
    # data = await proc.stdout.readline()
    data1 = await proc1.stdout.read()
    await proc1.wait()
    line1 = data1.decode('utf-8').rstrip().replace(' ', '')
    # print(f'line:: {line1}')
    # print(f'list line:: {(line1.split(";"))}')asyncio subprocess python
    line1_r = [host_data.split(',') for host_data in (line1.split(";"))]
    # print(f'line_r:: {line1_r}')

    proc2 = await asyncio.create_subprocess_exec(
                                                'test_async_subprocess.exe', f'{",".join(hosts_to_check[30:60])}',
                                                stdout=asyncio.subprocess.PIPE)
    data2 = await proc2.stdout.read()
    await proc2.wait()
    line2 = data2.decode('utf-8').rstrip().replace(' ', '')
    line2_r = [host_data.split(',') for host_data in (line2.split(";"))]


    proc3 = await asyncio.create_subprocess_exec(
                                                'test_async_subprocess.exe', f'{",".join(hosts_to_check[60:90])}',
                                                stdout=asyncio.subprocess.PIPE)
    data3 = await proc3.stdout.read()
    await proc3.wait()
    line3 = data3.decode('utf-8').rstrip().replace(' ', '')
    line3_r = [host_data.split(',') for host_data in (line3.split(";"))]

    proc4 = await asyncio.create_subprocess_exec(
                                                 'test_async_subprocess.exe', f'{",".join(hosts_to_check[90:120])}',
                                                 stdout=asyncio.subprocess.PIPE)

    data4 = await proc4.stdout.read()
    await proc4.wait()
    line4 = data4.decode('utf-8').rstrip().replace(' ', '')
    line4_r = [host_data.split(',') for host_data in (line4.split(";"))]

    proc5 = await asyncio.create_subprocess_exec(
                                                 'test_async_subprocess.exe', f'{",".join(hosts_to_check[120:150])}',
                                                 stdout=asyncio.subprocess.PIPE)

    data5 = await proc5.stdout.read()
    await proc5.wait()
    line5 = data5.decode('utf-8').rstrip().replace(' ', '')
    line5_r = [host_data.split(',') for host_data in (line5.split(";"))]





    all_hosts = line1_r + line2_r + line3_r + line4_r + line5_r
    # all_hosts.append(line1_r)
    # all_hosts.append(line2_r)
    # all_hosts.append(line3_r)

    return all_hosts


    # for i, host in enumerate(inner_data):
    #     if i < 50:
    #         tasks.append(asyncio.create_task(snmp_managemement_v3.get_data_frozen_controller(host)))
    #     else:
    #         break
    #
    #
    # return


    # values = await asyncio.gather(*tasks)
    # # print(values)
    # print('3')
    # return values

# asyncio.run(main(None))
# sys.exit()

data_analyze = {k: ['', '', 0] for k in hosts_to_check}
print(f'data_analyze: {data_analyze}')

for i in range(10000000):
    # print(f'i----> {i}')
    start_time = time.time()
    result = asyncio.run(main(hosts_to_check))
    print(f'operation time = {time.time() - start_time}')
    # print(f'res = {result}')

    for host in result:
        # print(f'host из for {host}')
        # print(f'result из for {result}')
        if len(host) > 1 and host[1] != 'null':
            # ip_adress = host[0]
            ip_adress, group_state_curr, stage_curr,  = host
            # print(f'ip_adress = {ip_adress} stage_curr = {stage_curr}, group_state_curr = {group_state_curr}')
            stage_prev, group_state_prev, cnt = data_analyze.get(ip_adress)
            # print(f'stage_prev = {stage_prev} group_state_prev = {group_state_prev}, cnt = {cnt}')

            if stage_curr == stage_prev and group_state_curr == group_state_prev:

                data_analyze[ip_adress][2] += 1
            else:

                data_analyze[ip_adress][0] = stage_curr
                data_analyze[ip_adress][1] = group_state_curr
                data_analyze[ip_adress][2] = 0

            if cnt > 240:
                pass # Отправить в бот
            #
            # for oid, val in r:
            #      print(f'oid = {oid.prettyPrint()}, val = {val.prettyPrint()}, type_val = {type(val.prettyPrint())}')
        else:
            pass
    print(f'data_analyze: {data_analyze}')


# swarcoUTCSignalGroupState = '.1.3.6.1.4.1.1618.3.5.2.1.6.0'
# swarcoUTCSignalGroupOffsetTime = '.1.3.6.1.4.1.1618.3.5.2.1.3.0'
# community = 'private'
# snmp_get = 'snmpget.exe'
# snmp_set = 'snmpset.exe'
#
# start_time = time.time()
# cn = 0
# print(f'len(data_analyze) {len(hosts_to_check)}')
# for num, ip_adr in enumerate(hosts_to_check):
#     proc = os.popen(f'{snmp_get} -q -r:{ip_adr} -v:2c -t:1 -c:{community} -o:{swarcoUTCSignalGroupState}')
#     val = proc.readline().rstrip().replace(" ", '').replace('.', '')
#     # print(f'val1: {val}')
#     proc = os.popen(f'{snmp_get} -q -r:{ip_adr} -v:2c -t:1 -c:{community} -o:{swarcoUTCSignalGroupOffsetTime}')
#     val = proc.readline().rstrip().replace(" ", '').replace('.', '')
#     # print(f'val2: {val}')
#     cn = num
#     # if 'Timeout' not in val and val != bad_oid:
#     #     return val
#     # elif i == 3:
#     #     return 'None'
#     # elif 'Timeout' in val:
#     #     continue
# print(f'operation time = {time.time() - start_time}')
# print(f'cn= {cn}')