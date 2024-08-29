import asyncio
import os
import socket
import subprocess
import sys

import aiohttp
import requests

from pysnmp.hlapi.asyncio import *
from toolkit.sdp_lib.configuration import auth, path_snmpget, path_snmpset


# snmp_get = path_snmpget
# snmp_set = path_snmpset

# try:
#     community_swarco, community_peek = auth('snmp')
#     print('norm')
# except:
#     community_swarco, community_peek = 'pass', 'pass'
#     pass


class AllProtocols:
    snmp_get = path_snmpget
    snmp_set = path_snmpset

    msg_bad_request = 'Request failed'
    shell_source = 'by_shell'
    pysnmp_source = 'by_pysnpm'

    # statusMode = {
    #     '8': 'Адаптивный',
    #     '10': 'Ручное управление',
    #     '11': 'Удалённое управление',
    #     '12': 'Фиксированный',
    # }

    statusMode = {
        '8': 'Адаптивный',
        '10': 'Ручное управление',
        '11': 'Удалённое управление',
        '12': 'Фиксированный',
        '00': 'Ошибка электрической цепи',
        '--': 'Нет данных',
    }

    def __init__(self, ip_adress, timeout=1, retries=1, source=shell_source):
        """
        :param ip_adress: ip контроллера
        :param timeout: таймаут запроса get/set
        :param retries: кол-во попыток запроса get/set
        :param source:
                      'shell' -> get/set из оболочки(snmpset/snmpget)
                      'pysnmp' -> get/set из библиотеки pysnmp
        """
        self.ip_adress = ip_adress
        self.timeout = timeout
        self.retries = retries
        self.source = source

    """****************** Different functions ******************"""

    def convert_scn(self, scn):
        """ Функция получает на вход строку, которую необходимо конвертировать в SCN
            для управления и мониторинга по протоколу UG405.
            Например: convert_scn(CO1111)
        """
        len_scn = str(len(scn)) + '.'
        convert_to_ASCII = [str(ord(c)) for c in scn]
        scn = f'.1.{len_scn}{".".join(convert_to_ASCII)}'
        return scn

    def check_host_tcp(self, ip_adress: str, port=80, timeout=2):
        """ Функция проверят наличие связи через socket с хостом.
            При наличии свзяи возвращает True, при отсутствии
            связи пишет в лог ошибку и возвращает False
            :return True or False
        """
        try:
            socket.setdefaulttimeout(timeout)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((ip_adress, port))
        except OSError as error:
            return False
        else:
            return True


class Swarco(AllProtocols):
    community = 'private'
    # Ключи значения фаз для get запросов STCIP Swarco
    get_val_stage_STCIP_swarco = {'2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '1': 8}
    # Ключи значения фаз для set запросов STCIP Swarco
    set_stage_STCIP_swarco_values = {'1': '2', '2': '3', '3': '4', '4': '5',
                                     '5': '6', '6': '7', '7': '8', '8': '1',
                                     'ЛОКАЛ': '0'}
    # Ключи oid STCIP Swarco
    swarcoUTCTrafftechPhaseCommand = '1.3.6.1.4.1.1618.3.7.2.11.1.0'
    swarcoUTCCommandDark = '1.3.6.1.4.1.1618.3.2.2.2.1.0'
    swarcoUTCCommandFlash = '1.3.6.1.4.1.1618.3.2.2.1.1.0'
    swarcoUTCTrafftechPlanCommand = '1.3.6.1.4.1.1618.3.7.2.2.1.0'
    swarcoUTCStatusEquipment = '1.3.6.1.4.1.1618.3.6.2.1.2.0'
    swarcoUTCTrafftechPhaseStatus = '1.3.6.1.4.1.1618.3.7.2.11.2.0'
    swarcoUTCTrafftechPlanCurrent = '1.3.6.1.4.1.1618.3.7.2.1.2.0'
    swarcoUTCTrafftechPlanSource = '.1.3.6.1.4.1.1618.3.7.2.1.3'
    swarcoSoftIOStatus = '1.3.6.1.4.1.1618.5.1.1.1.1.0'
    swarcoUTCDetectorQty = '1.3.6.1.4.1.1618.3.3.2.2.2.0'

    # oid для STCIP Swarco
    # oids_STCIP_SWARCO = {swarco_swarcoUTCTrafftechPhaseStatus: '1.3.6.1.4.1.1618.3.7.2.11.2.0',
    #                      swarco_swarcoUTCTrafftechPlanCurrent: '1.3.6.1.4.1.1618.3.7.2.1.2.0',
    #                      swarco_swarcoUTCTrafftechPhaseCommand: '1.3.6.1.4.1.1618.3.7.2.11.1.0',
    #                      swarco_swarcoUTCCommandDark: '1.3.6.1.4.1.1618.3.2.2.2.1.0',
    #                      swarco_swarcoUTCCommandFlash: '1.3.6.1.4.1.1618.3.2.2.1.1.0',
    #                      swarco_swarcoUTCTrafftechPlanCommand: '1.3.6.1.4.1.1618.3.7.2.2.1.0',
    #                      swarco_swarcoUTCStatusEquipment: '1.3.6.1.4.1.1618.3.6.2.1.2.0'}

    """ GET REQUEST """


    async def get_stage(self):
        print(f'async get_stage для {self.ip_adress}')
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
                   SnmpEngine(),
                   CommunityData(self.community),
                   UdpTransportTarget((self.ip_adress, 161), timeout=self.timeout, retries=self.retries),
                   ContextData(),
                   ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPhaseStatus), )
               )
        for oid, val in varBinds:
            val = val.prettyPrint()
            if val.isdigit:
                print(f'return {self.ip_adress}')
                return self.get_val_stage_STCIP_swarco.get(val)
        print(f'return {self.ip_adress}')
        return 'DDDD'

    async def get_plan(self):
        print(f'async get_plan')
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
                   SnmpEngine(),
                   CommunityData(self.community),
                   UdpTransportTarget((self.ip_adress, 161), timeout=self.timeout, retries=self.retries),
                   ContextData(),
                   ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPlanCurrent), )
               )
        for oid, val in varBinds:
            val = val.prettyPrint()
            if val.isdigit:
                return val

    async def get_plan_source(self):
        print(f'async get_plan_source')
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
                   SnmpEngine(),
                   CommunityData(self.community),
                   UdpTransportTarget((self.ip_adress, 161), timeout=self.timeout, retries=self.retries),
                   ContextData(),
                   ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPlanSource), )
               )
        for oid, val in varBinds:
            val = val.prettyPrint()
            if val.isdigit:
                return val

    # def get_plan(self):
    #     """  Возвращает номер текущего плана """
    #
    #     oid = self.swarcoUTCTrafftechPlanCurrent
    #     bad_oid = ['\n']
    #
    #     for i in range(4):
    #         proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
    #         val = proc.readline().rstrip().replace(" ", '').replace('.', '')
    #         if 'Timeout' not in val and val != bad_oid:
    #             return val
    #         elif i == 3:
    #             return 'None'
    #         elif 'Timeout' in val:
    #             continue

    # def get_plan_source(self):
    #     """
    #     Возвращает источник плана:
    #
    #     PlanSource (INTEGER)
    #     trafficActuatedPlanSelectionCommand(1),
    #     currentTrafficSituationCentral(2),
    #     controlBlockOrInput(3),
    #     manuallyFromWorkstation(4),
    #     emergencyRoute(5),
    #     currentTrafficSituation(6),
    #     calendarClock(7),
    #     controlBlockInLocal(8),
    #     forcedByParameterBP40(9),
    #     startUpPlan(10),
    #     localPlan(11),
    #     manualControlPlan(12)
    #     """
    #     """  Возвращает номер текущего плана """
    #
    #     oid = self.swarcoUTCTrafftechPlanSource
    #     bad_oid = ['\n']
    #
    #     for i in range(4):
    #         proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
    #         val = proc.readline().rstrip().replace(" ", '').replace('.', '')
    #         if 'Timeout' not in val and val != bad_oid:
    #             return val
    #         elif i == 3:
    #             return 'None'
    #         elif 'Timeout' in val:
    #             continue

    def get_status(self):
        """Возвращает значение "swarcoUTCStatusEquipment" (INTEGER):
            noInformation(0),
            workingProperly(1),
            powerUp(2),
            dark(3),
            flash(4),
            partialFlash(5),
            allRed(6)
        """

        oid = self.swarcoUTCStatusEquipment
        bad_oid = ['\n']

        for i in range(4):

            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')

            val = proc.readline().rstrip().replace(" ", '').replace('.', '')
            if 'Timeout' not in val and val != bad_oid:
                return val
            elif i == 3:
                return 'None'
            elif 'Timeout' in val:
                continue

    def get_dark(self):
        """ Возвращает значение  swarcoUTCCommandDark (INTEGER):
             commandDarkNormal(0),
             commandDarkTimed(1),
             commandDarkPermanent(2) --> вкл. режим ОС(18 план)
         """

        oid = self.swarcoUTCCommandDark
        bad_oid = ['\n']

        for i in range(4):
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
            val = proc.readline().rstrip().replace(" ", '').replace('.', '')
            if 'Timeout' not in val and val != bad_oid:
                return val
            elif i == 3:
                return 'None'
            elif 'Timeout' in val:
                continue

    def get_flash(self):
        """ Возвращает значение  swarcoUTCCommandFlash (INTEGER):
            commandFlashNormal(0),
            commandFlashTimed(1),
            commandFlashPermanent(2) --> вкл. режим ЖМ(17 план)
        """

        oid = self.swarcoUTCCommandFlash

        for i in range(4):
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
            val = proc.readline().rstrip().replace(" ", '').replace('.', '')
            if 'Timeout' not in val:
                return val
            elif i == 3:
                return 'None'
            elif 'Timeout' in val:
                continue

    async def get_softinputs(self):
        """
            Возвращает текущее состояние софт входов
        """

        print(f'async get_softinputs для {self.ip_adress}')
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
                   SnmpEngine(),
                   CommunityData(self.community),
                   UdpTransportTarget((self.ip_adress, 161), timeout=self.timeout, retries=self.retries),
                   ContextData(),
                   ObjectType(ObjectIdentity(self.swarcoSoftIOStatus), )
               )
        for oid, val in varBinds:
            val = val.prettyPrint()
            if val.isdigit:
                print(f'return {self.ip_adress}')
                return val
        print(f'return {self.ip_adress}')
        return 'DDDD'

    async def get_sum_det(self):
        """
            Возвращает количество дет логик
         """

        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
                   SnmpEngine(),
                   CommunityData(self.community),
                   UdpTransportTarget((self.ip_adress, 161), timeout=self.timeout, retries=self.retries),
                   ContextData(),
                   ObjectType(ObjectIdentity(self.swarcoUTCDetectorQty), )
               )
        for oid, val in varBinds:
            val = val.prettyPrint()
            if val.isdigit:
                print(f'return {self.ip_adress}')
                return val
        print(f'return {self.ip_adress}')
        return 'DDDD'

    async def get_multiple(self, oids):
        print(f'get_multiple для {self.ip_adress}')
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=self.timeout, retries=self.retries),
            ContextData(),
            *oids
        )
        # for oid, val in varBinds:
        #     print(f'oid = {oid.prettyPrint()}, val = {val.prettyPrint()}')
        print(f'Перед return для {self.ip_adress}')
        return varBinds


    def get_mode(self):
        """
            Возвращает текущий режим ДК
        """
        """ '8': 'Адаптивный',
        '10': 'Ручное управление',
        '11': 'Удалённое управление',
        '12': 'Фиксированный',
        '00': 'Ошибка электрической цепи',
        '--': 'Нет данных', """

        sum_det_logic = self.get_sum_det()
        plan = self.get_plan()
        softinp181 = self.get_softinputs()[180]

        if plan == '16':
            return '11'
        elif plan == '15':
            return '10'
        elif softinp181 == '1' or sum_det_logic == '0':
            return '12'
        elif softinp181 == '0' and sum_det_logic.isdigit() and int(sum_det_logic) > 2:
            return '8'

    async def get_test(self):
        """
            Возвращает количество дет логик
         """

        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
                   SnmpEngine(),
                   CommunityData(self.community),
                   UdpTransportTarget((self.ip_adress, 161), timeout=self.timeout, retries=self.retries),
                   ContextData(),
                   ObjectType(ObjectIdentity(self.swarcoUTCDetectorQty)),
                   ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPhaseStatus)),
                   ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPlanCurrent)),
               )
        for oid, val in varBinds:
            print(f'oid: {oid.prettyPrint()}, val: {val.prettyPrint()}')
        #     val = val.prettyPrint()
        #     if val.isdigit:
        #         print(f'return {self.ip_adress}')
        #         return val
        # print(f'return {self.ip_adress}')
        # return 'DDDD'

    async def get_test2(self):
        url = 'http://10.45.154.19'
        # for attempt in range(4):
        print('staRRt')
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=4) as resp:
                    print(resp.status)
        except Exception as e:
            print(f'e: {e}')




    """ SET REQUEST """

    def set_dark(self, value='0'):
        """ Функция включает/выключает режим ОС..
            Необходимо передать ip и значение: 2 -> включить ОС, 0 -> выключить ОС.
            Если не передать значение, установит 0(выключить ОС)
        """

        oid = self.swarcoUTCCommandDark

        for i in range(2):
            os.popen(f'{self.snmp_set} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}'
                     f' -val:{value} -tp:int')

    def set_flash(self, value='0'):
        """ Функция включает/выключает режим ЖМ..
            Необходимо передать ip и значение: 2 -> включить ЖМ, 0 -> выключить ЖМ.
            Если не передать значение, установит 0(выключить ЖМ)
        """

        oid = self.swarcoUTCCommandFlash

        for i in range(2):
            os.popen(f'{self.snmp_set} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}'
                     f' -val:{value} -tp:int')

    def set_all_red(self, value='100'):
        """ Функция включает/выключает режим КК..
            Необходимо передать ip и значение: 119 -> включить КК, 100 -> выключить КК.
            По умолчанию выключает  КК -> val=100
        """

        oid = self.swarcoUTCTrafftechPlanCommand

        for i in range(2):
            os.popen(f'{self.snmp_set} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}'
                     f' -val:{value} -tp:uint')

    def set_stage(self, value: str = 'ЛОКАЛ'):
        """ Функция устанавливает set запрос фазы
            Необходимо передать ip, значение фазы в виде: "Фаза 1", "Фаза 2"..."Фаза n".
            Если не указать значение, то по умолчанию установит 0(перевод в "Локал")
        """

        if value not in self.set_stage_STCIP_swarco_values:
            return

        oid = self.swarcoUTCTrafftechPhaseCommand
        value = self.set_stage_STCIP_swarco_values.get(value)

        for i in range(2):
            os.popen(f'{self.snmp_set} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}'
                     f' -val:{value} -tp:uint')

    """ GET MODE """


class PotokS(AllProtocols):

    """
    r -> read, w -> write
    potokS_rw_Dark = 'Установить и получить состояние ОС'
    potokS_rw_YellowFlash = 'Установить и получить состояние ЖМ'
    potokS_rw_Red = 'Установить и получить режим КК'
    potokS_rw_StageCommand = 'Установить и получить фазу'
    potokS_r_Mode = 'Возвращает статусы работы ДК(КУ, РУ и др.)'
    potokS_r_ControlState = 'Возвращает статусы работы ДК(Нормальная, ОС, ЖМ, КК)'
    potokS_r_StageStatus = 'Получить текущую фазу'
    potokS_r_PlanStatus = 'Возвращает текущий план'
    potokS_w_RestartProgramm = 'Перезапуск программы'
    """

    community = 'private'
    # oid Значения фаз(получить/установить) STCIP Potok
    get_val_stage_STCIP_potok = {
        str(k): str(v) for k, v in zip(range(2, 66), range(1, 65))
    }
    set_stage_STCIP_potok_values = {
        str(k) if k < 65 else 'ЛОКАЛ': str(v) if k < 65 else '0' for k, v in zip(range(1, 68), range(2, 69))
    }
    # oid STCIP Potok
    potokS_rw_Dark = '1.3.6.1.4.1.1618.3.2.2.2.1.0'
    potokS_rw_YellowFlash = '1.3.6.1.4.1.1618.3.2.2.1.1.0'
    potokS_rw_Red = '1.3.6.1.4.1.1618.3.2.2.4.1.0'
    potokS_rw_StageCommand = '1.3.6.1.4.1.1618.3.7.2.11.1.0'
    potokS_r_Mode = '1.3.6.1.4.1.1618.3.6.2.2.2.0'
    potokS_r_ControlState = '1.3.6.1.4.1.1618.3.6.2.1.2.0'
    potokS_r_PlanSource = '.1.3.6.1.4.1.1618.3.7.2.1.3.0'
    potokS_r_PlanStatus = '1.3.6.1.4.1.1618.3.7.2.1.2.0'
    potokS_r_StageStatus = '1.3.6.1.4.1.1618.3.7.2.11.2.0'
    potokS_w_RestartProgramm = '.1.3.6.1.4.1.1618.3.2.2.3.1.0'

    plan_source = {
        '7': 'Календарный',
        '3': 'Удалённое управление'
    }



    """*******************************************************************
    ***                          GET-REQUEST                          ****   
    **********************************************************************
    """

    def get_stage(self):
        """  Возвращает номер текущей фазы """
        # community = self.community
        # print(os.getcwd())
        #
        # print(f'ip_adress из функции: {self.ip_adress}')
        # print(f'community из функции: {community}')

        oid = self.potokS_r_StageStatus
        bad_oid = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')

            val = proc.readline().rstrip().replace(" ", '').replace('.', '')
            print(f'val: {val}')
            if 'Timeout' not in val and val != bad_oid:
                return self.get_val_stage_STCIP_potok.get(val)
            elif i == 3:
                return 'None'
            elif 'Timeout' in val:
                continue

    def get_plan(self):
        """  Возвращает номер текущего плана """

        oid = self.potokS_r_PlanStatus
        bad_oid = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')

            val = proc.readline().rstrip().replace(" ", '').replace('.', '')
            if 'Timeout' not in val and val != bad_oid:
                return val
            elif i == 3:
                return 'None'
            elif 'Timeout' in val:
                continue

    def get_plan_source(self):
        """

        Возвращает причину(источник в swarco) включения плана.
        7 - по расписанию (Расписание ДК)
        3 - удаленно включили по snmp (Центр)
        return INTEGER: 1

        """

        oid = self.potokS_r_PlanSource
        bad_oid = ['\n']

        for i in range(4):
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
            val = proc.readline().rstrip().replace(" ", '').replace('.', '')
            if 'Timeout' not in val and val != bad_oid:
                return val
            elif i == 3:
                return 'None'
            elif 'Timeout' in val:
                continue

    def get_mode(self):
        """Возвращает статусы работы ДК:
            0 - нет информации
            8 - адаптива (А)
            10 - ручное управление (Р)
            11 - удаленное управление (Ц)
            12 - фикс (Ф или А)
        """

        oid = self.potokS_r_Mode
        bad_oid = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')

            val = proc.readline().rstrip().replace(" ", '').replace('.', '')
            if 'Timeout' not in val and val != bad_oid:
                return str(val)
            elif i == 3:
                return 'None'
            elif 'Timeout' in val:
                continue

    def get_status(self):
        """Возвращает статусы работы ДК: (INTEGER):
            0 - нет информации (Неизвестно)
            1 - рабочая программа (Ф или А)
            3 - ОС
            4 - ЖМ
            6 - КК
        """

        oid = self.potokS_r_StageStatus
        bad_oid = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')

            val = proc.readline().rstrip().replace(" ", '').replace('.', '')
            if 'Timeout' not in val and val != bad_oid:
                return val
            elif i == 3:
                return 'None'
            elif 'Timeout' in val:
                continue

    def get_dark(self):

        oid = self.potokS_rw_Dark
        bad_oid = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')

            val = proc.readline().rstrip().replace(" ", '').replace('.', '')
            if 'Timeout' not in val and val != bad_oid:
                return val
            elif i == 3:
                return 'None'
            elif 'Timeout' in val:
                continue

    def get_flash(self):
        """ Возвращает значение (INTEGER):
            0 - ЖМ выключить
            2 - ЖМ включить
        """

        oid = self.potokS_rw_YellowFlash
        bad_oid = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')

            val = proc.readline().rstrip().replace(" ", '').replace('.', '')
            if 'Timeout' not in val and val != bad_oid:
                return val
            elif i == 3:
                return 'None'
            elif 'Timeout' in val:
                continue

    def get_red(self):
        """ Возвращает значение (INTEGER):
            0 - КК выключить
            2 - КК включить
        """

        oid = self.potokS_rw_Red
        bad_oid = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')

            val = proc.readline().rstrip().replace(" ", '').replace('.', '')
            if 'Timeout' not in val and val != bad_oid:
                return val
            elif i == 3:
                return 'None'
            elif 'Timeout' in val:
                continue



    """*******************************************************************
    ***                          SET-REQUEST                          ****   
    **********************************************************************
    """

    def set_dark(self, value='0'):
        """ Функция включает/выключает режим ОС..
            Необходимо передать ip и значение: 2 -> включить ОС, 0 -> выключить ОС.
            Если не передать значение, установит 0(выключить ОС)
        """

        oid = self.potokS_rw_Dark

        for i in range(2):
            os.popen(f'{self.snmp_set} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}'
                     f' -val:{value} -tp:int')

    def set_flash(self, value='0'):
        """ Функция включает/выключает режим ЖМ..
            Необходимо передать ip и значение: 2 -> включить ЖМ, 0 -> выключить ЖМ.
            Если не передать значение, установит 0(выключить ЖМ)
        """

        oid = self.potokS_rw_YellowFlash

        for i in range(2):
            os.popen(f'{self.snmp_set} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}'
                     f' -val:{value} -tp:int')

    def set_all_red(self, value='0'):
        """ Функция включает/выключает режим КК..
            Необходимо передать ip и значение: 2 -> включить КК, 0 -> выключить КК.
            Если не передать значение, установит 0(выключить КК)
        """

        oid = self.potokS_rw_Red

        for i in range(2):
            os.popen(f'{self.snmp_set} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}'
                     f' -val:{value} -tp:int')

    def set_stage(self, value='ЛОКАЛ'):
        """ Функция устанавливает set запрос фазы
            Необходимо передать ip, значение фазы в виде: "Фаза 1", "Фаза 2"..."Фаза n".
            Если не указать значение, то по умолчанию установит 0(перевод в "Локал")
        """

        if value not in self.set_stage_STCIP_potok_values:
            return

        oid = self.potokS_rw_StageCommand
        value = self.set_stage_STCIP_potok_values.get(value)

        for i in range(2):
            os.popen(f'{self.snmp_set} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}'
                     f' -val:{value} -tp:uint')

    def restart_programm(self, value='1'):
        """ Функция перезапускает программу ДК..
            Необходимо передать ip, scn в виде "COxxxx"(например "СO1111".
        """

        oid = self.potokS_w_RestartProgramm

        for i in range(2):
            os.popen(f'{self.snmp_set} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}'
                     f' -val:{value} -tp:int')


class Potok(AllProtocols):
    """
        potok_w_DarkCommand = 'Включить/Выключить ОС'
        potok_w_YellowFlash = 'Включить/Выключить ЖМ'
        potok_rw_StageCommand = 'Установка фазы'
        potok_rw_AllowBitTO = 'Разрешающий бит(TO)'
        potok_rw_OperaionMode = 'Получение режимов работы ДК(OperationMode)'
        potok_rw_OperaionModeTimeout = 'Таймаут на ожидание команды(OperationModeTimeout)'
        potok_r_StageStatus = 'Получение фазы'
        potok_r_PlanStatus = 'Возвращает номер плана'
        potok_r_DarkStatus = 'Получение состояния ОС'
        potok_r_FlashStatus = 'Получение состояния ЖМ'
        potok_w_restart_programm = 'Перезапуск программы'
    """

    community = 'UTMC'
    # set_stage_UG405_potok_values = {
    #     '1': '0x01', '2': '0x02', '3': '0x04', '4': '0x08',
    #     '5': '0x10', '6': '0x20', '7': '0x40', '8': '0x80',
    #     '9': '0x0100', '10': '0x0200', '11': '0x0400', '12': '0x0800',
    #     '13': '0x1000', '14': '0x2000', '15': '0x4000', '16': '0x8000',
    #     '17': '0x010000', '18': '0x020000', '19': '0x040000', '20': '0x080000',
    #     '21': '0x100000', '22': '0x200000', '23': '0x400000', '24': '0x800000',
    #     '25': '0x01000000', '26': '0x02000000', '27': '0x04000000', '28': '0x08000000',
    #     '29': '0x10000000', '30': '0x20000000', '31': '0x40000000', '32': '0x80000000',
    #     '33': '0x0100000000', '34': '0x0200000000', '35': '0x0400000000', '36': '0x0800000000',
    #     '37': '0x1000000000', '38': '0x2000000000', '39': '0x4000000000', '40': '0x8000000000',
    #     '41': '0x010000000000', '42': '0x020000000000', '43': '0x040000000000', '44': '0x080000000000',
    #     '45': '0x100000000000', '46': '0x200000000000', '47': '0x400000000000', '48': '0x800000000000',
    #     '49': '0x01000000000000', '50': '0x02000000000000', '51': '0x04000000000000', '52': '0x08000000000000',
    #     '53': '0x10000000000000', '54': '0x20000000000000', '55': '0x40000000000000', '56': '0x80000000000000',
    #     '57': '0x0100000000000000', '58': '0x0200000000000000', '59': '0x0400000000000000', '60': '0x0800000000000000',
    #     '61': '0x1000000000000000', '62': '0x2000000000000000', '63': '0x4000000000000000', '64': '0x8000000000000000'
    # }

    # Ключи oid UG405 Potok

    @staticmethod
    def val_stages_for_get_stage_UG405_potok(option=None):
        """ В зависимости от опции функция формирует словарь с номером и значением фазы
        """
        # print(f'option: {option}')
        if option == 'get':
            mask_after_8stages_get = ['01', '02', '04', '08', '10', '20', '40', '80']
            stages = ['01', '02', '04', '08', '10', '6', '@', '80']

            # одна итерация цикла 8 фаз. В stages изначально уже лежат 8 фаз
            # поэтому range(7) -> 8 + 7 * 8 = 64. тогда range(8) -> 8 + 8 * 8, range(9) -> 8 + 9 * 8 и т.д.
            for i in range(7):
                temp_lst = [
                    f'{el}{"00" * (i + 1)}' if el != '40' else f'{el}{"00" * (i + 1)}@' for el in mask_after_8stages_get
                ]
                stages = stages + temp_lst
            # print(stages)

            get_val_stage_UG405_POTOK = {k: v for v, k in enumerate(stages, 1)}
            return get_val_stage_UG405_POTOK
            # print(get_val_stage_UG405_POTOK)
        elif option == 'set':
            mask_after_8stages_set = ['0x01', '0x02', '0x04', '0x08', '0x10', '0x20', '0x40', '0x80']
            stages = ['0x01', '0x02', '0x04', '0x08', '0x10', '0x20', '0x40', '0x80']
            for i in range(7):
                temp_lst = [
                    f'{el}{"00" * (i + 1)}' for el in mask_after_8stages_set
                ]
                stages = stages + temp_lst
            set_val_stage_UG405_POTOK = {str(k): v for k, v in enumerate(stages, 1)}
            # print(set_val_stage_UG405_POTOK)
            return set_val_stage_UG405_POTOK

    # Значения фаз для для UG405 Potok
    get_val_stage_UG405_POTOK = val_stages_for_get_stage_UG405_potok(option='get')
    set_stage_UG405_potok_values = val_stages_for_get_stage_UG405_potok(option='set')

    # oid для UG405 Potok
    potok_w_DarkCommand = '.1.3.6.1.4.1.13267.3.2.4.2.1.11'
    potok_w_FlashCommand = '.1.3.6.1.4.1.13267.3.2.4.2.1.20'
    potok_rw_StageCommand = '.1.3.6.1.4.1.13267.3.2.4.2.1.5'
    potok_rw_AllowBitTO = '.1.3.6.1.4.1.13267.3.2.4.2.1.15'
    potok_r_ManPanel_Status = '1.3.6.1.4.1.13267.3.2.5.1.1.15'
    potok_rw_OperationMode = '.1.3.6.1.4.1.13267.3.2.4.1.0'
    potok_rw_OperationModeTimeout = '.1.3.6.1.4.1.13267.3.2.2.4.0'
    potok_r_StageStatus = '.1.3.6.1.4.1.13267.3.2.5.1.1.3'
    potok_r_PlanStatus = '.1.3.6.1.4.1.13267.1.2.9.1.3'
    potok_r_PlanSource = '1.3.6.1.4.1.13267.1.2.9.1.3.1'
    potok_r_DarkStatus = '.1.3.6.1.4.1.13267.3.2.5.1.1.45'
    potok_r_FlashStatus = '.1.3.6.1.4.1.13267.3.2.5.1.1.36'
    potok_w_restart_programm = '.1.3.6.1.4.1.13267.3.2.4.2.1.5.5'
    potok_r_DetError = '1.3.6.1.4.1.13267.3.2.5.1.1.5'
    potok_r_ElectricalCircuitErr = '1.3.6.1.4.1.13267.3.2.5.1.1.16.3'
    potok_r_LocalAdaptiv = '1.3.6.1.4.1.13267.3.2.5.1.1.46'




    def __init__(self, ip_adress, scn):
        super().__init__(ip_adress)
        self.scn = self.convert_scn(scn)


    """*******************************************************************
    ***                          GET-REQUEST                          ****   
    **********************************************************************
    """

    def get_stage(self):
        """  Возвращает номер текущей фазы """

        oid = self.potok_r_StageStatus + self.scn
        stage6 = [' \n']
        bad_scn = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            # val_list = proc.stdout.readlines()
            # val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')

            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
            val_list = proc.readlines()
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
            # print(val_list)
            # print(val_string)
            if val_list != stage6 and 'Timeout' not in val_string:
                return self.get_val_stage_UG405_POTOK.get(val_string)
            elif val_list == stage6:
                return 6
            elif i == 3:
                return 'None'
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad scn'

    def get_AllowBitTO(self):

        oid = self.potok_rw_AllowBitTO + self.scn
        bad_scn = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            # val_list = proc.stdout.readlines()
            # val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')

            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
            val_list = proc.readlines()
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')

            # print(val_list)
            # print(val_string, type(val_string))
            if 'Timeout' not in val_string:
                return str(val_string)
            elif i == 3:
                return 'None'
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad scn'

    def get_manual(self):
        """
            Получение состояния управления ДК через выносную панель управления(ВПУ)
            0 -> не управляется
            1 -> управляется
        """

        oid = self.potok_r_ManPanel_Status + self.scn
        bad_scn = ['\n']

        for i in range(4):

            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
            val_list = proc.readlines()
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')

            if 'Timeout' not in val_string:
                return str(val_string)
            elif i == 3:
                return 'None'
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad scn'

    def get_plan(self):
        """  Возвращает номер текущего плана """


        oid = self.potok_r_PlanStatus + self.scn
        bad_scn = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            # val_list = proc.stdout.readlines()
            # val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')

            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
            val_list = proc.readlines()
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')

            if 'Timeout' not in val_string:
                return str(val_string)
            elif i == 3:
                return 'None'
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad scn'

    def get_plan_source(self):
        """
        Возвращает причину(источник в swarco) включения плана.
        1 - по расписанию(только оно реализовано)
        2 - удаленно включили по snmp
        """

        oid = self.potok_r_PlanSource + self.scn

        bad_scn = ['\n']

        for i in range(4):
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
            val_list = proc.readlines()
            print(f'val_list potok_r_PlanSource: {val_list}')
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
            print(f'val_string potok_r_PlanSource: {val_string}')
            if 'Timeout' not in val_string:
                return str(val_string)
            elif i == 3:
                return
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad oid'

    def get_det_err(self):
        """
        Возвращает значение аварийного состояния детекторов:
        1 -> есть авария по дет
        0 -> нет аварии по дет
        """

        oid = self.potok_r_DetError + self.scn

        bad_scn = ['\n']

        for i in range(4):
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
            val_list = proc.readlines()
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
            print(f'val_string potok_r_DetError: {val_string}')
            if 'Timeout' not in val_string:
                return str(val_string)
            elif i == 3:
                return
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad oid'

    def get_local_adaptiv(self):
        """
        Получение локальной адаптивы:
        1 -> установить локальную адаптиву
        0 ->  отключить локальную адаптиву, то есть включить локальную программу с фиксированным временем
        """

        oid = self.potok_r_LocalAdaptiv + self.scn
        bad_scn = ['\n']

        for i in range(4):
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
            val_list = proc.readlines()
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')

            if 'Timeout' not in val_string:
                return str(val_string)
            elif i == 3:
                return 'None'
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad scn'

    def get_mode(self):
        """
        Возвращает текущий режим:
        '8' -> 'Адаптивный',
        '10' -> 'Ручное управление',
        '11' -> 'Удалённое управление',
        '12' -> 'Фиксированный',
        '00' -> Failure mode(Ошибка электрической цепи)
        """
        curr_plan = self.get_plan()
        curr_plan_source = self.get_plan_source()

        if curr_plan != '0' and curr_plan_source == '1':
            if self.get_det_err() == '0' and self.get_local_adaptiv() == '1':
                return '8'
            else:
                return '12'
        elif curr_plan == '0' and curr_plan_source == '2' and self.get_AllowBitTO() == '1':
            return '11'
        elif self.get_manual() == '1':
            return '10'
        elif self.get_electrical_circuit_err() == '1':
            return '00'
        else:
            return '--'

    def get_dark(self):
        """ Возвращает значение (INTEGER):
            0 - ВЫКЛ выключен
            1 - ВЫКЛ включен
        """


        oid = self.potok_r_DarkStatus + self.scn
        bad_scn = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            # val_list = proc.stdout.readlines()
            # val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')

            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
            val_list = proc.readlines()
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')

            if 'Timeout' not in val_string:
                return val_string
            elif i == 3:
                return 'None'
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad scn'

    def get_flash(self):
        """ Возвращает значение (INTEGER):
            0 - ЖМ выключен
            1 - по рассписанию
            2 - удаленно
            3 - в ручную
            4 - аварийный
        """


        oid = self.potok_r_FlashStatus + self.scn
        bad_scn = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            # val_list = proc.stdout.readlines()
            # val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
            val_list = proc.readlines()
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')

            if 'Timeout' not in val_string:
                return val_string
            elif i == 3:
                return 'None'
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad scn'

    def get_OperationMode(self):

        oid = self.potok_rw_OperationMode
        bad_scn = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            # val_list = proc.stdout.readlines()
            # val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
            val_list = proc.readlines()
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
            # print(f'val_string: {val_string}')
            if 'Timeout' not in val_string:
                return val_string
            elif i == 3:
                return
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad oid'

    def get_OperationModeTimeout(self):

        oid = self.potok_rw_OperationModeTimeout
        bad_scn = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            # val_list = proc.stdout.readlines()
            # val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
            val_list = proc.readlines()
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
            # print(f'val_string: {val_string}')
            if 'Timeout' not in val_string:
                return val_string
            elif i == 3:
                return
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad oid'

    def get_electrical_circuit_err(self):
        """
        Получение ошибки электрических цепей ДК:
        0 -> нет ошибки
        1 -> есть ошибка
        """
        oid = self.potok_r_ElectricalCircuitErr + self.scn
        bad_scn = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            # val_list = proc.stdout.readlines()
            # val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
            val_list = proc.readlines()
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
            # print(f'val_string: {val_string}')
            if 'Timeout' not in val_string:
                return str(val_string)
            elif i == 3:
                return
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad oid'


    """*******************************************************************
    ***                          SET-REQUEST                          ****   
    **********************************************************************
    """

    def set_OperationModeTimeout(self, value='90'):
        """ Функция устанавливает таймаут  для OperationMode(Utc Control(3))
            Необходимо передать ip и значение таймаута. Если не передать значение,
            по умолчанию устанавливает 90 секунд
        """

        oid = self.potok_rw_OperationModeTimeout

        os.popen(f'{self.snmp_set} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}'
                 f' -val:{value} -tp:int')

        # subprocess.Popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}'
        #                  f' -val:{value} -tp:int')

    def set_OperationMode(self, value='3'):
        """ Функция устанавливает режим operation mode:(Standalone(1), Utc Control(3)).
            Необходимо передать ip и значение, которое необходимо установить для
            operation mode. Если значение не передать, по умолчанию установит
            Utc Control(3)
        """


        oid = self.potok_rw_OperationMode

        for i in range(2):
            os.popen(f'{self.snmp_set} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}'
                     f' -val:{value} -tp:int')
            # subprocess.Popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}'
            #                  f' -val:{value} -tp:int', shell=True)

    def set_FnBit(self, value):
        """ Функция устанавливает set запрос фазы (Fn бит)
            Необходимо передать ip, scn в виде "COxxxx"(например "СO1111",
            значение фазы в виде: "Фаза 1", "Фаза 2"..."Фаза n"
        """
        if value not in self.set_stage_UG405_potok_values:
            return

        oid = self.potok_rw_StageCommand + self.scn
        value = self.set_stage_UG405_potok_values.get(value)
        for i in range(2):
            os.popen(f'{self.snmp_set} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}'
                     f' -val:{value} -tp:hex')

    def set_AllowBitTO(self, value='1'):
        """ Функция устанавливает  значение в TO бит.
            Необходимо передать ip, scn в виде "COxxxx"(например "СO1111", значение 0 или 1.
            Если значение не передать, по умолчанию установит 1.
        """

        oid = self.potok_rw_AllowBitTO + self.scn

        for i in range(2):
            os.popen(f'{self.snmp_set} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}'
                     f' -val:{value} -tp:int')

    def set_dark(self, value='0'):
        """ Функция устанавливает  режим ОС.
            Необходимо передать ip, scn в виде "COxxxx"(например "СO1111", значение 0 или 1.
            Если значение не передать, по умолчанию установит 0.
        """


        oid = self.potok_w_DarkCommand + self.scn

        for i in range(2):
            os.popen(f'{self.snmp_set} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}'
                     f' -val:{value} -tp:int')

    def set_flash(self, value='0'):
        """ Функция устанавливает  режим ЖМ..
            Необходимо передать ip, scn в виде "COxxxx"(например "СO1111", значение 0 или 1.
            Если значение не передать, по умолчанию установит 0.
        """

        oid = self.potok_w_FlashCommand

        for i in range(2):
            os.popen(f'{self.snmp_set} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}'
                     f' -val:{value} -tp:int')

    def restart_programm(self):
        """ Функция перезапускает программу ДК..
            Необходимо передать ip, scn в виде "COxxxx"(например "СO1111".
        """

        oid = self.potok_w_restart_programm + self.scn

        for i in range(2):
            os.popen(f'{self.snmp_set} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}'
                     f' -val:1 -tp:int')

    def set_stage(self, value):
        self.set_OperationModeTimeout()
        self.set_OperationMode()
        self.set_AllowBitTO()
        self.set_FnBit(value)

    def set_local(self):
        self.set_AllowBitTO('0')
        self.set_OperationMode(value='1')


class Peek(AllProtocols):

    community = 'UTMC'

    @staticmethod
    def val_stages_for_get_stage_UG405_peek(option=None):
        """ В зависимости от опции функция формирует словарь с номером и значением фазы
        """
        # print(f'option: {option}')
        if option == 'get':
            mask_after_8stages_get = ['01', '02', '04', '08', '10', '20', '40', '80']
            stages = ['01', '02', '04', '08', '10', '6', '@', '80']

            # одна итерация цикла 8 фаз. В stages изначально уже лежат 8 фаз
            # поэтому range(7) -> 8 + 7 * 8 = 64. тогда range(8) -> 8 + 8 * 8, range(9) -> 8 + 9 * 8 и т.д.
            for i in range(7):
                temp_lst = [
                    f'{el}{"00" * (i + 1)}' if el != '40' else f'{el}{"00" * (i + 1)}@' for el in mask_after_8stages_get
                ]
                stages = stages + temp_lst
            # print(stages)

            get_val_stage_UG405_Peek = {k: v for v, k in enumerate(stages, 1)}
            return get_val_stage_UG405_Peek
            # print(get_val_stage_UG405_POTOK)
        elif option == 'set':
            mask_after_8stages_set = ['01', '02', '04', '08', '10', '20', '40', '80']
            stages = ['01', '02', '04', '08', '10', '20', '40', '80']
            for i in range(7):
                temp_lst = [
                    f'{el}{"00" * (i + 1)}' for el in mask_after_8stages_set
                ]
                stages = stages + temp_lst
            set_val_stage_UG405_Peek = {str(k): v for k, v in enumerate(stages, 1)}
            # print(set_val_stage_UG405_POTOK)
            return set_val_stage_UG405_Peek

    # Ключи значения фаз для get запросов UG405 Peek
    get_val_stage_UG405_PEEK = {'0100': 1, '0200': 2, '0400': 3, '0800': 4,
                                '1000': 5, '2000': 6, '4000@': 7, '8000': 8,
                                '0001': 9, '0002': 10, '0004': 11, '0008': 12,
                                '0010': 13, '0020': 14, '0040@': 15, '0080': 16,

                                '010000': 1, '020000': 2, '040000': 3, '080000': 4,
                                '100000': 5, '200000': 6, '400000@': 7, '800000': 8,
                                '000100': 9, '000200': 10, '000400': 11, '000800': 12,
                                '001000': 13, '002000': 14, '004000@': 15, '008000': 16,

                                '01000000': 1, '02000000': 2, '04000000': 3, '08000000': 4,
                                '10000000': 5, '20000000': 6, '40000000@': 7, '80000000': 8,
                                '00010000': 9, '00020000': 10, '00040000': 11, '00080000': 12,
                                '00100000': 13, '00200000': 14, '00400000@': 15, '00800000': 16,

                                '01': 1, '02': 2, '04': 3, '08': 4,
                                '10': 5, '6': 6, '@': 7, '80': 8,
                                }

    # Ключи значения фаз для set запросов UG405 Peek
    set_stage_UG405_peek_values = val_stages_for_get_stage_UG405_peek(option='set')

    # oid для UG405 Peek
    peek_utcType2OperationModeTimeout = '.1.3.6.1.4.1.13267.3.2.2.4.0'
    peek_utcType2OperationMode = '.1.3.6.1.4.1.13267.3.2.4.1.0'
    peek_utcControlLO = '.1.3.6.1.4.1.13267.3.2.4.2.1.11'
    peek_utcControlFF = '.1.3.6.1.4.1.13267.3.2.4.2.1.20'
    peek_utcControlTO = '.1.3.6.1.4.1.13267.3.2.4.2.1.15'
    peek_utcControlFn = '.1.3.6.1.4.1.13267.3.2.4.2.1.5'
    peek_utcReplyGn = '.1.3.6.1.4.1.13267.3.2.5.1.1.3'

    mask_url_get_data = '/hvi?file=m001a.hvi&pos1=0&pos2=-1'

    state_CONTROL = ('УПРАВЛЕНИЕ', 'CONTROL')
    state_FLASH = 'МИГАНИЕ'
    state_RED = 'КРУГОМ КРАСНЫЙ'

    modeVA = 'VA'
    modeFT = 'FT'
    modeMAN = 'MAN'
    modeUTC = 'UTC'
    modeCLF = 'CLF'

    # oid для UG405 Peek
    # oids_UG405_PEEK = {peek_utcReplyGn: '.1.3.6.1.4.1.13267.3.2.5.1.1.3',
    #                    peek_utcControlLO: '.1.3.6.1.4.1.13267.3.2.4.2.1.11',
    #                    peek_utcControlFF: '.1.3.6.1.4.1.13267.3.2.4.2.1.20',
    #                    peek_utcControlTO: '.1.3.6.1.4.1.13267.3.2.4.2.1.15',
    #                    peek_utcControlFn: '.1.3.6.1.4.1.13267.3.2.4.2.1.5',
    #                    peek_utcType2OperationModeTimeout: '.1.3.6.1.4.1.13267.3.2.2.4.0',
    #                    peek_utcType2OperationMode: '.1.3.6.1.4.1.13267.3.2.4.1.0'
    #                    }

    def __init__(self, ip_adress, scn):
        super().__init__(ip_adress)
        self.scn = self.convert_scn(scn)
        self.stage = None
        self.plan = None

    def get_stageFn(self):
        """  Возвращает номер текущей фазы """

        oid = self.peek_utcReplyGn + self.scn
        stage6 = [' \n']
        bad_scn = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')
            val_list = proc.readlines()
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
            # print(val_list)
            # print(val_string)
            if 'Timeout' not in val_string and val_string != '0000' and val_list != stage6:
                return self.get_val_stage_UG405_PEEK.get(val_string)
            elif val_string == '0000':
                return val_string
            elif val_list == stage6:
                return 6
            elif i == 3:
                return 'None'
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad scn'

    def get_stage(self):
        """  Возвращает номер текущей фазы """
        return self.stage

    def get_plan(self):
        """  Возвращает номер текущего плана """
        return self.plan

    def get_LO(self):

        oid = self.peek_utcControlLO + self.scn
        bad_scn = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')

            val_list = proc.readlines()
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
            if 'Timeout' not in val_string:
                return val_string
            elif i == 3:
                return
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad scn'

    def get_FF(self):

        oid = self.peek_utcControlFF + self.scn
        bad_scn = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')

            val_list = proc.readlines()
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
            if 'Timeout' not in val_string:
                return val_string
            elif i == 3:
                return
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad scn'

    def get_OperationModeTimeout(self) -> str:

        oid = self.peek_utcType2OperationModeTimeout
        bad_scn = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')

            val_list = proc.readlines()
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
            if 'Timeout' not in val_string:
                return val_string
            elif i == 3:
                break
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad oid'

    def get_OperationMode(self):

        oid = self.peek_utcType2OperationMode
        bad_scn = ['\n']

        for i in range(4):
            # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
            #                         stdout=subprocess.PIPE, text=True)
            proc = os.popen(f'{self.snmp_get} -q -r:{self.ip_adress} -v:2c -t:1 -c:{self.community} -o:{oid}')

            val_list = proc.readlines()
            val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
            if 'Timeout' not in val_string:
                return val_string
            elif i == 3:
                return
            elif 'Timeout' in val_string:
                continue
            elif val_list == bad_scn:
                return 'Bad oid'

    def get_mode(self):
        """
        Возвращает текущий режим
        '8': 'Адаптивный',
        '10': 'Ручное управление',
        '11': 'Удалённое управление',
        '12': 'Фиксированный',
        '--': 'Нет данных',
        :return current mode
        """

        url = f'http://{self.ip_adress}{self.mask_url_get_data}'
        session = requests.get(url)
        data = bytes.decode(session.content, encoding='utf-8')

        state = mode = None
        for line in data.split('\n'):
            if 'T_PLAN' in line:
                self.plan = line.replace(':D;;##T_PLAN##;', '').replace('-', '').replace(' ', '')
                print(f'self.plan: {self.plan}')
            elif ':SUBTITLE' in line:
                adress = line.replace(':SUBTITLE;Moscow:', '')
                print(f'adress: {adress}')
            elif 'T_STATE' in line:
                state = line.replace(':D;;##T_STATE##;', '')
                print(f'state: {state}')

            elif 'T_MODE' in line:
                mode, stage = line.replace(':D;;##T_MODE## (##T_STAGE##);', '').split()
                self.stage = stage.replace('(', '').replace(')', '')
                print(f'mode: {mode}, self.stage: {self.stage}')
                break

        print(f'if self.stage.isdigit(): {self.stage.isdigit()}')
        print(f'int(self.stage) > 0: {int(self.stage) > 0}')
        print(f'self.state_CONTROL: {self.state_CONTROL}')

        if self.stage.isdigit() and int(self.stage) > 0 and state.strip() in self.state_CONTROL:
            if mode == self.modeVA:
                return '8'
            elif mode == self.modeFT:
                return '12'
            elif mode == self.modeMAN:
                return '10'
            elif mode == self.modeUTC:
                return '11'
            else:
                return '--'


###########################


"""**************************************************************************
***                          Configuration Peek                          ****   
*****************************************************************************
"""


"""*********************************************************************************
***                          Configuration Potok UG405                          ****   
************************************************************************************
"""


"""*********************************************************************************
***                          Configuration Potok STCIP                          ****   
************************************************************************************
"""
# Ключи значения фаз для get запросов STCIP Potok
# get_val_stage_STCIP_potok = {'2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '9': 8,
# get_val_stage_STCIP_potok = {str(k): str(v) for k, v in zip(range(2, 66), range(1, 65))}
# Словарь вида: {'2': '1', '3': '2', '4': '3'...'65': '64'}


# ************************************************************************************ #

"""*******************************************************************
***                          GET-REQUEST                          ****   
**********************************************************************
"""

"""************************* Peek *************************"""


############################################################

"""********************* Potok UG_405 *********************"""





############################################################

"""********************* Potok STCIP **********************"""



############################################################

"""********************* Swarco STCIP *********************"""



##############################################################


"""*******************************************************************
***                          SET-REQUEST                          ****   
**********************************************************************
"""

"""************************* Peek *************************"""


def set_operation_timeout_ug405_peek(ip_adress: str, value='90'):
    """ Функция устанавливает таймаут  для OperationMode(Utc Control(3))
        Необходимо передать ip и значение таймаута. Если не передать значение,
        по умолчанию устанавливает 90 секунд
    """

    community = community_peek
    oid = f'{oids_UG405_PEEK.get(peek_utcType2OperationModeTimeout)}'

    # subprocess.Popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}'
    #                  f' -val:{value} -tp:int')
    os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}'
             f' -val:{value} -tp:int')


def set_operation_mode_ug405_peek(ip_adress: str, value=('2', '3')):
    """ Функция устанавливает режим operation mode:(Standalone(1), (Monitor(2), Utc Control(3)).
        Необходимо передать ip и значение, которое необходимо установить для
        operation mode. Если значение не передать, по умолчанию установит
        Utc Control(3)
    """

    community = community_peek
    oid = f'{oids_UG405_PEEK.get(peek_utcType2OperationMode)}'

    current_operation_mode = get_OperationMode_ug405_peek(ip_adress)

    if current_operation_mode == '1' and value == ('2', '3'):
        for i in range(2):
            os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}'
                     f' -val:{value[0]} -tp:int')

        for i in range(2):
            os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}'
                     f' -val:{value[1]} -tp:int')

    elif value == ('2', '3') and current_operation_mode in value:
        for i in range(2):
            os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}'
                     f' -val:{value[1]} -tp:int')

    elif value != ('2', '3'):
        for i in range(2):
            os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}'
                     f' -val:{value} -tp:int')


def set_Fn_ug405_peek(ip_adress: str, scn_no_convert: str, value):
    """ Функция устанавливает set запрос фазы (Fn бит)
        Необходимо передать ip, scn в виде "COxxxx"(например "СO1111",
        значение фазы в виде: "Фаза 1", "Фаза 2"..."Фаза n"
    """

    if value not in set_stage_UG405_peek_values:
        return

    # stage_set = '0040'
    # test_hex = OctetString(hexValue=stage_set)
    # print(test_hex)

    scn = convert_scn(scn_no_convert)
    oid = f'{oids_UG405_PEEK.get(peek_utcControlFn)}{scn}'
    value = set_stage_UG405_peek_values.get(value)
    value = bytes.fromhex(value)
    value = OctetString(value)
    community = community_peek

    async def run():
        errorIndication, errorStatus, errorIndex, varBinds = await setCmd(

            SnmpEngine(),
            CommunityData(community, mpModel=1),
            UdpTransportTarget((ip_adress, 161), timeout=1, retries=2),
            ContextData(),
            ObjectType(ObjectIdentity(oid), value)
        )
        asyncio.run(run())


def set_TO_ug405_peek(ip_adress, scn_no_convert, value=1):
    """ Функция устанавливает  значение в TO бит.
        Необходимо передать ip, scn в виде "COxxxx"(например "СO1111", значение 0 или 1.
        Если значение не передать, по умолчанию установит 1.
    """

    scn = convert_scn(scn_no_convert)
    community = community_peek
    oid = f'{oids_UG405_PEEK.get(peek_utcControlTO)}{scn}'

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}'
                 f' -val:{value} -tp:int')


def set_LO_ug405_peek(ip_adress, scn_no_convert, value=0):
    """ Функция устанавливает  значение в LO бит.
        Необходимо передать ip, scn в виде "COxxxx"(например "СO1111", значение 0 или 1.
        Если значение не передать, по умолчанию установит 0.
    """

    scn = convert_scn(scn_no_convert)
    community = community_peek
    oid = f'{oids_UG405_PEEK.get(peek_utcControlLO)}{scn}'

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}'
                 f' -val:{value} -tp:int')


def set_FF_ug405_peek(ip_adress, scn_no_convert, value=0):
    """ Функция устанавливает  значение в FF бит.
        Необходимо передать ip, scn в виде "COxxxx"(например "СO1111", значение 0 или 1.
        Если значение не передать, по умолчанию установит 0.
    """

    scn = convert_scn(scn_no_convert)
    community = community_peek
    oid = f'{oids_UG405_PEEK.get(peek_utcControlFF)}{scn}'

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}'
                 f' -val:{value} -tp:int')


##############################################################


"""********************* Potok UG_405 *********************"""





##############################################################

"""********************* Potok STCIP **********************"""



##############################################################

"""********************* Swarco STCIP *********************"""



##############################################################


