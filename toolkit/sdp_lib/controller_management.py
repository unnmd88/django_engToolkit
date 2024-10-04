import itertools
from collections.abc import Iterable
import time
from datetime import datetime
from enum import Enum
import asyncio
import paramiko
import aiohttp
from pysnmp.hlapi.asyncio import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

"""*******************************************************************
***                          GET-REQUEST                          ****   
**********************************************************************
"""


async def get_stage(ip_adress, community, oids):
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        SnmpEngine(),
        CommunityData(community),
        UdpTransportTarget((ip_adress, 161), timeout=0, retries=0),
        ContextData(),
        *oids
    )
    return varBinds


#
# def convert_scn(scn):
#     """ Функция получает на вход строку, которую необходимо конвертировать в SCN
#         для управления и мониторинга по протоколу UG405.
#         Например: convert_scn(CO1111)
#     """
#     len_scn = str(len(scn)) + '.'
#     convert_to_ASCII = [str(ord(c)) for c in scn]
#     scn = f'.1.{len_scn}{".".join(convert_to_ASCII)}'
#     return scn


class BaseSTCIP:
    community = 'private'

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
    swarcoUTCSignalGroupState = '.1.3.6.1.4.1.1618.3.5.2.1.6.0'
    swarcoUTCSignalGroupOffsetTime = '.1.3.6.1.4.1.1618.3.5.2.1.3.0'

    converted_values_flash_dark = {
        '1': '2', 'true': '2', 'on': '2', 'вкл': '2', '2': '2',
        '0': '0', 'false': '0', 'off': '0', 'выкл': '0',
    }

    def __init__(self, ip_adress, num_host=None, ):
        self.num_host = num_host
        self.ip_adress = ip_adress

    """ GET REQUEST """

    async def get_swarcoUTCStatusEquipment(self, timeout=0, retries=0):
        """
        Возвращает значение swarcoUTCStatusEquipment -> текущего режима ДК
        |----EquipmentStatus (INTEGER)
        |----noInformation(0)
        |----workingProperly(1)
        |----powerUp(2)
        |----dark(3)
        |----flash(4)
        |----partialFlash(5)
        |----allRed(6)
        :param timeout: таймаут подключения
        :param retries: количество попыток подключения
        :return: значение swarcoUTCStatusEquipment
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCStatusEquipment), ),
        )
        return varBinds[0][1]

    async def get_swarcoUTCTrafftechPhaseCommand(self, timeout=0, retries=0):
        """
        Возвращает значение команды текущей фазы swarcoUTCTrafftechPhaseCommand ->
        :param timeout: таймаут подключения
        :param retries: количество попыток подключения
        :return: значение команды swarcoUTCTrafftechPhaseCommand
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPhaseCommand), ),
        )
        return varBinds[0][1]

    async def get_swarcoUTCTrafftechPhaseStatus(self, timeout=0, retries=0):
        """
        Возвращает значение текущей фазы swarcoUTCTrafftechPhaseStatus ->
        :param timeout: таймаут подключения
        :param retries: количество попыток подключения
        :return: значение swarcoUTCTrafftechPhaseStatus
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPhaseStatus), ),
        )
        return varBinds[0][1]

    async def get_swarcoUTCTrafftechPlanCommand(self, timeout=0, retries=0):
        """
        Возвращает значение команды текущего плана swarcoUTCTrafftechPlanCommand ->
        :param timeout: таймаут подключения
        :param retries: количество попыток подключения
        :return: значение команды текущего плана swarcoUTCTrafftechPlanCommand
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPlanCommand), ),
        )
        return varBinds[0][1]

    async def get_swarcoUTCTrafftechPlanCurrent(self, timeout=0, retries=0):
        """
        Возвращает номер текущего плана swarcoUTCTrafftechPlanCurrent
        :param timeout: таймаут подключения
        :param retries: количество попыток подключения
        :return: значение номер текущего плана swarcoUTCTrafftechPlanCurrent
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPlanCurrent), ),
        )
        return varBinds[0][1]

    async def get_swarcoUTCTrafftechPlanSource(self, timeout=0, retries=0):
        """
        Возвращает значение источника текущего плана swarcoUTCTrafftechPlanSource
        |---- trafficActuatedPlanSelectionCommand(1)
        |----currentTrafficSituationCentral(2)
        |----controlBlockOrInput(3)
        |----manuallyFromWorkstation(4)
        |----emergencyRoute(5)
        |----currentTrafficSituation(6)
        |----calendarClock(7)
        |----controlBlockInLocal(8)
        |----forcedByParameterBP40(9)
        |----startUpPlan(10)
        |----localPlan(11)
        |----manualControlPlan(12)
        :param timeout: таймаут подключения
        :param retries: количество попыток подключения
        :return: значение источника текущего плана swarcoUTCTrafftechPlanSource
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPlanSource), ),
        )
        return varBinds[0][1]

    async def get_swarcoSoftIOStatus(self, num_inp=None, timeout=0, retries=0):
        """
        Возвращает строку в виде "0000001000..." значений софт входов swarcoSoftIOStatus
        :param num_inp: можно указать номер определённого входа, значение которого хотим получить(от 0 до 255)
        :param timeout: таймаут подключения
        :param retries: количество попыток подключения
        :return: значение номер текущего плана swarcoUTCTrafftechPlanCurrent
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoSoftIOStatus), ),
        )
        if num_inp is None or num_inp.isdigit and int(num_inp) in range(0, 256):
            return varBinds[0][1]
        return varBinds[0][1][int(num_inp) + 1]

    async def get_swarcoUTCDetectorQty(self, timeout=0, retries=0):
        """
        Возвращает количество дет логик swarcoUTCDetectorQty
        :param timeout: таймаут подключения
        :param retries: количество попыток подключения
        :return: количество дет логик swarcoUTCDetectorQty
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCDetectorQty), ),
        )
        return varBinds[0][1]

    async def get_swarcoUTCSignalGroupState(self, timeout=0, retries=0):
        """
        Возвращает значение текущих состояний групп в hex формате в виде строки swarcoUTCSignalGroupState
        :param timeout: таймаут подключения
        :param retries: количество попыток подключения
        :return: значение текущих состояний групп в hex формате в виде строки swarcoUTCSignalGroupState
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCSignalGroupState), ),
        )
        return varBinds[0][1]

    """ SET REQUEST """

    async def set_swarcoUTCTrafftechPlanCommand(self, value='0'):
        """"
        Устанавливает  текущий план.
        :param value:  1-16 обычный план, 17 -> ЖМ, 18 -> ОС, 100 -> КК,
        """
        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPlanCommand), Unsigned32(value))
        )

    async def set_swarcoUTCTrafftechPhaseCommand(self, value=0):
        """"
        Устанавливает  фазу.
        :param value:  Значение фазы (фаза 1 -> value=2, фаза 2 -> value=3 и т.д)
        """
        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPhaseCommand), Unsigned32(value))
        )

    async def set_swarcoUTCCommandFlash(self, value='0'):
        """"
        Устанавливает ЖМ(или сбрасывает ранее установленный в swarcoUTCCommandFlash)
        :param value: 2 -> устанавливает ОС, 0 -> сбрасывает ранее установленный ЖМ
        """
        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCCommandFlash), Integer32(value))
        )

    async def set_swarcoUTCCommandDark(self, value='0'):
        """"
        Устанавливает ОС(или сбрасывает ранее установленный в swarcoUTCCommandDark)
        :param value: 2 -> устанавливает ОС, 0 -> сбрасывает ранее установленный ОС
        """
        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCCommandDark), Integer32(value))
        )


class BaseUG405:
    community = 'UTMC'

    # Ключи, прописанные вручную, рабочая версия
    # set_stage_UG405_peek_values = {'1': '01', '2': '02', '3': '04', '4': '08',
    #                                '5': '10', '6': '20', '7': '40', '8': '80',
    #                                '9': '0001', '10': '0002', '11': '0004', '12': '0008',
    #                                '13': '0010', '14': '0020', '15': '0040', '16': '0080'}

    # oid для UG405 Peek
    utcType2OperationModeTimeout = '.1.3.6.1.4.1.13267.3.2.2.4.0'
    utcType2OperationMode = '.1.3.6.1.4.1.13267.3.2.4.1.0'
    utcControlLO = '.1.3.6.1.4.1.13267.3.2.4.2.1.11'
    utcControlFF = '.1.3.6.1.4.1.13267.3.2.4.2.1.20'
    utcControlTO = '.1.3.6.1.4.1.13267.3.2.4.2.1.15'
    utcControlFn = '.1.3.6.1.4.1.13267.3.2.4.2.1.5'
    utcReplyGn = '.1.3.6.1.4.1.13267.3.2.5.1.1.3'
    utcReplyFR = '.1.3.6.1.4.1.13267.3.2.5.1.1.36'
    utcReplyDF = '.1.3.6.1.4.1.13267.3.2.5.1.1.5'
    utcReplyMC = '.1.3.6.1.4.1.13267.3.2.5.1.1.15'
    utcReplyCF = '.1.3.6.1.4.1.13267.3.2.5.1.1.16'

    # oid для UG405 Peek
    # oids_UG405_PEEK = {peek_utcReplyGn: '.1.3.6.1.4.1.13267.3.2.5.1.1.3',
    #                    peek_utcControlLO: '.1.3.6.1.4.1.13267.3.2.4.2.1.11',
    #                    peek_utcControlFF: '.1.3.6.1.4.1.13267.3.2.4.2.1.20',
    #                    peek_utcControlTO: '.1.3.6.1.4.1.13267.3.2.4.2.1.15',
    #                    peek_utcControlFn: '.1.3.6.1.4.1.13267.3.2.4.2.1.5',
    #                    peek_utcType2OperationModeTimeout: '.1.3.6.1.4.1.13267.3.2.2.4.0',
    #                    peek_utcType2OperationMode: '.1.3.6.1.4.1.13267.3.2.4.1.0'
    #                    }

    @staticmethod
    def convert_scn(scn):
        """ Функция получает на вход строку, которую необходимо конвертировать в SCN
            для управления и мониторинга по протоколу UG405.
            Например: convert_scn(CO1111)
        """
        len_scn = str(len(scn)) + '.'
        convert_to_ASCII = [str(ord(c)) for c in scn]
        scn = f'.1.{len_scn}{".".join(convert_to_ASCII)}'
        return scn

    def __init__(self, ip_adress, scn, num_host=None):
        self.ip_adress = ip_adress
        self.scn = self.convert_scn(scn)
        self.num_host = num_host

    """ GET REQUEST """

    async def get_utcType2OperationModeTimeout(self, timeout=0, retries=0):
        """
        Возвращает значение OperationModeTimeout
        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return Текущее значение utcType2OperationModeTimeout
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcType2OperationModeTimeout), ),
        )
        return varBinds[0][1].prettyPrint()

    async def get_utcType2OperationMode(self, timeout=0, retries=0):
        """
        Возвращает значение OperationModeTimeout
        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return Текущее значение utcType2OperationMode
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcType2OperationModeTimeout), ),
        )
        return varBinds[0][1].prettyPrint()

    async def get_utcReplyGn(self, timeout=0, retries=0):
        """
        Возвращает значение фазы utcReplyGn в стоке hex формата
        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return значение фазы utcReplyGn в стоке hex формата
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcReplyGn), ),
        )
        return varBinds[0][1].prettyPrint()

    async def get_utcControlTO(self, timeout=0, retries=0):
        """
        Возвращает значение utcControlTO
        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return Текущее значение utcControlTO
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcControlTO), ),
        )
        return varBinds[0][1].prettyPrint()

    async def get_utcControlLO(self, timeout=0, retries=0):
        """
        Возвращает значение utcControlLO
        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return Текущее значение utcControlLO
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcControlLO), ),
        )
        return varBinds[0][1].prettyPrint()

    async def get_utcControlFF(self, timeout=0, retries=0):
        """
        Возвращает значение utcControlFF
        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return Текущее значение utcControlFF
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcControlFF), ),
        )
        return varBinds[0][1].prettyPrint()

    async def get_utcControlFn(self, timeout=0, retries=0):
        """
        Возвращает кортеж значений utcControlFn в виде "val: stage"
        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return tuple: Возвращает текущее значение utcControlFn в виде "val: stage"
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcControlFn), ),
        )
        return varBinds[0][1].prettyPrint()

    async def get_utcReplyFR(self, timeout=0, retries=0):
        """
        Возвращает значение utcReplyFR ( Condition '1' confirms that the controller signals are in flashing
        amber mode. This bit is only specified for export (non-UK) applications.)
        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return tuple: Возвращает значение utcReplyFR (1 или 0)
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcReplyFR), ),
        )
        return varBinds[0][1].prettyPrint()

    async def get_utcReplyDF(self, timeout=0, retries=0):
        """
        Возвращает значение utcReplyDF ( Condition '1' confirms that the controller signals are in flashing
        amber mode. This bit is only specified for export (non-UK) applications.)
        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return tuple: Возвращает значение utcReplyDF (1 или 0)
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcReplyDF), ),
        )
        return varBinds[0][1].prettyPrint()

    async def get_utcReplyMC(self, timeout=0, retries=0):
        """
        Возвращает значение utcReplyMC
        Condition 1 confirms that Manual Control is either in operation or requested as specified in an
        associated Works Specification.
        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return Текущее значение utcReplyMC
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcReplyMC + self.scn), ),
        )
        return varBinds[0][1].prettyPrint()

    """ archive methods(not usage) """

    # def get_mode(self):
    #     """
    #     Возвращает текущий режим
    #     '8': 'Адаптивный',
    #     '10': 'Ручное управление',
    #     '11': 'Удалённое управление',
    #     '12': 'Фиксированный',
    #     '--': 'Нет данных',
    #     :return current mode
    #     """
    #
    #     url = f'http://{self.ip_adress}{self.mask_url_get_data}'
    #     session = requests.get(url)
    #     data = bytes.decode(session.content, encoding='utf-8')
    #
    #     state = mode = None
    #     for line in data.split('\n'):
    #         if 'T_PLAN' in line:
    #             self.plan = line.replace(':D;;##T_PLAN##;', '').replace('-', '').replace(' ', '')
    #             print(f'self.plan: {self.plan}')
    #         elif ':SUBTITLE' in line:
    #             adress = line.replace(':SUBTITLE;Moscow:', '')
    #             print(f'adress: {adress}')
    #         elif 'T_STATE' in line:
    #             state = line.replace(':D;;##T_STATE##;', '')
    #             print(f'state: {state}')
    #
    #         elif 'T_MODE' in line:
    #             mode, stage = line.replace(':D;;##T_MODE## (##T_STAGE##);', '').split()
    #             self.stage = stage.replace('(', '').replace(')', '')
    #             print(f'mode: {mode}, self.stage: {self.stage}')
    #             break
    #
    #     print(f'if self.stage.isdigit(): {self.stage.isdigit()}')
    #     print(f'int(self.stage) > 0: {int(self.stage) > 0}')
    #     print(f'self.state_CONTROL: {self.state_CONTROL}')
    #
    #     if self.stage.isdigit() and int(self.stage) > 0 and state.strip() in self.state_CONTROL:
    #         if mode == self.modeVA:
    #             return '8'
    #         elif mode == self.modeFT:
    #             return '12'
    #         elif mode == self.modeMAN:
    #             return '10'
    #         elif mode == self.modeUTC:
    #             return '11'
    #         else:
    #             return '--'

    """ SET REQUEST """

    async def set_utcControlTO(self, value=1):
        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcControlTO + self.scn), Integer32(value)),
        )

    async def set_utcControlFn(self, value: str, timeout=1, retries=1):
        """
            Устанавливает Fn бит(фаза).
            :param timeout: Таймаут подключения
            :param retries: Количетсво попыток подключения
            :param value -> str. В аргумент необходимо передавать номер фазы в десятичном виде.
        """
        pass

    async def set_utcControlLO(self, value=0, timeout=1, retries=1):
        """
            Устанавливает utcControlLO бит(Выключение сигналов).
            :param timeout: Таймаут подключения
            :param retries: Количетсво попыток подключения
            :param value -> В аргумент необходимо передавать значение 1 или 0.
        """

        await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcControlLO + self.scn), Integer32(value)),
        )

    async def set_utcControlFF(self, value=0, timeout=1, retries=1):
        """
            Устанавливает utcControlFF бит(Жёлтое мигание).
            :param timeout: Таймаут подключения
            :param retries: Количетсво попыток подключения
            :param value -> В аргумент необходимо передавать значение 1 или 0.
        """

        await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcControlFF + self.scn), Integer32(value)),
        )

    async def set_utcType2OperationMode(self, value=1):
        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcType2OperationMode + self.scn), Integer32(value)),
        )

    async def set_utcType2OperationModeTimeout(self, value=90):
        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcType2OperationModeTimeout + self.scn), Integer32(value)),
        )


class SwarcoSTCIP(BaseSTCIP):
    get_val_stage = {'2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '1': 8}
    set_val_stage = {'1': 2, '2': 3, '3': 4, '4': 5, '5': 6, '6': 7, '7': 8, '8': 1, 'ЛОКАЛ': 0, '0': 0}

    converted_values_all_red = {
        '1': '119', 'true': '119', 'on': '119', 'вкл': '119',
        '0': '100', 'false': '100', 'off': '100', 'выкл': '100',
    }

    """ GET REQUEST """

    async def get_current_mode(self, timeout=0, retries=0):
        print(f'перед await get_current_mode')
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCStatusEquipment), ),
            ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPhaseStatus), ),
            ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPlanCurrent), ),
            ObjectType(ObjectIdentity(self.swarcoUTCDetectorQty), ),
            ObjectType(ObjectIdentity(self.swarcoSoftIOStatus), ),
        )

        return self, self.num_host, varBinds

    async def get_stage(self, timeout=0, retries=0):
        """
        Возвращает номер текущей фазы
        :param timeout: таймаут подключения
        :param retries: количество попыток подключения
        :return: номер фазы
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPhaseStatus), ),
        )
        return self.get_val_stage.get(varBinds[0][1])

    """ SET REQUEST """

    async def set_stage(self, value='0'):
        """"
        Устанавливает  фазу.
        :param value:  Номер фазы в десятичном виде
        """

        await self.set_swarcoUTCTrafftechPhaseCommand(self.set_val_stage.get(str(value)))

    # def set_stage(self, value=0):
    #     """"
    #     Устанавливает  фазу.
    #     :param value:  Номер фазы в десятичном виде
    #     """
    #     value = self.set_val_stage.get(str(value))
    #
    #     async def run(value):
    #         print('async def run(value):')
    #         await setCmd(
    #             SnmpEngine(),
    #             CommunityData(self.community),
    #             UdpTransportTarget((self.ip_adress, 161)),
    #             ContextData(),
    #             ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPhaseCommand), Unsigned32(value))
    #         )
    #     asyncio.run(run(value))

    async def set_flash(self, value='0'):
        """"
        Устанавливает ОС(или сбрасывает ранее установленный в swarcoUTCCommandDark)
        :param value: 2 -> устанавливает ОС, 0 -> сбрасывает ранее установленный ОС
        """
        print(' async def set_flash(self, value):')
        value = self.converted_values_flash_dark.get(value)
        await self.set_swarcoUTCCommandFlash(value)

    async def set_dark(self, value='0'):
        """"
        Устанавливает ОС(или сбрасывает ранее установленный в swarcoUTCCommandDark)
        :param value: 2 -> устанавливает ОС, 0 -> сбрасывает ранее установленный ОС
        """
        value = self.converted_values_flash_dark.get(value)
        await self.set_swarcoUTCCommandDark(value)

    async def set_allred(self, value='100'):
        """"
        Устанавливает КК(или сбрасывает ранее установленный в swarcoUTCCommandDark)
        :param value: 100 -> устанавливает К, 0 -> сбрасывает ранее установленный КК
        """
        value = self.converted_values_all_red.get(value)
        await self.set_swarcoUTCTrafftechPlanCommand(value)


class PotokS(BaseSTCIP):
    get_val_stage = {
        str(k): str(v) for k, v in zip(range(2, 66), range(1, 65))
    }
    # set_val_stage = {
    #     str(k) if k < 65 else 'ЛОКАЛ': str(v) if k < 65 else '0' for k, v in zip(range(1, 68), range(2, 69))
    # }

    set_val_stage = {
        str(k): str(v) if k > 0 else '0' for k, v in zip(range(65), range(1, 66))
    }

    # Command
    potokUTCCommandAllRed = '1.3.6.1.4.1.1618.3.2.2.4.1.0'
    potokUTCSetGetLocal = '1.3.6.1.4.1.1618.3.7.2.8.1.0'
    potokUTCprohibitionManualPanel = '1.3.6.1.4.1.1618.3.6.2.1.3.1.0'
    restart_programm = '1.3.6.1.4.1.1618.3.2.2.3.1.0'
    # Status
    potokUTCStatusMode = '1.3.6.1.4.1.1618.3.6.2.2.2.0'

    """ GET REQUEST """

    async def get_current_mode(self, timeout=0, retries=0):
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCStatusEquipment), ),
            ObjectType(ObjectIdentity(self.potokUTCStatusMode), ),
            ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPhaseStatus), ),
            ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPlanCurrent), ),
        )

        if errorIndication is None and varBinds and len(varBinds) >= 4:
            return self, self.num_host, varBinds
        else:
            return self, self.num_host, False

    async def get_potokUTCStatusMode(self, timeout=0, retries=0):
        """
        Возвращает статусы работы ДК:
        |----0 -> нет информации
        |----8 -> адаптива (А)
        |----10 -> ручное управление (Р)
        |----11 -> удаленное управление (Ц)
        |----12 -> фикс (Ф или А)
        :param timeout: таймаут подключения
        :param retries: количество попыток подключения
        :return Возвращает значение текущего статуса
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.potokUTCStatusMode), ),
        )
        return varBinds[0][1]

    async def get_stage(self, timeout=0, retries=0):
        """
        Возвращает номер текущей фазы
        :param timeout: таймаут подключения
        :param retries: количество попыток подключения
        :return: номер фазы
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPhaseStatus), ),
        )
        return self.get_val_stage.get(varBinds[0][1])

    async def get_swarcoUTCSetGetLocal(self, timeout=0, retries=0):
        """
        Возвращает локальный режим(1 -> ВКЛ, 0 -> ВЫКЛ) swarcoUTCSetGetLocal
        :param timeout: таймаут подключения
        :param retries: количество попыток подключения
        :return: Возвращает локальный режим(1 -> ВКЛ, 0 -> ВЫКЛ) swarcoUTCSetGetLocal
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.potokUTCSetGetLocal), ),
        )
        return varBinds[0][1]

    async def get_potokUTCprohibitionManualPanel(self, timeout=0, retries=0):
        """
        Возвращает локальный режим(1 -> ВКЛ, 0 -> ВЫКЛ) swarcoUTCSetGetLocal
        :param timeout: таймаут подключения
        :param retries: количество попыток подключения
        :return: Возвращает локальный режим(1 -> ВКЛ, 0 -> ВЫКЛ) swarcoUTCSetGetLocal
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.potokUTCprohibitionManualPanel), ),
        )
        return varBinds[0][1]

    """ SET REQUEST """

    async def set_stage(self, value='0'):
        """"
        Устанавливает  фазу.
        :param value:  Номер фазы в десятичном виде
        """
        if value.lower() in ('false', 'reset', 'сброс', 'локал', 'local'):
            value = '0'
        else:
            value = self.set_val_stage.get(str(value))
        errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCTrafftechPhaseCommand), Unsigned32(value))
        )
        return errorIndication

    async def set_potokUTCCommandAllRed(self, value=0):
        """"
        Устанавливает КК(или сбрасывает ранее установленный в potokUTCCommandAllRed)
        :param value: 2 -> устанавливает КК, 0 -> сбрасывает ранее установленный КК
        """
        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(self.potokUTCCommandAllRed), Unsigned32(value))
        )

    async def set_get_swarcoUTCSetGetLocal(self, value=0):
        """"
        Устанавливает/сбрасывает локальный режим
        :param value: 1 -> устанавливает Устанавливает локальный режим, 0 -> сбрасывает установленный локальный режим
        """
        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(self.get_swarcoUTCSetGetLocal), Unsigned32(value))
        )

    async def set_potokUTCprohibitionManualPanel(self, value=0):
        """
        Устанавливает запрет использования ВПУ(1 -> ВКЛ, 0 -> ВЫКЛ) potokUTCprohibitionManualPanel
        :param timeout: таймаут подключения
        :param retries: количество попыток подключения
        """
        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), ),
            ContextData(),
            ObjectType(ObjectIdentity(self.potokUTCprohibitionManualPanel), Unsigned32(value)),
        )

    async def set_allred(self, value='0'):
        """"
        Устанавливает КК(или сбрасывает ранее установленный в potokUTCCommandAllRed)
        :param value: 2 -> устанавливает КК, 0 -> сбрасывает ранее установленный КК
        """
        value = self.converted_values_flash_dark.get(value)
        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(self.potokUTCCommandAllRed), Unsigned32(value))
        )

    async def set_flash(self, value='0'):
        """"
        Устанавливает ЖМ(или сбрасывает ранее установленный в swarcoUTCCommandFlash)
        :param value: 2 -> устанавливает ОС, 0 -> сбрасывает ранее установленный ЖМ
        """
        value = self.converted_values_flash_dark.get(value)
        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCCommandFlash), Unsigned32(value))
        )

    async def set_dark(self, value='0'):
        """"
        Устанавливает ОС(или сбрасывает ранее установленный в swarcoUTCCommandDark)
        :param value: 2 -> устанавливает ОС, 0 -> сбрасывает ранее установленный ОС
        """
        value = self.converted_values_flash_dark.get(value)
        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(self.swarcoUTCCommandDark), Unsigned32(value))
        )

    async def set_restartProgramm(self, value=1):
        """"
        Перезапускает рабочую программу
        :param value: 1 -> команда на перезапуск рабочей программы
        """
        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161)),
            ContextData(),
            ObjectType(ObjectIdentity(self.restart_programm), Unsigned32(value))
        )


class PotokP(BaseUG405):
    """
        utcControlLO = 'Включить/Выключить ОС'
        utcControlFF = 'Включить/Выключить ЖМ'
        utcControlFn = 'Установка фазы'
        utcControlTO = 'Разрешающий бит(TO)'
        utcType2OperationMode = 'Получение режимов работы ДК(OperationMode)'
        utcType2OperationModeTimeout = 'Таймаут на ожидание команды(OperationModeTimeout)'
        utcControlGn = 'Получение значения фазы(hex)'
        potok_utcReplyPlanStatus = 'Возвращает номер плана'
        potok_utcControRestartProgramm = 'Перезапуск программы'
        potok_utcReplyDarkStatus = Получение состояния ОС(0 - ВЫКЛ выключен, 1 - ВЫКЛ включен)
        utcReplyFR = Получение состояния ЖМ:
                                            |----   0 ЖМ выключен
                                            |----   1 -> по рассписанию
                                            |----   2 -> удаленно
                                            |----   3 -> в ручную
                                            |----   4 -> аварийный

    """

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
            stages = ['01', '02', '04', '08', '0x10', '0x20', '0x40', '0x80']
            for i in range(7):
                temp_lst = [
                    f'{el}{"00" * (i + 1)}' for el in mask_after_8stages_set
                ]
                stages = stages + temp_lst
            set_val_stage_UG405_POTOK = {str(k): v for k, v in enumerate(stages, 1)}
            # print(set_val_stage_UG405_POTOK)
            return set_val_stage_UG405_POTOK

    # Значения фаз для для UG405 Potok
    val_stage_get_request = val_stages_for_get_stage_UG405_potok(option='get')
    val_stage_set_request = val_stages_for_get_stage_UG405_potok(option='set')

    # -- Control Bits --#
    potok_utcControRestartProgramm = '.1.3.6.1.4.1.13267.3.2.4.2.1.5.5'
    # -- Reply Bits --#

    potok_utcReplyPlanStatus = '.1.3.6.1.4.1.13267.1.2.9.1.3'
    potok_utcReplyPlanSource = '1.3.6.1.4.1.13267.1.2.9.1.3.1'
    potok_utcReplyDarkStatus = '.1.3.6.1.4.1.13267.3.2.5.1.1.45'
    potok_utcReplyLocalAdaptiv = '1.3.6.1.4.1.13267.3.2.5.1.1.46'

    potok_utcReplyHardwareErr = '1.3.6.1.4.1.13267.3.2.5.1.1.16.1'
    potok_utcReplySoftwareErr = '1.3.6.1.4.1.13267.3.2.5.1.1.16.2'
    potok_utcReplyElectricalCircuitErr = '1.3.6.1.4.1.13267.3.2.5.1.1.16.3'

    """ GET REQUEST """

    async def get_current_mode(self, timeout=0, retries=0):
        """
        Возвращает значение oid, которые опреляют текущий режим работы контроллера
        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return varBinds
        """
        print(f'перед get_current_mode await')
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcType2OperationMode), ),
            ObjectType(ObjectIdentity(self.utcReplyCF + self.scn), ),
            ObjectType(ObjectIdentity(self.utcReplyFR + self.scn), ),
            ObjectType(ObjectIdentity(self.potok_utcReplyDarkStatus + self.scn), ),
            ObjectType(ObjectIdentity(self.utcReplyMC + self.scn), ),
            ObjectType(ObjectIdentity(self.potok_utcReplyPlanStatus + self.scn), ),
            ObjectType(ObjectIdentity(self.utcReplyGn + self.scn), ),
            ObjectType(ObjectIdentity(self.utcReplyDF + self.scn), ),
            ObjectType(ObjectIdentity(self.potok_utcReplyLocalAdaptiv + self.scn), ),
        )
        return self, self.num_host, varBinds

    async def get_potok_utcReplyPlanStatus(self, timeout=0, retries=0):
        """
        Возвращает значение utcReplyPlanStatus
        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return Текущее значение utcReplyPlanStatus
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.potok_utcReplyPlanStatus + self.scn), ),
        )
        return varBinds[0][1].prettyPrint()

    async def get_potok_utcReplyPlanSource(self, timeout=0, retries=0):
        """
        Возвращает значение utcReplyPlanSource:
        |----   1 - по расписанию
        |----   2 - удаленно включили по snmp
        |----   3 - панели или с веб

        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return Текущее значение utcReplyPlanSource
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.potok_utcReplyPlanSource + self.scn), ),
        )
        return varBinds[0][1].prettyPrint()

    async def get_potok_utcReplyElectricalCircuitErr(self, timeout=0, retries=0):
        """
        Возвращает значение utcReplyElectricalCircuitErr
        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return Текущее значение utcReplyElectricalCircuitErr
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.potok_utcReplyElectricalCircuitErr + self.scn), ),
        )
        return varBinds[0][1].prettyPrint()

    async def get_potok_utcReplyLocalAdaptiv(self, timeout=0, retries=0):
        """
        Возвращает значение utcReplyLocalAdaptiv:
        |----    1 -> установлена локальная адаптива
        |----    0 -> локальная адаптива не установлена

        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return Текущее значение utcReplyLocalAdaptiv
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.potok_utcReplyLocalAdaptiv + self.scn), ),
        )
        return varBinds[0][1].prettyPrint()

    async def get_stage(self, timeout=0, retries=0):
        """
        Возвращает номер фазы в десятичном виде
        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return Значение текущей фазы в десятичном виде
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcReplyGn + self.scn), ),
        )
        return self.val_stage_get_request.get(varBinds[0][1].prettyPrint())

    async def get_dark(self, timeout=0, retries=0):
        """
        Возвращает значение utcReplyDarkStatus
        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return Текущее значение utcReplyDarkStatus
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.potok_utcReplyDarkStatus + self.scn), ),
        )
        return varBinds[0][1].prettyPrint()

    async def get_flash(self, timeout=0, retries=0):
        """
        Возвращает значение utcReplyFR:
        |----   0 ЖМ выключен
        |----   1 -> по рассписанию
        |----   2 -> удаленно
        |----   3 -> в ручную
        |----   4 -> аварийный

        :param timeout: Таймаут подключения
        :param retries: Количетсво попыток подключения
        :return Текущее значение utcReplyFR
        """
        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcReplyFR + self.scn), ),
        )
        return varBinds[0][1].prettyPrint()

    """*******************************************************************
    ***                          SET-REQUEST                          ****   
    **********************************************************************
    """

    async def set_stage(self, value=0):

        if str(value) != '0':
            value = self.val_stage_set_request.get(value)
            await setCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
                ContextData(),
                ObjectType(ObjectIdentity(self.utcType2OperationModeTimeout), Integer32(90)),
                ObjectType(ObjectIdentity(self.utcType2OperationMode), Integer32(3)),
                ObjectType(ObjectIdentity(self.utcControlTO + self.scn), Integer32(1)),
                ObjectType(ObjectIdentity(self.utcControlFn + self.scn), OctetString(hexValue=value)),
            )
        else:

            await setCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
                ContextData(),
                ObjectType(ObjectIdentity(self.utcType2OperationMode), Integer32(1)),
                ObjectType(ObjectIdentity(self.utcControlTO + self.scn), Integer32(0)),
            )

        # for oid, val in varBinds:
        #     print(f'oid = {oid.prettyPrint()}, val = {val.prettyPrint()}')

    async def set_dark(self, value=0):

        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcControlLO + self.scn), Integer32(value)),
        )

    async def set_flash(self, value=0):

        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
            ContextData(),
            ObjectType(ObjectIdentity(self.utcControlFF + self.scn), Integer32(value)),
        )

    async def set_restartProgramm(self, value=1):

        await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
            ContextData(),
            ObjectType(ObjectIdentity(self.potok_utcControRestartProgramm + self.scn), Integer32(value)),
        )


class PeekUG405(BaseUG405):

    @staticmethod
    def val_stages_UG405_peek(option):
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
                    f'{"00" * (i + 1)}{el}' for el in mask_after_8stages_set
                ]
                stages = stages + temp_lst
            set_val_stage_UG405_Peek = {str(k): v for k, v in enumerate(stages, 1)}
            # print(set_val_stage_UG405_POTOK)
            return set_val_stage_UG405_Peek

    # Ключи значения фаз для get запросов UG405 Peek
    val_stage_get_request = {'0100': 1, '0200': 2, '0400': 3, '0800': 4,
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
    val_stage_set_request = val_stages_UG405_peek(option='set')

    # Ключи, прописанные вручную, рабочая версия
    # set_stage_UG405_peek_values = {'1': '01', '2': '02', '3': '04', '4': '08',
    #                                '5': '10', '6': '20', '7': '40', '8': '80',
    #                                '9': '0001', '10': '0002', '11': '0004', '12': '0008',
    #                                '13': '0010', '14': '0020', '15': '0040', '16': '0080'}

    # oid для UG405 Peek

    # Маска адреса для получения контента с данными о режиме/работе дк on-line
    mask_url_get_data = '/hvi?file=m001a.hvi&pos1=0&pos2=-1'
    # Режимы ДК
    state_CONTROL = ('УПРАВЛЕНИЕ', 'CONTROL')
    state_OFF = 'ЛАМПЫ ВЫКЛ'
    state_FLASH = 'ЖЕЛТОЕ МИГАНИЕ'
    state_RED = 'КРУГОМ КРАСНЫЙ'
    state_blocked_inspector = 'ЗАБЛОКИРОВАН ИНСПЕКТОРОМ'
    # Рабочие режимы, когда state_CONTROL = 'УПРАВЛЕНИЕ'
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

    """ GET REQUEST """

    async def get_current_mode(self, timeout=1):

        url = f'http://{self.ip_adress}/hvi?file=m001a.hvi&pos1=0&pos2=-1'
        timeout = aiohttp.ClientTimeout(total=timeout)
        try:
            print(f'перед aiohttp.ClientSession() as session:')
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as s:
                    assert s.status == 200

                    content = await s.text()
        except aiohttp.client_exceptions.ClientConnectorError as e:
            content = f'Нет соединения с хостом {e}'
        except asyncio.TimeoutError as e:
            content = f'Нет соединения с хостом-> {e}'
        return self, self.num_host, content

    """ archive methods(not usage) """

    """ SET REQUEST """

    async def set_stage(self, value: str, timeout=1, retries=1):
        """
            Устанавливает фазу.
            :param timeout: Таймаут подключения
            :param retries: Количетсво попыток подключения
            :param value -> В аргумент необходимо передавать значение 1 или 0.
        """
        # print('set_stage_UG405_peek_values')
        # print(self.val_stage_set_request)
        value = self.val_stage_set_request.get(value)

        lock = asyncio.Lock()
        # print(f'value = {value}')
        # print(f'OctetString(hexValue=value) = {OctetString(hexValue=value)}')
        async with lock:
            errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
                ContextData(),
                ObjectType(ObjectIdentity(self.utcType2OperationMode), ),
            )
            val = varBinds[0][1].prettyPrint()

        if str(val) == '1':
            async with lock:
                errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
                    SnmpEngine(),
                    CommunityData(self.community),
                    UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
                    ContextData(),
                    # ObjectType(ObjectIdentity(oid), value),
                    ObjectType(ObjectIdentity(self.utcType2OperationModeTimeout), Integer32(90)),
                    ObjectType(ObjectIdentity(self.utcType2OperationMode), Integer32(2)),

                )
            errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
                ContextData(),
                ObjectType(ObjectIdentity(self.utcType2OperationMode), Integer32(3)),
            )

        elif str(val) in ('2', '3'):
            async with lock:
                errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
                    SnmpEngine(),
                    CommunityData(self.community),
                    UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
                    ContextData(),
                    ObjectType(ObjectIdentity(self.utcType2OperationMode), Integer32(3)),
                )
        else:
            return

        errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
            ContextData(),
            # ObjectType(ObjectIdentity(oid), value),

            ObjectType(ObjectIdentity(self.utcControlTO + self.scn), Integer32(1)),
            ObjectType(ObjectIdentity(self.utcControlFn + self.scn), OctetString(hexValue=value)),
        )
        # print(errorIndication, errorStatus, errorIndex, varBinds)
        # for oid, val in varBinds:
        #     print(f'oid = {oid.prettyPrint()}, val = {val.prettyPrint()}')

    async def set_flash(self, value=0, timeout=1, retries=1):
        """
            Устанавливает жёлтое мигание.
            :param timeout: Таймаут подключения
            :param retries: Количетсво попыток подключения
            :param value -> В аргумент необходимо передавать значение 1 или 0.
        """

        lock = asyncio.Lock()
        # print(f'value = {value}')
        # print(f'OctetString(hexValue=value) = {OctetString(hexValue=value)}')
        async with lock:
            errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
                ContextData(),
                ObjectType(ObjectIdentity(self.utcType2OperationMode), ),
            )
            val = varBinds[0][1].prettyPrint()

        if str(val) == '1':
            async with lock:
                errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
                    SnmpEngine(),
                    CommunityData(self.community),
                    UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
                    ContextData(),
                    # ObjectType(ObjectIdentity(oid), value),
                    ObjectType(ObjectIdentity(self.utcType2OperationModeTimeout), Integer32(90)),
                    ObjectType(ObjectIdentity(self.utcType2OperationMode), Integer32(2)),

                )
            errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
                ContextData(),
                ObjectType(ObjectIdentity(self.utcType2OperationMode), Integer32(3)),
            )

        elif str(val) in ('2', '3'):
            async with lock:
                errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
                    SnmpEngine(),
                    CommunityData(self.community),
                    UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
                    ContextData(),
                    ObjectType(ObjectIdentity(self.utcType2OperationMode), Integer32(3)),
                )
        else:
            return

        errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
            ContextData(),
            # ObjectType(ObjectIdentity(oid), value),
            ObjectType(ObjectIdentity(self.utcControlFF + self.scn), Integer32(value)),
        )

    async def set_dark(self, value=0, timeout=1, retries=1):
        """
            Устанавливает жёлтое ос.
            :param timeout: Таймаут подключения
            :param retries: Количетсво попыток подключения
            :param value -> В аргумент необходимо передавать значение 1 или 0.
        """

        lock = asyncio.Lock()
        # print(f'value = {value}')
        # print(f'OctetString(hexValue=value) = {OctetString(hexValue=value)}')
        async with lock:
            errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.ip_adress, 161), timeout=timeout, retries=retries),
                ContextData(),
                ObjectType(ObjectIdentity(self.utcType2OperationMode), ),
            )
            val = varBinds[0][1].prettyPrint()

        if str(val) == '1':
            async with lock:
                errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
                    SnmpEngine(),
                    CommunityData(self.community),
                    UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
                    ContextData(),
                    # ObjectType(ObjectIdentity(oid), value),
                    ObjectType(ObjectIdentity(self.utcType2OperationModeTimeout), Integer32(90)),
                    ObjectType(ObjectIdentity(self.utcType2OperationMode), Integer32(2)),

                )
            errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
                ContextData(),
                ObjectType(ObjectIdentity(self.utcType2OperationMode), Integer32(3)),
            )

        elif str(val) in ('2', '3'):
            async with lock:
                errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
                    SnmpEngine(),
                    CommunityData(self.community),
                    UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
                    ContextData(),
                    ObjectType(ObjectIdentity(self.utcType2OperationMode), Integer32(3)),
                )
        else:
            return

        errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
            SnmpEngine(),
            CommunityData(self.community),
            UdpTransportTarget((self.ip_adress, 161), timeout=1, retries=2),
            ContextData(),
            # ObjectType(ObjectIdentity(oid), value),
            ObjectType(ObjectIdentity(self.utcControlLO + self.scn), Integer32(value)),
        )


class AvailableProtocolsManagement(Enum):
    """ Протоколы управления """
    POTOK_UG405 = 'POTOK_UG405'
    POTOK_STCIP = 'POTOK_STCIP'
    SWARCO_STCIP = 'SWARCO_STCIP'
    SWARCO_SSH = 'SWARCO_SSH'
    PEEK_UG405 = 'PEEK_UG405'
    PEEK_WEB = 'PEEK_WEB'


class Controller:

    def __new__(cls, ip_adress, type_object, scn: str = None, num_host: str = None):
        print('ya в new')
        print(type_object)

        if type_object == AvailableProtocolsManagement.POTOK_STCIP.value:
            return PotokS(ip_adress, num_host)
        elif type_object == AvailableProtocolsManagement.POTOK_UG405.value:
            return PotokP(ip_adress, scn, num_host)
        elif type_object == AvailableProtocolsManagement.SWARCO_STCIP.value:
            return SwarcoSTCIP(ip_adress, num_host)
        elif type_object == AvailableProtocolsManagement.SWARCO_SSH.value:
            return SwarcoSSH(ip_adress, num_host)
        elif type_object == AvailableProtocolsManagement.PEEK_UG405.value:
            return PeekUG405(ip_adress, scn, num_host)
        elif type_object == AvailableProtocolsManagement.PEEK_WEB.value:
            return PeekWeb(ip_adress, num_host)


class GetDataControllerManagement:
    statusMode = {
        '3': 'Сигналы выключены(ОС)',
        '4': 'Жёлтое мигание',
        '5': 'Заблокирован инспектором',
        '6': 'Кругом Красный',
        '8': 'Адаптивный',
        '10': 'Ручное управление',
        '11': 'Удалённое управление',
        '12': 'Фиксированный',
        '00': 'Ошибка электрической цепи',
        '14': 'Жёлтое мигание по расписанию',
        '--': 'Нет данных',
    }

    protocols = ('Поток_UG405', 'Поток_STCIP', 'Swarco_STCIP', 'Peek_UG405')
    snmp_set_request = ('фаза snmp', 'ос', 'жм', 'кк')
    swarco_ssh = ('фаза man',)

    peek_web = ('фаза MAN',)

    def __init__(self, data=None):
        self.data = data

    # def create_snmp_object_get_request(self, num_host, ip_adress, protocol, scn):
    #     # protocols = ('Поток_UG405', 'Поток_STCIP', 'Swarco_STCIP', 'Peek_UG405')
    #     protocols = ('ПОТОК (P)', 'ПОТОК (S)', 'SWARCO', 'PEEK')
    #     obj = None
    #     protocol = protocol.upper()
    #     if protocol == protocols[0]:
    #         obj = PotokP(ip_adress, scn, num_host, )
    #     elif protocol == protocols[1]:
    #         obj = PotokS(ip_adress, num_host, )
    #     elif protocol == protocols[2]:
    #         obj = SwarcoSTCIP(ip_adress, num_host, )
    #     elif protocol == protocols[3]:
    #         obj = PeekUG405(ip_adress, scn, num_host, )
    #     return obj

    # def create_object_for_get_request(self, num_host: str, controller_type: str, ip_adress: str, scn: str = None):
    #
    #     if controller_type == AvailableControllers.POTOK_P.value:
    #         return snmp_managemement_v3.PotokP(ip_adress, scn, num_host)
    #     elif controller_type == AvailableControllers.POTOK_S.value:
    #         return snmp_managemement_v3.PotokS(ip_adress, num_host)
    #     elif controller_type == AvailableControllers.SWARCO.value:
    #         return snmp_managemement_v3.SwarcoSTCIP(ip_adress, num_host)
    #     elif controller_type == AvailableControllers.PEEK.value:
    #         return snmp_managemement_v3.PeekUG405(ip_adress, scn, num_host)

    # def create_set_request(self, num_host, ip_adress, protocol, scn, command, value):
    #
    #     obj = None
    #
    #     if protocol == self.protocols[0]:
    #         obj = PotokP(ip_adress, scn)
    #     elif protocol == self.protocols[1]:
    #         obj = PotokS(ip_adress, num_host, )
    #     elif protocol == self.protocols[2]:
    #         if command in self.swarco_ssh:
    #             obj = SwarcoSSH(ip_adress, )
    #         elif command in self.snmp_set_request:
    #             obj = SwarcoSTCIP(ip_adress, )
    #     elif protocol == self.protocols[3]:
    #         if command in self.snmp_set_request:
    #             obj = PeekUG405(ip_adress, scn)
    #         elif command in self.peek_web:
    #             pass  # Тут необходимо создать экземпляр класса PeekWeb
    #     return obj

    # async def main(self):
    #     tasks = []
    #     for num_host, data in self.data.items():
    #         data = data.split(';')
    #         if len(data) != 3:
    #             continue
    #         ip_adress, protocol, scn = data
    #         host = self.create_snmp_object_get_request(num_host, ip_adress, protocol, scn)
    #         if host is None:
    #             return
    #         tasks.append(host.get_current_mode())
    #
    #     start_time = time.time()
    #     result = await asyncio.gather(*tasks)
    #     print(f'Время выполнения: {time.time() - start_time}')
    #
    #     print(result)
    #     return result

    async def main(self, tasks_inner, option):
        print(tasks_inner)

        if tasks_inner is None or option is None:
            return

        if option == 'set':
            tasks = [method(value) for method, value in tasks_inner]
        elif option == 'get':
            tasks = [method() for method in tasks_inner]
        else:
            return False

        start_time = time.time()
        result = await asyncio.gather(*tasks)
        print(f'Время выполнения: {time.time() - start_time}')

        print(result)
        return result

    def data_processing(self, raw_data):

        processed_data = {}

        for host_data in raw_data:
            if not host_data and len(host_data) != 3:
                continue
            obj, num_host, varBinds = host_data
            if not varBinds:
                processed_data[num_host] = 'Хост недоступен'
            # print(f'host data --> {host_data}')
            if isinstance(obj, SwarcoSTCIP):
                processed_data[num_host] = self.make_data_for_swarco(obj, varBinds)
            elif isinstance(obj, PotokP):
                processed_data[num_host] = self.make_data_for_potokP(obj, varBinds)
            elif isinstance(obj, PotokS):
                processed_data[num_host] = self.make_data_for_potokS(obj, varBinds)
            elif isinstance(obj, PeekUG405):
                processed_data[num_host] = self.make_data_for_peek(obj, web_content=varBinds)
            else:
                raise ValueError
        return processed_data

        #         num_host, protocol, varBinds = host_data
        #         if protocol == protocols[0]:
        #             stage = get_val_stage_UG405_POTOK.get(varBinds[0][1].prettyPrint())
        #             # print(f'stage UG = {stage}')
        #             # print(f'get_val_stage_UG405_POTOK = {get_val_stage_UG405_POTOK}')
        #             plan = varBinds[1][1].prettyPrint()
        #             plan_source = varBinds[2][1].prettyPrint()
        #             det_err = varBinds[3][1].prettyPrint()
        #             allowBitTO = varBinds[4][1].prettyPrint()
        #             local_adaptiv = varBinds[5][1].prettyPrint()
        #             manual = varBinds[6][1].prettyPrint()
        #             electrics = varBinds[7][1].prettyPrint()
        #             # operMode = varBinds[5][1].prettyPrint()
        #             if plan != '0' and plan_source == '1':
        #                 if det_err == '0' and local_adaptiv == '1':
        #                     mode = statusMode.get('8')
        #                 else:
        #                     mode = statusMode.get('12')
        #             elif plan == '0' and plan_source == '2' and allowBitTO == '1':
        #                 mode = statusMode.get('11')
        #             elif manual == '1':
        #                 mode = statusMode.get('10')
        #             elif electrics == '1':
        #                 mode = statusMode.get('00')
        #             else:
        #                 mode = statusMode.get('--')
        #             processed_data[num_host] = f'Фаза={stage} План={plan} Режим={mode}'
        #
        #         elif protocol == protocols[1]:
        #             stage = get_val_stage_STCIP_potok.get(varBinds[0][1].prettyPrint())
        #             plan, control_state, status = (varBinds[1][1].prettyPrint(), varBinds[2][1].prettyPrint(),
        #                                            varBinds[3][1].prettyPrint())
        #             if control_state == '1':
        #                 if status == '8' and plan not in ('0', '16'):
        #                     mode = statusMode.get('8')
        #                 elif status == '12' and plan not in ('0', '16'):
        #                     mode = statusMode.get('12')
        #                 elif status == '11':
        #                     mode = statusMode.get('11')
        #                 elif status == '10':
        #                     mode = statusMode.get('10')
        #                 else:
        #                     mode = statusMode.get('--')
        #                 processed_data[num_host] = f'Фаза={stage} План={plan} Режим={mode}'
        #
        #         elif protocol == protocols[2]:
        #             stage = get_val_stage.get(varBinds[0][1].prettyPrint())
        #             plan, num_detlogics, softinp181 = (varBinds[1][1].prettyPrint(), varBinds[2][1].prettyPrint(),
        #                                                varBinds[3][1].prettyPrint()[180])
        #             if plan == '16':
        #                 mode = statusMode.get('11')
        #             elif plan == '15':
        #                 mode = statusMode.get('10')
        #             elif softinp181 == '1' or num_detlogics == '0':
        #                 mode = statusMode.get('12')
        #             elif softinp181 == '0' and num_detlogics.isdigit() and int(num_detlogics) > 2:
        #                 mode = statusMode.get('8')
        #             else:
        #                 mode = statusMode.get('--')
        #             processed_data[num_host] = f'Фаза={stage} План={plan} Режим={mode}'
        #         elif protocol == protocols[3]:
        #             if 'Нет соединения с хостом' in varBinds:
        #                 processed_data[num_host] = varBinds
        #                 continue
        #
        #             state = mode = None
        #             for line in varBinds.split('\n'):
        #                 if 'T_PLAN' in line:
        #                     plan = line.replace(':D;;##T_PLAN##;', '').replace('-', '').replace(' ', '')
        #                 elif ':SUBTITLE' in line:
        #                     adress = line.replace(':SUBTITLE;Moscow:', '')
        #                 elif 'T_STATE' in line:
        #                     state = line.replace(':D;;##T_STATE##;', '')
        #
        #                 elif 'T_MODE' in line:
        #                     mode, stage = line.replace(':D;;##T_MODE## (##T_STAGE##);', '').split()
        #                     stage = stage.replace('(', '').replace(')', '')
        #                     break
        #
        #             print(f'state -> {state}')
        #
        #             if stage.isdigit() and int(stage) > 0 and state.strip() in state_CONTROL:
        #                 if mode == modeVA:
        #                     mode = statusMode.get('8')
        #                 elif mode == modeFT:
        #                     mode = statusMode.get('12')
        #                 elif mode == modeMAN:
        #                     mode = statusMode.get('10')
        #                 elif mode == modeUTC:
        #                     mode = statusMode.get('11')
        #
        #             elif state.strip() == state_FLASH:
        #                 mode = statusMode.get('4')
        #             elif state.strip() == state_OFF:
        #                 mode = statusMode.get('3')
        #             elif state.strip() == state_blocked_inspector:
        #                 mode = statusMode.get('5')
        #             else:
        #                 mode = statusMode.get('--')
        #
        #             processed_data[num_host] = f'Фаза={stage} План={plan} Режим={mode}'
        #
        #
        # return processed_data

    def validate_varBinds_swarco(self, varBinds):

        # full oid swarcoSoftIOStatus = '1.3.6.1.4.1.1618.5.1.1.1.1.0'

        # SNMPv2-SMI::enterprises.1618.5.1.1.1.1.0 -> таим будет отображение в oid.prettyPrint() из varbinds
        # Возьмем маску опредедения оида swarcoSoftIOStatus(после 1618)
        swarcoSoftIOStatus = '5.1.1.1.1.0'

        if not varBinds:
            return False

        for oid, val in varBinds:
            if oid.prettyPrint().split('1618.')[-1] == swarcoSoftIOStatus:
                print(f'oid -> {oid.prettyPrint()}, val:  {val.prettyPrint()}')
                print(
                    f'oid.prettyPrint().split("1618.")[-1] -> {oid.prettyPrint().split("1618.")[-1]}, val:  {val.prettyPrint()}')
                if len(val.prettyPrint()) < 180:
                    return False
        return True

    def validate_varBinds_potokS(self, varBinds):

        if not varBinds:
            return False
        return True

    def validate_varBinds_potokP(self, varBinds):

        if not varBinds:
            return False
        return True

    def validate_varBinds_peek(self, web_content):

        if not web_content:
            return False
        return True

    def make_data_for_swarco(self, obj, varBinds):

        result_check_varBinds = self.validate_varBinds_swarco(varBinds)

        if not result_check_varBinds:
            return f'Сбой получения данных. Проверьте ДК'

        equipment_status = str(varBinds[0][1].prettyPrint())
        stage = obj.get_val_stage.get(varBinds[1][1].prettyPrint())
        plan = varBinds[2][1].prettyPrint()
        num_det_logics = varBinds[3][1].prettyPrint()
        softstat180_181 = varBinds[4][1].prettyPrint()[179:181] if len(varBinds[4][1].prettyPrint()) > 180 else '01'

        if equipment_status != '1':
            if equipment_status == '3':
                return f'Режим={self.statusMode.get("3")}'
            elif equipment_status == '4':
                return f'Режим={self.statusMode.get("4")}'
            elif equipment_status == '6':
                return f'Режим={self.statusMode.get("6")}'
            else:
                return f'Режим={self.statusMode.get("--")}'

        if plan == '16':
            mode = self.statusMode.get('11')
        elif plan == '15':
            mode = self.statusMode.get('10')
        elif '1' in softstat180_181 or num_det_logics == '0':
            mode = self.statusMode.get('12')
        elif softstat180_181 == '00' and num_det_logics.isdigit() and int(num_det_logics) > 2:
            mode = self.statusMode.get('8')
        else:
            mode = self.statusMode.get('--')

        return f'Фаза={stage} План={plan} Режим={mode}'

    def make_data_for_potokS(self, obj, varBinds):
        """
        equipment_status -> статусы работы: рабочая программа(1), ОС(3), ЖМ(4), КК(6)
        status_mode -> текущий режим:
                                    8 -  фиксированное управление (Ф)
                                    10 - ручное управление (Р)
                                    11 - удаленное управление (Ц)
                                    12 - адаптивное управление (A)
        :param obj: instance, для взятия номера фазы
        :param varBinds: oid + values
        :return: фаза, план, режим
        """

        result_check_varBinds = self.validate_varBinds_potokS(varBinds)

        if not result_check_varBinds:
            return f'Сбой получения данных. Проверьте ДК'

        equipment_status = str(varBinds[0][1].prettyPrint())
        status_mode = str(varBinds[1][1].prettyPrint())
        stage = obj.get_val_stage.get(varBinds[2][1].prettyPrint())
        plan = varBinds[3][1].prettyPrint()

        if equipment_status != '1':
            if equipment_status == '3':
                return f'Режим={self.statusMode.get("3")}'
            elif equipment_status == '4':
                return f'Режим={self.statusMode.get("4")}'
            elif equipment_status == '6':
                return f'Режим={self.statusMode.get("6")}'
            else:
                return f'Режим={self.statusMode.get("--")}'

        if status_mode == '11' and plan == '16':
            mode = self.statusMode.get('11')
        elif status_mode == '12':
            mode = self.statusMode.get('12')
        elif status_mode == '8':
            mode = self.statusMode.get('8')
        elif status_mode == '10':
            mode = self.statusMode.get('10')
        else:
            mode = self.statusMode.get('--')

        return f'Фаза={stage} План={plan} Режим={mode}'

    def make_data_for_potokP(self, obj, varBinds):

        result_check_varBinds = self.validate_varBinds_potokP(varBinds)

        if not result_check_varBinds:
            return f'Сбой получения данных. Проверьте ДК'

        utcType2OperationMode = str(varBinds[0][1].prettyPrint())
        hasErrors = str(varBinds[1][1].prettyPrint())
        isFlash = str(varBinds[2][1].prettyPrint())
        isDark = str(varBinds[3][1].prettyPrint())
        isManual = str(varBinds[4][1].prettyPrint())
        plan = str(varBinds[5][1].prettyPrint())
        stage = obj.val_stage_get_request.get(str(varBinds[6][1].prettyPrint()).split('x')[-1])
        hasDetErrors = str(varBinds[7][1].prettyPrint())
        localAdaptiv = str(varBinds[8][1].prettyPrint())

        # print(f'isFlash: {isFlash}')
        # print(f'hasDetErrors: {hasDetErrors}')
        # print(f'localAdaptiv: {localAdaptiv}')
        # print(f'plan: {plan}')
        # print(f'utcType2OperationMode: {utcType2OperationMode}')

        if isFlash.isdigit() and int(isFlash) in range(1, 5):
            return f'Режим={self.statusMode.get("4")}'
        if isDark == '1':
            return f'Режим={self.statusMode.get("3")}'
        if isManual == '1':
            return f'Режим={self.statusMode.get("10")}'

        if utcType2OperationMode == '3' and plan == '0':
            mode = self.statusMode.get('11')
        elif localAdaptiv == '1' and hasDetErrors == '0' and plan != '0':
            mode = self.statusMode.get('8')
        elif (localAdaptiv == '0' or hasDetErrors == '1') and plan != '0':
            mode = self.statusMode.get('12')
        else:
            mode = self.statusMode.get("--")

        return f'Фаза={stage} План={plan} Режим={mode}'

    def make_data_for_peek(self, obj, web_content):
        result_check_varBinds = self.validate_varBinds_potokP(web_content)

        if not result_check_varBinds:
            return f'Сбой получения данных. Проверьте ДК'

        state = mode = stage = plan = None
        for line in web_content.split('\n'):
            if 'T_PLAN' in line:
                plan = line.replace(':D;;##T_PLAN##;', '').replace('-', '').replace(' ', '')
            elif ':SUBTITLE' in line:
                adress = line.replace(':SUBTITLE;Moscow:', '')
            elif 'T_STATE' in line:
                state = line.replace(':D;;##T_STATE##;', '')

            elif 'T_MODE' in line:
                mode, stage = line.replace(':D;;##T_MODE## (##T_STAGE##);', '').split()
                stage = stage.replace('(', '').replace(')', '')
                break

        print(f'state -> {state}')

        if stage is not None and stage.isdigit() and int(stage) > 0 and state.strip() in obj.state_CONTROL:
            if mode == obj.modeVA:
                mode = self.statusMode.get('8')
            elif mode == obj.modeFT:
                mode = self.statusMode.get('12')
            elif mode == obj.modeMAN:
                mode = self.statusMode.get('10')
            elif mode == obj.modeUTC:
                mode = self.statusMode.get('11')

        elif state is not None and state.strip() == obj.state_FLASH:
            mode = self.statusMode.get('4')
        elif state is not None and state.strip() == obj.state_OFF:
            mode = self.statusMode.get('3')
        elif state is not None and state.strip() == obj.state_blocked_inspector:
            mode = self.statusMode.get('5')
        else:
            mode = self.statusMode.get('--')

        return f'Фаза={stage} План={plan} Режим={mode}'


"""" SSH MANAGEMENT """


class ConnectionSSH:
    access_levels = {
        'swarco_itc': ('itc', 'level1NN'),
        'swarco_r': ('root', 'N1eZ4pC'),
        'peek_r': ('root', 'peek'),
    }

    @classmethod
    def create_ssh_session(cls, ip_adress, access_level):

        login, password = cls.access_levels.get(access_level)

        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            client.connect(hostname=ip_adress,
                           username=login,
                           password=password,
                           look_for_keys=False, allow_agent=False)
            message = f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} < Соединение установлено >'
        except paramiko.ssh_exception.NoValidConnectionsError as err:
            client = None
            message = f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} Не удалось установить соединение с хостом...'
        except paramiko.ssh_exception.AuthenticationException as err:
            client = None
            message = f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} Ошибка авторизации...'
        except TimeoutError as err:
            client = None
            message = f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} Ошибка таймаута подключения...'
        except:
            client = None
            message = f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} Программный сбой подключения...'
        return client, message


class SwarcoSSH(ConnectionSSH):
    inp_stages = {str(stage): str(inp) for stage, inp in zip(range(1, 9), range(104, 112))}

    def __init__(self, ip_adress: str, num_host: str = None):
        self.ip_adress = ip_adress

    @staticmethod
    def make_any_commands(commands_from_user, separ=','):
        return (command + '\n' for command in commands_from_user.split(separ))

    @staticmethod
    def commands_set_stage(stage_inp):
        return 'inp102=1\n', f'inp{SwarcoSSH.inp_stages.get(stage_inp)}=1\n', 'instat102 ?\n'

    @staticmethod
    def commands_l2():
        login, password = 'l2', '2727'
        return 'lang UK\n', f'{login}\n', f'{password}\n'

    @staticmethod
    def commands_reset_inp104_111():
        return (f'inp{inp}=0\n' for inp in range(104, 112))

    @staticmethod
    def commands_reset_inp102_111():
        return (f'inp{inp}=0\n' if inp < 112 else 'instat102 ?\n' for inp in range(102, 113) if inp != 103)

    def send_commands_to_shell(self, commands, output='standard output'):
        """
        Принимает на вход коллекию commands и рекурсивно отравляет команды из данной коллекции
        в shell для логина itc(команды должны быть доступны для логина itc(terminal communication))
        :param commands: Итерируемый объект
        :param output: опция вывода сессии:
                                           'standard output' -> полный вывод всей сесии
                                           'inputs102_111' - > сотсояние входов со 102 по 112
        :return: вывод сесии в виде строки
        """

        short_sleep = 0.4
        recieve_bytes = 6000
        client, message = self.create_ssh_session(self.ip_adress, 'swarco_itc')

        if client is None:
            return
        print(f'ssh_commands: {commands}')

        with client.invoke_shell() as ssh:
            for command in itertools.chain(*commands, 'exit\n'):
                ssh.send(command)
                time.sleep(short_sleep)
            res = ssh.recv(recieve_bytes).decode(encoding="latin-1")
            if output == 'inputs102_111':
                res = f'23456789012\n{res.split(": ")[-1].split()[0][:11]}'
            else:
                res = res.split('l2')[-1]
        return res

    def manage_send_commands_to_shell(self, type_request, val, output=None, separ=',') -> str:
        """
        Метод является менеджером для подготовки отпраки команд в shell
        :param type_request: тип команд
        :param val: команды, в зависимости от type_request.
                    Примеры:
                            type_request = 'фаза', то в val нужно передать номер фазы.
                            type_request = 'терминальная команда', в val передаем строку
                                            команд в виде 'inp102=1,inp108=1,ws4 10 1, ws3 170 0... и т.д', т.е. любая
                                            команда доступная из terminal communication через разделитель(по
                                            умолчанию это ','

        :param output: опция, какой вывод вернуть после завершения сесии(см. в методе 'send_commands_to_shell')
        :param separ: разделитель команд для val
        :return: вывод сесии ssh
        """
        res = None
        if 'фаза' in type_request:
            commands = (SwarcoSSH.commands_l2(),
                        SwarcoSSH.commands_reset_inp104_111(),
                        SwarcoSSH.commands_set_stage(val),
                        )
            res = self.send_commands_to_shell(commands, output)
        elif 'терминальная команда' in type_request:
            commands = (SwarcoSSH.commands_l2(),
                        SwarcoSSH.make_any_commands(val, separ=separ)
                        )
            res = self.send_commands_to_shell(commands)
        return res

    def set_stage(self, val):

        if str(val.lower()) in ('reset', 'false', '0'):
            commands = (SwarcoSSH.commands_l2(), SwarcoSSH.commands_reset_inp102_111())
        elif val.isdigit() and int(val) in range(1, 9):
            commands = (SwarcoSSH.commands_l2(),
                        SwarcoSSH.commands_reset_inp104_111(),
                        SwarcoSSH.commands_set_stage(val),
                        )
        else:
            return
        res = self.send_commands_to_shell(commands, output='inputs102_111')
        # res = self.send_commands_to_shell(commands, )
        # print('res')
        print(res)
        return res


"""" WEB MANAGEMENT """


class PeekWeb:
    MAN_INPUTS = {'MPP_MAN', 'MPP_FL', 'MPP_OFF', 'MPP_PH1', 'MPP_PH2', 'MPP_PH3',
                  'MPP_PH4', 'MPP_PH5', 'MPP_PH6', 'MPP_PH7', 'MPP_PH8'}
    MAN_INPUTS_STAGES = {'MPP_PH1', 'MPP_PH2', 'MPP_PH3', 'MPP_PH4',
                         'MPP_PH5', 'MPP_PH6', 'MPP_PH7', 'MPP_PH8'}

    actuator_values = {
        'ВФ': '//*[@id="button_div"]/ul/li[1]/button',
        'ВЫКЛ': '//*[@id="button_div"]/ul/li[2]/button',
        'ВКЛ': '//*[@id="button_div"]/ul/li[3]/button'
    }

    allowed_inputs = {'MKEY1', 'MKEY2', 'MKEY3', 'MKEY4', 'MKEY5',
                      'MPP_MAN', 'MPP_FL', 'MPP_OFF', 'MPP_PH1', 'MPP_PH2', 'MPP_PH3', 'MPP_PH4', 'MPP_PH5',
                      'MPP_PH6', 'MPP_PH7', 'MPP_PH8',
                      'CP_OFF', 'CP_FLASH', 'CP_RED', 'CP_AUTO'}

    button_3_entrance = '//*[@id="buttonpad"]/form[1]/ul[1]/li[3]/button'
    button_entrance = '//*[@id="buttonpad"]/form[1]/ul[4]/li/button'

    span_refresh_change = '//*[@id="refresh_button"]'
    span_start = '//*[@id="mainnav"]/li[1]/a'

    def __init__(self, ip_adress: str, num_host: str = None):
        self.ip_adress = ip_adress
        self.driver = None

        self.short_pause = 0.5
        self.middle_pause = 1
        self.long_pause = 4
        # print(f'timeout из init:')
        # print(f'self.short_pause: {self.short_pause}')
        # print(f'self.middle_pause: {self.middle_pause}')
        # print(f'self.long_pause: {self.long_pause}')

        # span_user_inputs = '//*[@id="mainnav"]/li[6]/ul/li[10]/ul/li[4]/a/span'   оригинал :)
        ###########################################################################################

    @staticmethod
    def _make_inputs_and_user_parameters(inputs, user_parameters):
        set_stageMAN = reset_stageMAN = set_reset_dark = set_reset_flash = False
        if inputs:
            inps_dict = {}
            for inp, val in (i.split('=') for i in inputs):
                inps_dict[inp] = val
                set_stageMAN = True if inp == 'MPP_MAN' and val == 'ВКЛ' else False
                reset_stageMAN = True if inp == 'MPP_MAN' and val in ('ВЫКЛ, ВФ') else False
                set_reset_flash = True if inp == 'MPP_FL' else False
                set_reset_dark = True if inp == 'MPP_OFF' else False
        else:
            inps_dict = None
        if user_parameters:
            # user_parameters = (i.split('=') for i in user_parameters)
            # user_parameters = {i[0]: i[1] for i in user_parameters}
            user_parameters_dict = {inp: val for inp, val in (up.split('=') for up in user_parameters)}
        else:
            user_parameters_dict = None
        return inps_dict, user_parameters_dict

    def _start_and_login(self):
        """ Метод, в котором производится нажатие в нужные элементы чтобы залогинится """

        time.sleep(self.middle_pause)
        self.driver.switch_to.parent_frame()
        self.driver.switch_to.frame('menu_frame')

        ### Пример поиска элемента
        # content = driver.find_elements(By.TAG_NAME, "span")
        # content = [el.text for el in content]
        # print(content)

        element = self.driver.find_element(By.TAG_NAME, 'ul')
        element = element.find_elements(By.TAG_NAME, 'li')
        main_page = [el.text for el in element]

        if 'Рисунок перекрёстка' in main_page:
            span_entrance = f'//*[@id="mainnav"]/li[3]/a'
            span_user_inputs = '//*[@id="mainnav"]/li[7]/ul/li[10]/ul/li[4]/a/span'
            span_user_parameters = '//*[@id="mainnav"]/li[6]/ul/li[3]/a/span'
        else:
            span_entrance = '//*[@id="mainnav"]/li[2]/a'
            span_user_inputs = '//*[@id="mainnav"]/li[6]/ul/li[10]/ul/li[4]/a/span'
            span_user_parameters = '//*[@id="mainnav"]/li[5]/ul/li[3]/a/span'
        # Клик в Вход
        element_input = self.driver.find_element(By.XPATH, span_entrance)
        element_input.click()
        time.sleep(self.middle_pause)
        # Логинимся 3333
        self.driver.switch_to.parent_frame()
        self.driver.switch_to.frame('content_frame')
        element_input = self.driver.find_element(By.XPATH, self.button_3_entrance)
        for i in range(4):
            element_input.click()
        element_input = self.driver.find_element(By.XPATH, self.button_entrance)
        element_input.click()
        time.sleep(self.middle_pause)

        return span_user_inputs, span_user_parameters

    def _detect_span_inputs_and_user_parameterts(self):
        time.sleep(self.middle_pause)
        self.driver.switch_to.parent_frame()
        self.driver.switch_to.frame('menu_frame')

        element = self.driver.find_element(By.TAG_NAME, 'ul')
        element = element.find_elements(By.TAG_NAME, 'li')
        main_page = [el.text for el in element]
        # print(main_page)
        if 'Рисунок перекрёстка' in main_page:
            span_entrance = f'//*[@id="mainnav"]/li[3]/a'
            span_user_inputs = '//*[@id="mainnav"]/li[7]/ul/li[10]/ul/li[4]/a/span'
            span_user_parameters = '//*[@id="mainnav"]/li[6]/ul/li[3]/a/span'
        else:
            span_entrance = '//*[@id="mainnav"]/li[2]/a'
            span_user_inputs = '//*[@id="mainnav"]/li[6]/ul/li[10]/ul/li[4]/a/span'
            span_user_parameters = '//*[@id="mainnav"]/li[5]/ul/li[3]/a/span'

        return span_user_inputs, span_user_parameters

    def _set_INPUTS(self, num_inp, actuator_val):
        # Двойной клик в нужный вход в колонке АКТУАТОР:

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, f'//*[@id="data"]/table/tbody/tr[{num_inp}]/td[5]')))
        element_input = self.driver.find_element(By.XPATH,
                                                 f'//*[@id="data"]/table/tbody/tr[{num_inp}]/td[5]')
        action = ActionChains(self.driver)
        action.double_click(element_input)
        action.perform()
        time.sleep(self.short_pause)
        # Клик в АКТУАТОР(ВКЛ/ВЫКЛ/ВФ)
        actuator_value = self.actuator_values.get(actuator_val)
        element_input = self.driver.find_element(By.XPATH, actuator_value)
        element_input.click()
        time.sleep(self.middle_pause)

    def _set_USER_PARAMETERS(self, id_user_parameter, value):
        """ Метод, в котором осуществляется клик в нужное значение нужного параметра программы(юзер-параметра)
            В цикле for на каждой итерации осуществляется клик в парметр программы(по индексу), который
            является ключом словаря, затем клик в значение(значение словаря)
            :param dict filtered_user_parameters_to_set: словарь с офтильтрованнами параметрами программы.
        """

        # button_1_UP = '//*[@id="buttonpad"]/ul[1]/li[1]/button'
        # button_2_UP = '//*[@id="buttonpad"]/ul[1]/li[2]/button'
        # button_3_UP = '//*[@id="buttonpad"]/ul[1]/li[3]/button'
        # button_4_UP = '//*[@id="buttonpad"]/ul[2]/li[1]/button'
        # button_5_UP = '//*[@id="buttonpad"]/ul[2]/li[2]/button'
        # button_6_UP = '//*[@id="buttonpad"]/ul[2]/li[3]/button'
        # button_7_UP = '//*[@id="buttonpad"]/ul[3]/li[1]/button'
        # button_8_UP = '//*[@id="buttonpad"]/ul[3]/li[2]/button'
        # button_9_UP = '//*[@id="buttonpad"]/ul[3]/li[3]/button'
        # button_0_UP = '//*[@id="buttonpad"]/ul[4]/li[1]/button'
        # button_OK_UP = '//*[@id="buttonpad"]/ul[4]/li[4]/button'

        buttons = {'1': '//*[@id="buttonpad"]/ul[1]/li[1]/button', '2': '//*[@id="buttonpad"]/ul[1]/li[2]/button',
                   '3': '//*[@id="buttonpad"]/ul[1]/li[3]/button', '4': '//*[@id="buttonpad"]/ul[2]/li[1]/button',
                   '5': '//*[@id="buttonpad"]/ul[2]/li[2]/button', '6': '//*[@id="buttonpad"]/ul[2]/li[3]/button',
                   '7': '//*[@id="buttonpad"]/ul[3]/li[1]/button', '8': '//*[@id="buttonpad"]/ul[3]/li[2]/button',
                   '9': '//*[@id="buttonpad"]/ul[3]/li[3]/button', '0': '//*[@id="buttonpad"]/ul[4]/li[1]/button',
                   'OK': '//*[@id="buttonpad"]/ul[4]/li[4]/button'
                   }

        up_index = f'//*[@id="data"]/table/tbody/tr[{id_user_parameter}]/td[3]'
        element_input = self.driver.find_element(By.XPATH, up_index)
        action = ActionChains(self.driver)
        action.double_click(element_input)
        action.perform()
        time.sleep(self.short_pause)
        for number in value:
            self.driver.find_element(By.XPATH, buttons.get(number)).click()
            time.sleep(self.short_pause)
        # # Клик в OK
        element_input = self.driver.find_element(By.XPATH, buttons.get('OK'))
        element_input.click()
        time.sleep(self.short_pause)

    def _goto_content_frame(self, span_name):
        self.driver.switch_to.parent_frame()
        self.driver.switch_to.frame('menu_frame')
        # Клик во ВВОДЫ/Параметры программы(в зависимости что передано в span_name)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, span_name)))
        element_input = self.driver.find_element(By.XPATH, span_name)
        element_input.click()
        time.sleep(self.middle_pause)
        # Клик в обновить/изменить
        self.driver.switch_to.parent_frame()
        time.sleep(self.short_pause)
        self.driver.switch_to.frame('inst_frame')
        time.sleep(self.short_pause)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, self.span_refresh_change)))
        element_input = self.driver.find_element(By.XPATH, self.span_refresh_change)
        element_input.click()
        time.sleep(self.middle_pause)
        # Переход в content_frame чтобы далее устанавливать значения(для INPUTS или USER_PARAMETERS)
        self.driver.switch_to.parent_frame()
        self.driver.switch_to.frame('content_frame')
        time.sleep(self.short_pause)

    def _click_to_span_refresh(self):
        # Клик в обновить/изменить
        self.driver.switch_to.parent_frame()
        time.sleep(self.short_pause)
        # self.driver.switch_to.parent_frame()
        self.driver.switch_to.frame('inst_frame')
        time.sleep(self.short_pause)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, self.span_refresh_change)))
        element_input = self.driver.find_element(By.XPATH, self.span_refresh_change)
        element_input.click()
        time.sleep(self.middle_pause)

    def _make_curr_inputs_and_states(self):

        table_INPUTS = self.driver.find_element(By.TAG_NAME, 'table')
        table_INPUT_elements = table_INPUTS.find_elements(By.TAG_NAME, 'tr')

        MPP_INPUTS = ('MPP_PH1', 'MPP_PH2', 'MPP_PH3', 'MPP_PH4', 'MPP_PH5', 'MPP_PH6', 'MPP_PH7',
                      'MPP_PH8', 'MPP_FL', 'MPP_OFF')

        INPS = {}
        for num_row, row_content in enumerate([el.text.split() for el in table_INPUT_elements]):
            if len(row_content) == 5 and num_row > 0:
                num, name, state, time_state, actuator_val = row_content
                if name in MPP_INPUTS and actuator_val == '-' and state == '1':
                    INPS[name] = num, state, actuator_val
                elif name == 'MPP_MAN':
                    MPP_MAN = (num, state, actuator_val)
            else:
                continue
        print('INPS:')
        print(INPS)
        return INPS

    def _manage_set_inputs(self, inputs, set_man=False, reset_man=False):

        table_INPUTS = self.driver.find_element(By.TAG_NAME, 'table')
        table_INPUT_elements = table_INPUTS.find_elements(By.TAG_NAME, 'tr')

        inputs_to_set = {}

        print(f'set_man: {set_man}')
        print(f'reset_man: {reset_man}')

        print(inputs)
        print('----!!!!--------')
        for row in [el.text.split() for el in table_INPUT_elements]:
            # if not inputs:
            #     break

            # Проверка корректности считанных данных
            if len(row) == 5:
                num, name, state, time_state, actuator_val = row
            else:
                continue

            # Если необходимо установить фазу, добавляем в inputs_to_set
            if name == 'MPP_MAN' and set_man:
                if state != '1':
                    print(*row)
                    inputs_to_set[name] = num, 'ВКЛ'
                continue
            # Если необходимо установить фазу и у какого то ввода MPP_PHx значение 1, то его добавляем в inputs_to_set
            if set_man and name in self.MAN_INPUTS_STAGES and name not in inputs and state == '1':
                inputs_to_set[name] = num, 'ВЫКЛ'
                continue

            if name in inputs:
                inputs_to_set[name] = num, inputs.get(name)
                inputs.pop(name)

        print(f'-- inputs_to_set 1 -- {inputs_to_set}')
        if set_man and 'MPP_MAN' in inputs_to_set.keys():
            inputs_to_set['MPP_MAN'] = inputs_to_set.pop('MPP_MAN')
        elif reset_man:
            tmp_inputs = {'MPP_MAN': inputs_to_set.pop('MPP_MAN')}
            inputs_to_set = tmp_inputs | inputs_to_set
            print(f'-- inputs_to_set -- {inputs_to_set}')

        print(f'-- inputs_to_set перед for -- {inputs_to_set}')
        for num, val in inputs_to_set.values():
            self._set_INPUTS(num, val)

        time.sleep(self.long_pause)

    def session_manager(self, increase_the_timeout=False, inputs=None, user_parameters=None):
        """ Метод создаёт web сессию, в которрй совершаются действия в зависимости от переданных аргументов:
        :param bool increase_the_timeout: увеличивает таймаут с каждым новым вызовом метода у экземпляра
        :param bool session_for_greenroad: если метод вызван для "Зелёной улицы" приложения Engineering_tool_kit,
               то при наличии :arg: resetting_the_desired_values - не будет сбрасывать MPP_MAN
        :param tuple inputs: словарь "Вводов", которые необходимо актировать. Ключ словаря - название Ввода, значение -
               значение Актутора, которое необходимо установить
        :param dict user_parameters: словарь "параметров программы", которые необходимо установить.
               Ключ словаря - str, которая должна содердать ращзделитель "_". Всё, что до "_" -> произольно. После
               "_" -> индекс параметра. Например: UP_2, UP->произвольная часть, 2->индекс параметра.
               Значение словаря - str/int -> значение, которе будет утсановлено в поле "Значение".
               Например: UP_2: 154 -> установить значение 154 для юзер параметра с индексом 2
        :param dict resetting_the_desired_values: ключ - str Актуатор(ВФ, ВЫКЛ, ВКЛ), который будет установлен для
               Вводов, текущее значение которых содержится в tuple значении словаря.
               Например: {'ВЫКЛ: (ВКЛ, )'} - это значит ВЫКЛ будет установлено для всех Вводов, текущее сотсояние
               которых 'ВКЛ'
               Еще пример: {'ВФ: (ВКЛ, ВЫКЛ)'} - это значит ВФ будет установлено для всех Вводов, текущее сотсояние
               которых 'ВКЛ' или 'ВЫКЛ'
        :param kwargs: можно передавать Вводы или параметры программы вместо ipputs/user_parameters.
               Например: MPP_MAN=ВКЛ, MPP_PH1=ВЫКЛ, CP_RED=ВКЛ, UP_1=154, UP_3=1 и т.д.
        :param expected_state_for_greenroad: фаза, которую необходимо включить из Engineering_tool_kit_v1.0 "greenroad"
        """

        if inputs is None and user_parameters is None:
            raise ValueError('inputs и user_parameters могут быть пустыми одновременно')
        elif inputs and not isinstance(inputs, Iterable):
            raise ValueError('inputs должен быть итерируемым объектом')
        elif user_parameters and not isinstance(user_parameters, Iterable):
            raise ValueError('user_parameters должен быть итерируемым объектом')

        if increase_the_timeout:
            self.short_pause += 1
            self.middle_pause += 2
            self.long_pause += 2

        inputs, user_parameters = PeekWeb._make_inputs_and_user_parameters(inputs, user_parameters)

        print(f'inputs = {inputs}, user_parameters = {user_parameters},')
        # print(f'set_stageMAN = {set_stageMAN}, reset_stageMAN = {reset_stageMAN},')
        # print(f'set_reset_flash = {set_reset_flash}, set_reset_dark = {set_reset_dark},')

        ##############################################################

        # Боевой вариант
        options = Options()
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=options)
        self.driver.get('http://' + self.ip_adress)
        time.sleep(self.short_pause)
        self.driver.get('http://' + self.ip_adress + '/hvi?file=dummy.hvi&uic=3333')
        time.sleep(self.short_pause)
        self.driver.get('http://' + self.ip_adress)

        # Тест вариант
        # self.driver = webdriver.Chrome()
        # self.driver.get('http://localhost/')
        # time.sleep(self.short_pause)
        # self.driver.get('http://localhost' + '/hvi?file=dummy.hvi&uic=3333')
        # time.sleep(self.short_pause)
        # self.driver.get('http://localhost/')
        # time.sleep(self.middle_pause)

        span_inputs, span_user_parameters = self._detect_span_inputs_and_user_parameterts()
        time.sleep(self.middle_pause)

        if inputs:
            self.driver.refresh()
            time.sleep(self.short_pause)
            self._goto_content_frame(span_inputs)

            self._manage_set_inputs(inputs)

            # table_INPUTS = self.driver.find_element(By.TAG_NAME, 'table')
            # table_INPUT_elements = table_INPUTS.find_elements(By.TAG_NAME, 'tr')
            #
            # print(inputs)
            # print('----!!!!--------')
            # cnt, len_inputs, num_MPP_MAN = 0, len(inputs), None
            # for row in [el.text.split() for el in table_INPUT_elements]:
            #     if len(row) == 5:
            #         num, name, state, time_state, actuator_val = row
            #     else:
            #         continue
            #     # print(f'num: {num}, name: {name},state: {state},time_state: {time_state},actuator_val: {actuator_val}')
            #     if name not in inputs and set_stage_MAN and name in self.MAN_INPUTS:
            #         if name == 'MPP_MAN' and state == '0':
            #             num_MPP_MAN = num
            #         elif state == '1' and name != 'MPP_MAN':
            #             self._set_INPUTS(num, 'ВЫКЛ')
            #     elif name in inputs:
            #         val_actuator_to_set = inputs.get(name)
            #         val_actuator_to_curr = 'ВФ' if actuator_val == '-' else actuator_val
            #         if val_actuator_to_set != val_actuator_to_curr:
            #             self._set_INPUTS(num, inputs.get(name))
            #             cnt += 1
            # if num_MPP_MAN:
            #     self._set_INPUTS(num_MPP_MAN, 'ВКЛ')
            # Возврат в начало, если не будем далее работать с параметрами программы

        if user_parameters:
            self.driver.refresh()
            self._goto_content_frame(span_user_parameters)

            table_UP = self.driver.find_element(By.TAG_NAME, 'table')
            table_UP_elements = table_UP.find_elements(By.TAG_NAME, 'tr')

            print([el.text for el in table_UP_elements])

            # Установка UP
            cnt, len_inputs = 1, len(inputs)
            for row in [el.text.split() for el in table_UP_elements]:
                if len(row) == 5:
                    num, name, val_cur, val_min, val_max = row
                else:
                    continue
                if name in user_parameters:
                    val_up_to_set = user_parameters.get(name)
                    if val_up_to_set != val_cur:
                        self._set_USER_PARAMETERS(num, val_up_to_set)
                    cnt += 1
                if cnt >= len_inputs:
                    print(f'if cnt >= len_inputs:')
                    break
        self.driver.refresh()
        time.sleep(self.middle_pause)
        self.driver.close()

    def set_stage(self, value, increase_the_timeout=False):
        if increase_the_timeout:
            self.short_pause += 1
            self.middle_pause += 2
            self.long_pause += 2

        ##############################################################

        # Боевой вариант
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        self.driver = webdriver.Chrome(options=options)
        self.driver.get('http://' + self.ip_adress)
        time.sleep(self.short_pause)
        self.driver.get('http://' + self.ip_adress + '/hvi?file=dummy.hvi&uic=3333')
        time.sleep(self.short_pause)
        self.driver.get('http://' + self.ip_adress)

        # Тест вариант
        # self.driver = webdriver.Chrome()
        # self.driver.get('http://localhost/')
        # time.sleep(self.short_pause)
        # self.driver.get('http://localhost' + '/hvi?file=dummy.hvi&uic=3333')
        # time.sleep(self.short_pause)
        # self.driver.get('http://localhost/')
        # time.sleep(self.middle_pause)

        time.sleep(self.middle_pause)

        span_inputs, _ = self._detect_span_inputs_and_user_parameterts()
        time.sleep(self.middle_pause)

        self.driver.refresh()
        time.sleep(self.short_pause)
        self._goto_content_frame(span_inputs)

        if value.isdigit() and int(value) in range(1, 9):
            inputs = {'MPP_MAN': 'ВКЛ', f'MPP_PH{value}': 'ВКЛ'}
            set_man, reset_man = True, False
        elif value.lower() in ('0', 'false', 'reset', 'local', 'сброс', 'локал'):
            inputs = {'MPP_MAN' if i == 0 else f'MPP_PH{i}': 'ВЫКЛ' if i == 0 else 'ВФ' for i in range(9)}
            set_man, reset_man = False, True
        else:
            return

        self._manage_set_inputs(inputs, set_man, reset_man)

    def set_flash(self, value, increase_the_timeout=False):
        if increase_the_timeout:
            self.short_pause += 1
            self.middle_pause += 2
            self.long_pause += 2

        ##############################################################

        # Боевой вариант
        options = Options()
        # options.add_argument('--headless')
        # options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(options=options)
        self.driver.get('http://' + self.ip_adress)
        time.sleep(self.short_pause)
        self.driver.get('http://' + self.ip_adress + '/hvi?file=dummy.hvi&uic=3333')
        time.sleep(self.short_pause)
        self.driver.get('http://' + self.ip_adress)

        # Тест вариант
        # self.driver = webdriver.Chrome()
        # self.driver.get('http://localhost/')
        # time.sleep(self.short_pause)
        # self.driver.get('http://localhost' + '/hvi?file=dummy.hvi&uic=3333')
        # time.sleep(self.short_pause)
        # self.driver.get('http://localhost/')
        # time.sleep(self.middle_pause)

        time.sleep(self.middle_pause)

        span_inputs, _ = self._detect_span_inputs_and_user_parameterts()
        time.sleep(self.middle_pause)

        self.driver.refresh()
        time.sleep(self.short_pause)
        self._goto_content_frame(span_inputs)

        if value.lower() in ('1', 'true', 'set', 'on', 'установить'):
            inputs = {'MPP_FL': 'ВКЛ'}
        elif value.lower() in ('0', 'false', 'reset', 'off', 'сброс'):
            inputs = {'MPP_FL': 'ВЫКЛ'}
        else:
            return

        self._manage_set_inputs(inputs, )





