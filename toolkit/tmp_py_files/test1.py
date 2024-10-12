import toolkit.sdp_lib as sdp_lib
import os

from dotenv import load_dotenv

load_dotenv()

DEBUG = True if os.getenv('DEBUG') in ('1', 'True') else False

print(DEBUG)

stg_mask = ['01', '02', '04', '08', '10', '20', '40', '80']
# stgs = (f'{i}{j * "00"}' for j in range(8) for i in stg_mask)
stages = {k: v for k, v in enumerate((f'{i}{j * "00"}' for j in range(8) for i in stg_mask), 1)}
# print(stgs)
print(stages)


