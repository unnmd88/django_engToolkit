import asyncio
import time

import requests
import aiohttp


session = requests.Session()



url='http://10.179.107.129/hvi?file=data.hvi&page=cell6710.hvi,'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
  }

data = {'par_name': 'PARM.R1/1', 'par_value': '0'}

cookies = {'uic': '3333'}


# resp1 = session.post(headers=headers, url='http://10.179.107.129/hvi?file=data.hvi&page=cell6710.hvi,',
#                      data={'par_name': 'PARM.R1/1', 'par_value': '0'}, cookies=cookies)
#
# print(resp1.text)



async def fetch_data(session, url):
    print(f"Starting task: {url}")
    async with session.post(url,  data=data) as response:
        await asyncio.sleep(1)  # Simulating a delay
        data1 = await response.text()
        print(f"Completed task: {url}")
        return data1


async def main():
    urls = [
        'http://10.179.107.129/hvi?file=data.hvi&page=cell6710.hvi',
        'http://10.179.105.225/hvi?file=data.hvi&page=cell6710.hvi'
    ]

    async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
        tasks = [fetch_data(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
    # for res in results:
    #     print(f'res: {res}')


if __name__ == '__main__':
    start_time = time.time()
    asyncio.run(main())
    print(f"Total time taken: {time.time() - start_time} seconds")