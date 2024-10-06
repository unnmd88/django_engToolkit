import asyncio
import time
from typing import *

from toolkit.sdp_lib import conflicts, controller_management

import requests
import aiohttp

url_inputs = 'http://10.179.107.129/hvi?file=cell1020.hvi&pos1=0&pos2=40'


session = requests.Session()

# host1 = controller_management.PotokS('10.45.154.11', '1')
#
# url='http://10.179.107.129/hvi?file=data.hvi&page=cell6710.hvi,'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
  }

data = {'par_name': 'PARM.R1/1', 'par_value': '0'}

cookies = {'uic': '3333'}


# resp1 = session.post(headers=headers, url='http://10.179.107.129/hvi?file=data.hvi&page=cell6710.hvi,',
#                      data={'par_name': 'PARM.R1/1', 'par_value': '0'}, cookies=cookies)
#
# print(resp1.text)


async def collect_data(session, url, params):
    print(f"Starting task: {url}")
    async with session.get(url,  data=data) as response:
        await asyncio.sleep(1)  # Simulating a delay
        data1 = await response.text()
        print(f"Completed task: {url}")
        return data1


async def fetch_data(session, url):
    print(f"Starting task: {url}")
    async with session.post(url,  data=data) as response:
        await asyncio.sleep(1)  # Simulating a delay
        data1 = await response.text()
        print(f"Completed task: {url}")
        return data1


def parse_inputs(data):
    pass



async def main(ip_adress: str,
               params_type: str,
               params: dict[str, str]
               ):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    }

    data = {'par_name': 'PARM.R1/1', 'par_value': '0'}

    cookies = {'uic': '3333'}

    if params_type == ''
    url_inputs = f'http://{ip_adress}/hvi?file=cell1020.hvi&pos1=0&pos2=40'
    url_user_parameters = f'http://{ip_adress}/hvi?file=cell6710.hvi&pos1=0&pos2=24'

    urls_test = [
        'http://10.179.107.129/hvi?file=data.hvi&page=cell6710.hvi',
        'http://10.179.105.225/hvi?file=data.hvi&page=cell6710.hvi'
    ]


    with requests.Session() as session:
        response1 = session.get(url=url_inputs, headers=headers, cookies=cookies, timeout=1)
        print(f'response1: {response1.text}')

    timeout = aiohttp.ClientTimeout(2)
    async with aiohttp.ClientSession(headers=headers, cookies=cookies, timeout=timeout) as session:

        responce = session.get(url_inputs)
        print(f'responce: {responce}')

        print(responce.text())

        tasks = [fetch_data(session, url) for url in urls_test]
        print(f'tasks: {tasks}')
        results = await asyncio.gather(*tasks)
        print(f'res: {results}')




async def set_stage(value):







if __name__ == '__main__':
    start_time = time.time()
    asyncio.run(main('10.45.154.19'))
    print(f"Total time taken: {time.time() - start_time} seconds")