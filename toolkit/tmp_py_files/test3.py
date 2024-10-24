import logging
import os
import functools
import asyncio, asyncssh, sys
import textwrap
import time
from engineering_tools import settings
import aiohttp
from enum import Enum

import pyautogui

from toolkit.sdp_lib import controller_management
from datetime import datetime

logger = logging.getLogger(__name__)

from toolkit.sdp_lib import controller_management
from dotenv import load_dotenv
load_dotenv()


start_time = time.time()
h1 = controller_management.AsyncSwarcoSsh(ip_adress='10.45.154.19')
h2 = controller_management.PotokP('10.45.154.12')
h3 = controller_management.SwarcoSTCIP('10.179.117.97')
# async def main():
#     tasks = [asyncio.create_task(h1.set_stage('2')), asyncio.create_task(h2.set_stage('12'))]
#     await asyncio.gather(*tasks)

# res = asyncio.run(h3.get_request(get_mode=True, oids=[controller_management.Oids.swarcoUTCStatusEquipment.value,
#                                                       controller_management.Oids.swarcoUTCDetectorQty,
#                                                       controller_management.Oids.swarcoSoftIOStatus]))

res = asyncio.run(h3.set_stage('0'))

print(res)
print(h3.create_json(res[0], res[1]))

print(f'Время выполнения: {time.time() - start_time}')


# print('1111111111')
# for line in res.decode('utf-8').splitlines():
#     print('l {}'.format(line))

# async def create_proc(conn):
#     async with conn.create_process(term_type="ansi", encoding='latin-1', recv_eof=True) as proc:
#             print('create_conn')
#             response = await read_timed(proc.stdout, timeout=3, bufsize=4096)
#
# asyncio.run(create_proc(conn))

# async def create_conn():
#     async with conn.create_process(term_type="ansi", encoding='latin-1', recv_eof=True) as proc:
#         print('create_conn')
#         response = await read_timed(proc.stdout, timeout=3, bufsize=4096)





async def read_timed(stream: asyncssh.SSHReader,
                     timeout: float = 1,
                     bufsize: int = 1024) -> str:
    """Read data from a stream with a timeout."""
    ret = ''
    while True:
        try:
            ret += await asyncio.wait_for(stream.read(bufsize), timeout)
        except (asyncio.TimeoutError, asyncio.CancelledError):
            return ret

async def run_client():
    async with asyncssh.connect(host='10.45.154.16',
                                # username=os.getenv('swarco_itc_login'),
                                # password=os.getenv('swarco_itc_password'),
                                username='itc',
                                password='level1NN',
                                kex_algs="+diffie-hellman-group1-sha1",
                                encryption_algs='+aes256-cbc',
                                known_hosts=None) as conn:
        async with conn.create_process(term_type="ansi", encoding='latin-1', recv_eof=True) as proc:
            response = await read_timed(proc.stdout, timeout=3, bufsize=4096)
            proc.stdin.write('lang UK\n')
            proc.stdin.write('l2\n')
            proc.stdin.write('2727\n')
            print('Response:', response)
            for i in range(1, 4):
                if i != 2:
                    proc.stdin.write(f'inp10{i}=1\n')
            proc.stdin.write('CBMEM10 ?\n')

            response = await read_timed(proc.stdout, timeout=3, bufsize=4096)
            print('Response:', response)
            with open('log', 'w') as f:
                f.write(response)

            logger.debug(response)
            r = response.encode('iso-8859-1')
            logger.debug(r)
            r_enc = r.decode('iso-8859-1').encode('utf-8')
            logger.debug(r_enc)
            print(r)
            print(r_enc.decode('utf-8').splitlines())
            for line in r_enc.decode('utf-8').splitlines():
                print(f'line: {line}')

            return response


# async def run_client():
#     async with asyncssh.connect(host='10.45.154.16',
#                                 # username=os.getenv('swarco_itc_login'),
#                                 # password=os.getenv('swarco_itc_password'),
#                                 username='root',
#                                 password='N1eZ4pC',
#                                 kex_algs="+diffie-hellman-group1-sha1",
#                                 known_hosts=None) as conn:
#         async with conn.create_process(term_type="ansi", encoding='latin-1', recv_eof=True) as proc:
#             response = await read_timed(proc.stdout, timeout=3, bufsize=4096)
#             proc.stdin.write('ls\n')
#
#             print('Response:', response)
#             response = await read_timed(proc.stdout, timeout=3, bufsize=4096)
#             print('Response:', response)
#             with open('log', 'w') as f:
#                 f.write(response)
#             return response


# async def run_client():
#     async with asyncssh.connect(host='10.45.154.19',
#                                 # username=os.getenv('swarco_itc_login'),
#                                 # password=os.getenv('swarco_itc_password'),
#                                 username='root',
#                                 password='peek',
#                                 kex_algs="+diffie-hellman-group1-sha1",
#                                 encryption_algs='+aes256-cbc',
#                                 known_hosts=None) as conn:
#         async with conn.create_process(term_type="ansi", encoding='latin-1', recv_eof=True) as proc:
#             response = await read_timed(proc.stdout, timeout=3, bufsize=4096)
#             proc.stdin.write('ls\n')
#
#             print('Response:', response)
#             response = await read_timed(proc.stdout, timeout=3, bufsize=4096)
#             print('Response:', response)
#             with open('log', 'w') as f:
#                 f.write(response)
#             return response


# res = asyncio.run(run_client())





# loop = asyncio.new_event_loop()
# try:
#     loop.run_until_complete(run_client())
# except (OSError, asyncssh.Error) as exc:
#     sys.exit('SSH connection failed: ' + str(exc))