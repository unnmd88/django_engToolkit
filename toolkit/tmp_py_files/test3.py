import logging
import os
import asyncio, asyncssh, sys
import textwrap
import time

import aiohttp
from enum import Enum

import pyautogui

from toolkit.sdp_lib import controller_management
from datetime import datetime

logger = logging.getLogger(__name__)

from toolkit.sdp_lib import controller_management
from dotenv import load_dotenv
load_dotenv()


# async def run_client() -> None:
#     async with asyncssh.connect('10.45.154.16',
#                                 username=os.getenv('swarco_r_login'),
#                                 password=os.getenv('swarco_r_password'),
#                                 kex_algs="+diffie-hellman-group1-sha1",
#                                 known_hosts=None) as conn:
#
#         async with conn.create_process(term_type="ansi") as process:
#             process.stdin.write('itc')
#             print(f'3nd str')
#             result = await process.stdout.readline()
#             return result

# res = asyncio.run(run_client())




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
                                port=22,
                                # username=os.getenv('swarco_itc_login'),
                                # password=os.getenv('swarco_itc_password'),
                                username='itc',
                                password='level1NN',
                                kex_algs="+diffie-hellman-group1-sha1",
                                known_hosts=None) as conn:
        async with conn.create_process(term_type="ansi", encoding='latin-1') as proc:
            # welcome = await read_timed(proc.stdout, timeout=1, bufsize=4096, )
            # print(welcome.encode().decode('latin-1'), end='')
            proc.stdin.write('lang UK\n')
            #
            # proc.stdin.write('itc\n')
            # proc.stdin.write('l2\n')
            # proc.stdin.write('2727\n\n')


            proc.stdin.write('CBMEM10 ?\n')



            response = await read_timed(proc.stdout, timeout=1, bufsize=4096, )
            print('Response:', response)


asyncio.run(run_client())

# loop = asyncio.new_event_loop()
# try:
#     loop.run_until_complete(run_client())
# except (OSError, asyncssh.Error) as exc:
#     sys.exit('SSH connection failed: ' + str(exc))