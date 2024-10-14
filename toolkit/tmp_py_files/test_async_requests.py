import asyncio
import textwrap
import time

import aiohttp

from toolkit.sdp_lib import controller_management

ip = '10.179.107.129'
ip3 = '10.179.86.209'
ip2 = '10.45.154.12'
ip4 = '10.45.154.11'


async def coro1(delay):
    print('coro1 before sleep')
    await asyncio.sleep(delay)
    print('coro1 after sleep')
    return 'done coro1'


async def coro2(delay):
    print('coro2 before sleep')
    await asyncio.sleep(delay)
    print('coro2 after sleep')
    return 'done coro2'


async def coro3(delay):
    print('coro3 before sleep')
    await asyncio.sleep(delay)
    print('coro3 after sleep')
    return 'done coro3'


async def coro4(delay):
    print('coro4 before sleep')
    await asyncio.sleep(delay)
    print('coro4 after sleep')
    return 'done coro4'


async def main():
    async with asyncio.TaskGroup() as tg:
        # res = [tg.create_task(coro1(2)) for i in range(6)]
        # print(f' res : {res}')
        # return res
        for t in range(6):
            tg.create_task(coro1(2))
        tg.create_task(coro2(2))
        tg.create_task(coro3(2))
        tg.create_task(coro4(2))

res = asyncio.run(main())
for i in res:
    print(f' i: {i.result()}')

