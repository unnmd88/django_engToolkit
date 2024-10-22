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

h1 = controller_management.PotokP('10.45.154.11')
res = asyncio.run(h1.get_scn())
print(res)

