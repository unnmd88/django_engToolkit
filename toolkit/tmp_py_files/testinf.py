from enum import Enum

import fake_useragent
import requests
import certifi
from requests.auth import HTTPBasicAuth
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from pysnmp.hlapi.asyncio import *
import asyncio

from toolkit.sdp_lib import controller_management

h1 = controller_management.PotokS('10.45.154.17')
res = asyncio.run(h1.set_flash())
print(res)

