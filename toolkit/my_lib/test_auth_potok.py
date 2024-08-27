import lxml.html

import controller_management
import requests
import requests
from bs4 import BeautifulSoup
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# ip_addr = '10.45.154.16'
# obj = snmp_managemement_v3.SwarcoSSH(ip_addr)
# print(obj.make_any_commands())
url = 'https://10.45.154.11/'
headers = {'user-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
			 'Content-Type': 'application/x-www-form-urlencoded'}
data = {
		'login': 'admin',
		'password': 'zBCTRuV7'
		}

# session = requests.Session()
# session.get(url, headers=headers, verify=False)
# session.headers.update(headers) # обновим хедеры в сессии
#
# def get_token():# Метод, для получения токена
# 	response = session.post(url, headers=headers, verify=False)
# 	soup = BeautifulSoup(response.text, "html.parser")
# 	# print(soup)
# 	token = soup.find('input', {'name': 'csrf_token'}).get('value')
# 	print(f'token = {token}')
# 	return token # Возвращает токен
#
# def auth(): # Метод, для авторизации
# 	response = session.post(url, headers=headers, data=data, verify=False)
# 	return response.text
#
# data['csrf_token'] = 'get_token()' # Вызывает метод для получения токена, и результат заносим в словарь
#
# print(data)
#
# time.sleep(2) # Пауза 2 сек :)
# html = auth() # Авторизируемся. В html будет наш ответ после авторизации
#
# print(html)

url2 = 'https://10.45.154.11/login'
headers1 = {'user-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
}
headers2 = {'user-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
			"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7'
	}
session = requests.Session()
login = session.get(url2, verify=False)

login_html = lxml.html.fromstring(login.text)
hidden_elements = login_html.xpath('//form//input[@type="hidden"]')
form = {x.attrib['name']: x.attrib['value'] for x in hidden_elements}
form['login'] = 'operator'
form['password'] = 'operator'
print(form)
responce = session.post(url2, data=form, headers=headers2, verify=False)
print(responce.text)


