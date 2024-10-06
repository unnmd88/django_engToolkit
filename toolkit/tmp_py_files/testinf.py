import fake_useragent
import requests
import certifi
from requests.auth import HTTPBasicAuth
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
  }
#
# variable = requests.session()

payload = {'file': 'dummy.hvi', 'uic': '3333'}

session.get(url='http://10.179.107.129/', headers=headers)
session.get(url='http://10.179.107.129/hvi?file=dummy.hvi&uic=3333')
resp1 = session.get(url='http://10.179.107.129/hvi?file=sysinfo.hvi&pos1=0&pos2=-1')
print(f'resp1: {resp1.text}')
resp2 = session.get(url='http://10.179.107.129/hvi?file=cell1020.hvi&pos1=0&pos2=40')

r = resp2.content.decode("utf-8")
print(f'type(r): {r}')


inps = (line.split(';') for line in r.splitlines() if line.startswith(':D'))
print(f'inps: {inps}')

def get_inputs(content):
    inputs = (line.split(';')[1:] for line in content.splitlines() if line.startswith(':D'))
    for inp in inputs:
        yield inp

for inps1 in get_inputs(resp2.content.decode("utf-8")):
    ind, num, name, cur_val, time, actuator_val = inps1
    print(f'inps1: {inps1}')
    if name.startswith('MPP'):
        # session.post(url='http://10.179.107.129/hvi?file=data.hvi&page=cell1020.hvi,',
        #              data={'par_name': f'XIN.R20/14', 'par_value': '2'},
        #              )
        session.post(url='http://10.179.107.129/hvi?file=data.hvi&page=cell1020.hvi,',
                     data=[('par_name', 'XIN.R20/10'), ('par_value', '2'),
                           ('par_name', 'XIN.R20/11'), ('par_value', '2')]
                     )



        # session.post(url='http://10.179.107.129/hvi?file=data.hvi&page=cell1020.hvi,',
        #              data={'par_name': f'XIN.R20/{ind}', 'par_value': '0'})
        # if cur_val != '-':
        #     session.post(url='http://10.179.107.129/hvi?file=data.hvi&page=cell1020.hvi,',
        #                  data={'par_name': f'XIN.R20/{ind}', 'par_value': '0'})
        # if cur_val == '1' and actuator_val == '-':
        #     session.post(url='http://10.179.107.129/hvi?file=data.hvi&page=cell1020.hvi,',
        #                                   data={'par_name': f'XIN.R20/{ind}', 'par_value': '0'})


resp1 = session.post(url='http://10.45.154.19/hvi?file=data.hvi&page=cell6710.hvi,',
                     data={'par_name': 'PARM.R1/2', 'par_value': '0'})


print(f'resp1: {resp1}')

# api_token = "IjdiODQyZDk3NzdmMmM0OWRmZGJhM2NhMGE1MzhjMjdhOTMzMzliZGUi.XJJhgg.LUbE1BpSkYV1jfQkpry4pVOJTrI"
# response = variable.get("https://192.168.45.13/login", verify=False, auth=("admin",api_token))
#
# data = {"login":"admin",
#         "password":"zBCTRuV7",
#         "X-Amzn-Trace-Id":"IjdiODQyZDk3NzdmMmM0OWRmZGJhM2NhMGE1MzhjMjdhOTMzMzliZGUi.XJJhgg.LUbE1BpSkYV1jfQkpry4pVOJTrI"}
#
#
# response = variable.post("https://192.168.45.13/login", verify=False, headers=headers, data=data)
# url = 'https://192.168.45.18/index'
# user_agent_val = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
# session = requests.Session()
# r = session.get(url, headers = {
#     'User-Agent': user_agent_val,
#
# })
# session.headers.update({'Referer':url})
# session.headers.update({'User-Agent':user_agent_val})
# _xsrf = session.cookies.get('_xsrf', domain="https://192.168.45.18/index")
# tok = 'IjkwOWMwZDY3OWYzMDgwODNmMzI5YzgwOWY3Zjk2OGI3YzVlY2FkYjIi.XJazKg.T0gAoC3bOEZBv5n5Im0M5BtSK2Y'
# post_request = session.post(url, {
#      'backUrl': 'https://192.168.45.18/index',
#      'login': 'admin',
#      'password': 'zBCTRuV',
#      '_xsrf':_xsrf,
#      'remember':'yes',
#      'csrftoken': tok,
# })
# print(post_request.text)





# from requests.auth import AuthBase
#
# class PizzaAuth(AuthBase):
#     """Присоединяет HTTP аутентификацию к объекту запроса."""
#     def __init__(self, username):
#         # здесь настроем любые данные, связанные с аутентификацией
#         self.username = 'admin'
#         self.password = 'zBCTRuV'
#
#     def __call__(self, req):
#         # изменяем и возвращаем запрос
#         req.headers['X-Pizza'] = self.username
#         return req
#
# requests.get('https://192.168.45.18/index', auth=PizzaAuth('superken'))



# user_agent_val = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
#
# url_potok = 'https://192.168.45.18/login'
# url_swarco = 'http://192.168.45.13/cgi-bin/web.cgi'
# user = fake_useragent.UserAgent().random
#
# header = {
#     'user-agent': user
# }
#
# tok = 'IjkwOWMwZDY3OWYzMDgwODNmMzI5YzgwOWY3Zjk2OGI3YzVlY2FkYjIi.XJazKg.T0gAoC3bOEZBv5n5Im0M5BtSK2Y'
#
# datas_potok = {"login":"admin", "password":"zBCTRuV"}
# s = requests.Session()
# datas_swarco = {"loginUsername":"admin", "password":"changeME1"}
#
# responce = session.post(url_swarco, data=datas_swarco, headers=header).text
# # print(responce)
#
# lnk = 'http://192.168.45.13/cgi-bin/web.cgi?pageid=page'
# resp2 = session.get(lnk, headers=header).text
# print(resp2)
#
# r = s.get(url_potok, auth=HTTPBasicAuth('3', '4'), verify=False, stream=True).text
# print(r)