import time
import web_management

import snmpmanagement_v2
import os
from selenium import webdriver
import time



# host4 = web_management.PeekWeb('10.45.154.19')
# host4.session_refactor(user_parameters={'UP_0': '1'})
# PhantomJS


# host2 = snmpmanagement_v2.Potok('10.45.154.12', 'CO1111')
# print(host2.get_plan_source())
# print(host2.scn)


# host3 = snmpmanagement_v2.Potok('10.179.114.97', 'CO4523')

# print(host3)
# print(host3.scn)


# def get_det():
#     """  Возвращает номер текущего плана """
#
#
#     bad_oid = ['\n']
#
#     for i in range(4):
#         proc = os.popen(f'snmpget.exe -q -r:10.179.68.9 -v:2c -t:1 -c:private -o:.1.3.6.1.4.1.1618.3.3.2.2.2.0')
#         val = proc.readline().rstrip().replace(" ", '').replace('.', '')
#         if 'Timeout' not in val and val != bad_oid:
#             return val
#         elif i == 3:
#             return 'None'
#         elif 'Timeout' in val:
#             continue
#
# data = get_det()
# print(data)

def remove_chars(string):
    """"
        Метод удаляет последний символ строки, если он не является числом
        :param string -> строка, которую необходимо проверить
        :return string -> строка, в которой последний символ число, либо пустая строка, если нет чисел
    """

    for i in range(len(string)):
        if string[-1].isdigit():
            return string
        string = string[:-1]
        print(f'string: {string}')
    return string


print(remove_chars('1,2,3\rzj\vpvm\[\nsd,v]sd'))

