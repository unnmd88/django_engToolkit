import asyncio

from toolkit.sdp_lib import controller_management

ip = '10.179.107.129'
ip2 = '10.45.154.11'
ip3 = '10.45.154.19'
ip4 = '10.179.22.129'
ip5 = '10.179.19.81'

# h1 = controller_management.PeekUG405(ip3)
# res = asyncio.run(h1.set_utcType2OperationModeTimeout())
# res = asyncio.run(h1.get_utcReplyGn())
# res = asyncio.run(h1.get_utcType2OperationMode())
# res = asyncio.run(h1.set_stage('2'))



h2 = controller_management.SwarcoSTCIP(ip5, num_host=23)
res = asyncio.run(h2.set_allred('0'))

print(res)

