import asyncio
import os
import sys

import asyncssh

from toolkit.sdp_lib import controller_management
from dotenv import load_dotenv
load_dotenv()

# print(controller_management.BaseUG405.convert_scn('CO884'))
async def run_client() -> None:
    async with asyncssh.connect('10.179.19.81',
                                username=os.getenv('swarco_r_login'),
                                password=os.getenv('swarco_r_password'),
                                kex_algs="+diffie-hellman-group1-sha1",
                                known_hosts=None) as conn:

        async with conn.create_process(term_type="ansi") as process:
        #
            process.stdin.write('ls')
            print(f'3nd str')
            result = await process.stdout.readline()
        #
            return result
        #     # print(f'result: {result.decode("latin-1")}')

        # async with conn.create_process('bc') as process:
        #     process.stdin.write('itc' + '\n')
        #     res = await process.stdout.readline()
        #     print(res)

res = asyncio.run(run_client())
# asyncio.get_event_loop().run_until_complete(run_client())

print('result + ' + res)