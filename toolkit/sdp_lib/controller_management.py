"""" Модуль управления/получения данных различных типов контроллеров по различным протоколам """
import abc
import os
from datetime import datetime as dt
from typing import Generator

import asyncssh
from dotenv import load_dotenv

from collections.abc import Iterable, Callable

import itertools
import re
import time
import math
from datetime import datetime
import logging

from enum import Enum
import ipaddress
import asyncio
import paramiko
import aiohttp
from pysnmp.hlapi.asyncio import *


"""*******************************************************************
***                          GET-REQUEST                          ****   
**********************************************************************
"""

load_dotenv()

logger = logging.getLogger(__name__)


class AvailableControllers(Enum):
    """ Доступные типы контроллера и команд"""
    SWARCO = 'Swarco'
    POTOK_P = 'Поток (P)'
    POTOK_S = 'Поток (S)'
    PEEK = 'Peek'


class ErrorMessages(Enum):
    BAD_TYPE_OID = 'Оид должен быть строкой или или атрибутом класса Oids'


class EntityJsonResponce(Enum):
    """ Доступные типы контроллера и команд"""

    RESULT = 'result'
    TYPE_CONTROLLER = 'type_controller'
    TYPE_COMMAND = 'type_command'
    VALUE = 'value'
    REQUEST_ENTITY = 'request_entity'
    RESPONCE_ENTITY = 'responce_entity'

    SET_STAGE_MPP_MAN = 'set_stage_mpp_man'
    SET_MAN_INPUTS_WEB = 'set_inputs'
    SET_USER_PARAMETERS_WEB = 'set_user_parameters'

    TYPE_GET_STATE = ''
    TYPE_REQUEST = 'type_request'
    TYPE_SNMP_REQUEST_SET = 'snmp_set_values'
    TYPE_SNMP_REQUEST_GET = 'snmp_get_values'
    TYPE_SNMP_REQUEST_GET_STATE = 'get_state_on_snmp'
    TYPE_WEB_REQUEST_SET = 'web_set_parameters'
    TYPE_WEB_REQUEST_GET = 'web_get_parameters'
    TYPE_SSH_REQUEST_SET = 'ssh_set_values'

    NO_DATA_FOR_REQ = 'There is no data for the request'


    COMMAND_SEND_SUCCESSFULLY = 'Команда успешно отправлена'
    COMMAND_SEND_ERROR = 'Команда не была отправлена'

    REQUEST_ERRORS = 'request_errors'
    # TIMEOUT_ERROR_GET_REQUEST_MSG = 'ConnectTimeoutError'
    TIMEOUT_ERROR_WEB_REQUEST_MSG = 'ConnectTimeoutError'
    TIMEOUT_ERROR_SNMP_MSG = 'No SNMP response received before timeout'
    BAD_CONTROLLER_TYPE_MSG = 'No Such Object currently exists at this OID'
    TYPE_CONTROLLER_ERROR_MSG = 'Type controller error'
    SET_VAL_TO_WEB_ERROR_MSG = 'Error setting the value on the web'

    NUM_HOST = 'host_id'
    NUM_DET_LOGICS = 'num_detLogics'
    NUM_DETECTORS = 'num_detectors'
    CURRENT_PLAN = 'current_plan'
    CURRENT_PARAM_PLAN = 'current_parameter_plan'
    CURRENT_TIME = 'current_time'
    CURRENT_ERRORS = 'current_errors'
    CURRENT_DET_ERRORS = 'current_det_errors'
    CURRENT_STATE = 'current_state'
    CURRENT_MODE = 'current_mode'
    CURRENT_STAGE = 'current_stage'


class JsonBody(Enum):
    BASE_JSON_BODY = (
        EntityJsonResponce.TYPE_CONTROLLER.value,
        EntityJsonResponce.NUM_HOST.value,
    )

    JSON_SET_BODY = (
        EntityJsonResponce.RESULT.value,
        EntityJsonResponce.TYPE_COMMAND.value,
        EntityJsonResponce.VALUE.value
    )


class Oids(Enum):
    """" STCIP """
    # Command
    swarcoUTCTrafftechPhaseCommand = '1.3.6.1.4.1.1618.3.7.2.11.1.0'
    swarcoUTCCommandDark = '1.3.6.1.4.1.1618.3.2.2.2.1.0'
    swarcoUTCCommandFlash = '1.3.6.1.4.1.1618.3.2.2.1.1.0'
    swarcoUTCTrafftechPlanCommand = '1.3.6.1.4.1.1618.3.7.2.2.1.0'
    # Status
    swarcoUTCStatusEquipment = '1.3.6.1.4.1.1618.3.6.2.1.2.0'
    swarcoUTCTrafftechPhaseStatus = '1.3.6.1.4.1.1618.3.7.2.11.2.0'
    swarcoUTCTrafftechPlanCurrent = '1.3.6.1.4.1.1618.3.7.2.1.2.0'
    swarcoUTCTrafftechPlanSource = '1.3.6.1.4.1.1618.3.7.2.1.3.0'
    swarcoSoftIOStatus = '1.3.6.1.4.1.1618.5.1.1.1.1.0'
    swarcoUTCDetectorQty = '1.3.6.1.4.1.1618.3.3.2.2.2.0'
    swarcoUTCSignalGroupState = '1.3.6.1.4.1.1618.3.5.2.1.6.0'
    swarcoUTCSignalGroupOffsetTime = '1.3.6.1.4.1.1618.3.5.2.1.3.0'
    # Command(Spec PotokS)
    potokS_UTCCommandAllRed = '1.3.6.1.4.1.1618.3.2.2.4.1.0'
    potokS_UTCSetGetLocal = '1.3.6.1.4.1.1618.3.7.2.8.1.0'
    potokS_UTCprohibitionManualPanel = '1.3.6.1.4.1.1618.3.6.2.1.3.1.0'
    potokS_UTCCommandRestartProgramm = '1.3.6.1.4.1.1618.3.2.2.3.1.0'
    # Status(Spec PotokS)
    potokS_UTCStatusMode = '1.3.6.1.4.1.1618.3.6.2.2.2.0'

    """" UG405 """
    # -- Control Bits --#
    utcControlLO = '1.3.6.1.4.1.13267.3.2.4.2.1.11'
    utcControlFF = '1.3.6.1.4.1.13267.3.2.4.2.1.20'
    utcControlTO = '1.3.6.1.4.1.13267.3.2.4.2.1.15'
    utcControlFn = '1.3.6.1.4.1.13267.3.2.4.2.1.5'
    # -- Reply Bits --#
    utcType2Reply = '1.3.6.1.4.1.13267.3.2.5'
    utcType2Version = '1.3.6.1.4.1.13267.3.2.1.1.0'
    utcReplySiteID = '1.3.6.1.4.1.13267.3.2.5.1.1.2.0'
    utcType2VendorID = '1.3.6.1.4.1.13267.3.2.1.4.0'
    utcType2HardwareType = '1.3.6.1.4.1.13267.3.2.1.5.0'
    utcType2OperationModeTimeout = '1.3.6.1.4.1.13267.3.2.2.4.0'
    utcType2OperationMode = '1.3.6.1.4.1.13267.3.2.4.1.0'
    utcReplyGn = '1.3.6.1.4.1.13267.3.2.5.1.1.3'
    utcReplyFR = '1.3.6.1.4.1.13267.3.2.5.1.1.36'
    utcReplyDF = '1.3.6.1.4.1.13267.3.2.5.1.1.5'
    utcReplyMC = '1.3.6.1.4.1.13267.3.2.5.1.1.15'
    utcReplyCF = '1.3.6.1.4.1.13267.3.2.5.1.1.16'
    utcReplyVSn = '1.3.6.1.4.1.13267.3.2.5.1.1.32'
    utcType2OutstationTime = '1.3.6.1.4.1.13267.3.2.3.2.0'
    utcType2ScootDetectorCount = '1.3.6.1.4.1.13267.3.2.3.1.0'
    # -- Control Bits --#(Spec PotokP)
    potokP_utcControRestartProgramm = '1.3.6.1.4.1.13267.3.2.4.2.1.5.5'
    # -- Reply Bits --#(Spec PotokP)
    potokP_utcReplyPlanStatus = '1.3.6.1.4.1.13267.1.2.9.1.3'
    potokP_utcReplyPlanSource = '1.3.6.1.4.1.13267.1.2.9.1.3.1'
    potokP_utcReplyDarkStatus = '1.3.6.1.4.1.13267.3.2.5.1.1.45'
    potokP_utcReplyLocalAdaptiv = '1.3.6.1.4.1.13267.3.2.5.1.1.46'
    potokP_utcReplyHardwareErr = '1.3.6.1.4.1.13267.3.2.5.1.1.16.1'
    potokP_utcReplySoftwareErr = '1.3.6.1.4.1.13267.3.2.5.1.1.16.2'
    potokP_utcReplyElectricalCircuitErr = '1.3.6.1.4.1.13267.3.2.5.1.1.16.3'

    # scn_required_oids = {
    #     utcReplyGn, utcReplyFR, utcReplyDF, utcControlTO, utcControlFn, potokP_utcReplyPlanStatus,
    #     potokP_utcReplyPlanSource, potokP_utcReplyPlanSource, potokP_utcReplyDarkStatus, potokP_utcReplyLocalAdaptiv,
    #     potokP_utcReplyHardwareErr, potokP_utcReplySoftwareErr, potokP_utcReplyElectricalCircuitErr,
    #     utcReplyMC, utcReplyCF
    # }


class BaseCommon:
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
        'FT': 'Фиксированный',
        'VA': 'Адаптивный',
        'MAN': 'Ручное управление',
        'UTC': 'Удалённое управление',
        'CLF': 'Беспентровая синхронизация',
        'ЛАМПЫ ВЫКЛ': 'Сигналы выключены(ОС)',
        'ЖЕЛТОЕ МИГАНИЕ': 'Жёлтое мигание',
        'КРУГОМ КРАСНЫЙ': 'Кругом Красный',
        'ЗАБЛОКИРОВАН ИНСПЕКТОРОМ': 'Заблокирован инспектором',
        'УПРАВЛЕНИЕ': 'Управление',
        'CONTROL': 'Управление'
    }

    type_request: EntityJsonResponce | None
    controller_type: str | None
    json_body_second_part: Iterable | None
    parse_varBinds_get_state: Callable
    parse_varBinds: Callable

    def __init__(self, ip_adress, host_id=None):
        self.ip_adress = ip_adress
        self.host_id = host_id
        # self.get_mode_flag = False
        # self.type_curr_request = None
        # self.cur_req_entity = {}
        self.errorIndication = None
        self.varBinds = None
        self.req_data = {}
        self.get_entity = []
        self.set_entity = {}
        self.result_set_command = None
        self.request_time = None

    def set_curr_datetime(self) -> str:
        self.request_time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        return datetime.today().strftime("%Y-%m-%d %H:%M:%S")


    def set_controller_type(self) -> None:
        """ Метод устанавливает тип контроллера """

        if isinstance(self, (SwarcoSTCIP, SwarcoSSH)):
            self.controller_type = AvailableControllers.SWARCO.value
        elif isinstance(self, PotokP):
            self.controller_type = AvailableControllers.POTOK_P.value
        elif isinstance(self, PotokS):
            self.controller_type = AvailableControllers.POTOK_S.value
        elif isinstance(self, (PeekUG405, PeekWeb)):
            self.controller_type = AvailableControllers.PEEK.value
        else:
            self.controller_type = None

    def put_to_get_entity(self, data: str | list):
        if type(data) == str:
            self.get_entity.append(data)
        elif type(data) == list:
            self.get_entity += data

    def put_to_req_data(self, data: dict):
        if type(data) == dict:
            self.req_data |= data
    # def create_json(self, errorIndication: None | Exception | str, varBinds: list, **kwargs) -> dict:
    #     """"
    #     Метод формирует словарь вида json
    #     :arg errorIndication: None если не было ошибки при запросе иначе класс ошибки или str
    #     :param varBinds: список varBinds, полученный после запроса
    #     :arg kwargs: параметры, которые будут добавлены в словарь
    #     """
    #
    #
    #     json = {k: v for k, v in zip(JsonBody.BASE_JSON_BODY.value, (self.controller_type, self.host_id))}
    #     errorIndication = errorIndication.__str__() if errorIndication is not None else errorIndication
    #     json[EntityJsonResponce.REQUEST_ERRORS.value] = errorIndication
    #     # json[EntityJsonResponce.TYPE_REQUEST.value] = self.type_curr_request
    #
    #
    #     if errorIndication:
    #         self.get_mode_flag = False
    #         if kwargs:
    #             json |= {k: v for k, v in kwargs.items()}
    #         return {self.ip_adress: json}
    #
    #     if self.get_mode_flag:
    #         varBinds, curr_state = self.get_current_mode(varBinds)
    #         json |= curr_state
    #     if varBinds:
    #         json |= self.parse_varBinds_common(varBinds)
    #
    #     self.get_mode_flag = False
    #     if kwargs:
    #         json |= {k: v for k, v in kwargs.items()}
    #
    #     return {self.ip_adress: json}

    def create_json(self, errorIndication: None | Exception | str, varBinds: list, **kwargs) -> dict:
        """"
        Метод формирует словарь вида json
        :arg errorIndication: None если не было ошибки при запросе иначе класс ошибки или str
        :param varBinds: список varBinds, полученный после запроса
        :arg kwargs: параметры, которые будут добавлены в словарь
        """

        example_get = {
            'host_id': "1",
            'request_errors': None,
            'type_controller': 'Swarco',
            "request": {'protocol': 'snmp',
                        'type': 'get',
                 'entity': ['get_mode', "swarcoUTCTrafftechPlanSource"]
                },
            "responce": {'mode': 'Адаптивный',
                         'фаза': '2',
                         'план': '5'
            }
        }

        example_set = {
            'host_id':"1",
            'request_errors': None,
            'type_controller': 'Swarco',
                "request": {'protocol': 'snmp',
                        'type': 'set',
                 'entity':
                        {'set_stage': '1'}
                },
            "responce": {'swarcoUTCTrafftechPhaseCommand[1.3.6.1.4.1.1618.3.7.2.11.1.0]': 'num_stage[1], val_stage[2]'}
        }

        self.req_data |= {k: v for k, v in zip(JsonBody.BASE_JSON_BODY.value, (self.controller_type, self.host_id))}
        logger.debug('self.req_data %s', self.req_data)
        errorIndication = errorIndication.__str__() if errorIndication is not None else errorIndication
        self.req_data[EntityJsonResponce.REQUEST_ERRORS.value] = errorIndication

        if self.get_entity:
            self.req_data[EntityJsonResponce.REQUEST_ENTITY.value] = self.get_entity
            get_mode_flag = True
        else:
            get_mode_flag = False
        if self.set_entity:
            self.req_data[EntityJsonResponce.REQUEST_ENTITY.value] = self.set_entity
        logger.debug(self.set_entity)
        logger.debug(self.req_data)

        if errorIndication:
            if kwargs:
                self.req_data |= {k: v for k, v in kwargs.items()}
            return self.req_data

        self.req_data[EntityJsonResponce.RESPONCE_ENTITY.value] = {}

        if get_mode_flag:
            varBinds, curr_state = self.get_current_mode(varBinds)
            self.req_data[EntityJsonResponce.RESPONCE_ENTITY.value] |= curr_state

        if varBinds:
            if self.set_entity:
                self.req_data[EntityJsonResponce.RESPONCE_ENTITY.value]['result'] = 'request sent successfully'
                self.req_data[EntityJsonResponce.RESPONCE_ENTITY.value]['success'] = True
            self.req_data[EntityJsonResponce.RESPONCE_ENTITY.value] |= self.parse_varBinds(varBinds)

        # self.get_mode_flag = False
        if kwargs:
            self.req_data |= {k: v for k, v in kwargs.items()}

        return self.req_data

    def get_current_mode(self, args: list) -> list:
        ...


class BaseSNMP(BaseCommon):
    """
    Базовый класс для snmp запросов по всем протоколам: set и get запросы
    """
    user_oids: Iterable
    scn: str
    get_state_oids: set
    matching_types_set_req: dict
    community_read: str
    community_write: str

    def __init__(self, ip_adress, host_id=None):
        super().__init__(ip_adress, host_id)

    async def get_request_base(self,
                               ip_adress: str,
                               community: str,
                               oids: Iterable,
                               json_responce: bool = False,
                               timeout: int = 0,
                               retries: int = 1):
        """
        Возвращает list значений оидов при успешном запросе, инчае возвращает str с текстом ошибки.
        :param type_controller:
        :param json_responce:
        :arg ip_adress: ip хоста
        :arg community: коммьюнити хоста
        :arg oids: List или Tuple оидов
        :arg timeout: таймаут запроса, в секундах
        :arg retries: количество попыток запроса
        :return: list при успешном запросе, иначе errorIndication
        """
        # print(f'get_request ')
        # print(f'oids : {oids} ')

        # if isinstance(self, (PotokP, PeekUG405)):
        #     oids = (oid + self.scn if oid in Oids.scn_required_oids.value else oid for oid in oids)
        # elif isinstance(self, SwarcoSTCIP):
        #     oids = [oid.value for oid in oids]
        self.put_to_req_data({'protocol': 'snmp', 'type': 'get', 'request_time': self.set_curr_datetime()})

        errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            *[ObjectType(ObjectIdentity(oid)) for oid in oids]
        )

        # logging.debug(
        #     f'errorIndication: {errorIndication.__str__()}\n'
        #     f'errorStatus: {errorStatus}\n'
        #     f'errorIndex: {errorIndex}\n'
        #     f'varBinds: {varBinds}\n'
        # )
        # print(f'errorIndication .__str__: {errorIndication.__str__()}')
        # print(f'errorIndication: {errorIndication}')
        # print(f'errorIndication type : {type(errorIndication)}')
        # print(f'errorStatus: {errorStatus}')
        # print(f'errorIndex: {errorIndex}')
        # print(f'varBinds: {varBinds}')
        self.errorIndication, self.varBinds = errorIndication, varBinds
        return errorIndication, varBinds, self

    async def getNext_request_base(self,
                                   ip_adress: str,
                                   community: str,
                                   oids: Iterable,
                                   timeout: int = 0,
                                   retries: int = 0):


        self.type_curr_request = EntityJsonResponce.TYPE_SNMP_REQUEST_GET.value
        errorIndication, errorStatus, errorIndex, varBinds = await nextCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            *[ObjectType(ObjectIdentity(oid)) for oid in oids]
        )
        # logging.debug(
        #     f'errorIndication: {errorIndication.__str__()}\n'
        #     f'errorStatus: {errorStatus}\n'
        #     f'errorIndex: {errorIndex}\n'
        #     f'varBinds: {varBinds}\n'
        # )
        # print(f'errorIndication .__str__: {errorIndication.__str__()}')
        # print(f'errorIndication: {errorIndication}')
        # print(f'errorIndication type : {type(errorIndication)}')
        # print(f'errorStatus: {errorStatus}')
        # print(f'errorIndex: {errorIndex}')
        # print(f'varBinds: {varBinds}')
        return errorIndication, varBinds, self

    async def set_request_base(self,
                               ip_adress: str,
                               community: str,
                               oids: list | tuple | set | dict,
                               timeout: int = 0, retries: int = 0) -> tuple:
        """
        Возвращает list значений оидов при успешном запросе, инчае возвращает str с текстом ошибки
        :param ip_adress: ip хоста
        :param community: коммьюнити хоста
        :param oids: List или Tuple оидов
        :param timeout: таймаут запроса, в секундах
        :param retries: количество попыток запроса
        :return: list при успешном запросе, иначе str с текстом ошибки
        """
        logging.debug(f'set_request_base')
        self.put_to_req_data({'protocol': 'snmp', 'type': 'set', 'request_time': self.set_curr_datetime()})
        oids = list(oids.items() if type(oids) is dict else oids)
        errorIndication, errorStatus, errorIndex, varBinds = await setCmd(
            SnmpEngine(),
            CommunityData(community),
            UdpTransportTarget((ip_adress, 161), timeout=timeout, retries=retries),
            ContextData(),
            *[ObjectType(ObjectIdentity(oid), val) for oid, val in oids]
            # ObjectType(ObjectIdentity(Oids.swarcoUTCTrafftechPhaseCommand.value), Unsigned32('0'))
        )
        logging.debug(
            f'\nerrorIndication: {errorIndication.__str__()}\n'
            f'errorStatus: {errorStatus}\n'
            f'errorIndex: {errorIndex}\n'
            f'varBinds: {varBinds}\n'
        )
        self.errorIndication, self.varBinds = errorIndication, varBinds
        return errorIndication, varBinds, self

        # print(f'errorIndication: {errorIndication.__str__()}')
        # print(f'errorStatus: {errorStatus}')
        # print(f'errorIndex: {errorIndex}')
        # print(f'varBinds: {varBinds}')
        # res = [(data[0].prettyPrint(), data[1].prettyPrint()) for data in varBinds]
        # # print(f'res -> {res}')
        # if not errorIndication and varBinds:
        #     if varBinds:
        #         # return True, [(data[0].prettyPrint(), data[1].prettyPrint()) for data in varBinds]
        #
        #         return [data[1].prettyPrint() for data in varBinds]
        #     else:
        #         return self.error_no_varBinds
        #     # print(f'(len(varBinds): {len(varBinds)}')
        #     # # res = [(data[0].prettyPrint(), data[1].prettyPrint()) for data in varBinds]
        #     # res = [data[1].prettyPrint() for data in varBinds]
        #     # print(f'res -> {res}')
        # return errorIndication.__str__()

    def create_data_for_get_req(self,
                                oids: list,
                                get_mode: bool,
                                ) -> list:
        """
        Метод формирует коллекцию оидов для отправки в соответствии с переданными параметрами
        :arg oids: коллекция оидов для запроса от пользователя
        :arg get_mode: флаг, говорящий о необходимости получения базового состояния ДК:
                       режим, фаза, план
        :return processed_oids: финальная коллекция оидов, которые будут отправлены хосту в get запросе(snmp)
        """

        # oids = oids if oids else []

        if get_mode:
            # self.get_mode_flag = True
            if isinstance(self, (PotokP, PeekUG405)):
                processed_oids = [self.add_scn_to_oids(self.check_type_oid(oid))
                                  for oid in itertools.chain(self.get_state_oids, oids)]

            else:
                processed_oids = [self.check_type_oid(oid) for oid in itertools.chain(self.get_state_oids, oids)]
        else:
            if isinstance(self, (PotokP, PeekUG405)):
                processed_oids = [self.add_scn_to_oids(self.check_type_oid(oid)) for oid in oids]
            else:
                processed_oids = [self.check_type_oid(oid) for oid in oids]
        # if get_mode:
        #     self.get_mode_flag = True
        #     if oids:
        #         if isinstance(self, (PotokP, PeekUG405)):
        #             processed_oids = [self.add_scn_to_oids(self.check_type_oid(oid))
        #                               for oid in itertools.chain(oids, self.get_state_oids)]
        #         else:
        #             processed_oids = [self.check_type_oid(oid) for oid in itertools.chain(oids, self.get_state_oids)]
        #     else:
        #         processed_oids = self.get_state_oids
        # else:
        #     if isinstance(self, (PotokP, PeekUG405)):
        #         processed_oids = [self.add_scn_to_oids(self.check_type_oid(oid)) for oid in oids]
        #     else:
        #         processed_oids = [self.check_type_oid(oid) for oid in oids]

        return processed_oids

    def create_data_for_set_req(self, oids: tuple | list | dict, unique_oids: bool = False) -> list | set:
        """


        :param oids:
        :param unique_oids:
        :return: оиды для отправки. Примеры возвращаемой коллекции:

        """
        processed_oids = []

        oids = list(oids.items()) if type(oids) == dict else oids
        for oid, val in oids:
            oid = self.check_type_oid(oid)
            if isinstance(self, (PotokP, PeekUG405)):
                oid = self.add_scn_to_oids(oid)
            processed_oids.append((oid, self.matching_types_set_req.get(oid)(val)))

        return processed_oids if not unique_oids else set(processed_oids)

    async def get_request(self, oids: tuple | list = None, get_mode: bool = True) -> tuple:

        if get_mode:
            self.put_to_get_entity('get_mode')

        if not oids and not get_mode:
            self.errorIndication, self.varBinds = EntityJsonResponce.NO_DATA_FOR_REQ.value, []
            return None, [], self

        oids = [self.check_type_oid(oid) for oid in oids] if oids else []
        # self.get_entity += [Oids(oid).name if oid in {o.value for o in Oids} else oid for oid in oids]
        self.put_to_get_entity([Oids(oid).name if oid in {o.value for o in Oids} else oid for oid in oids])

        if isinstance(self, (PotokP, PeekUG405)):
            if not self.scn:
                self.scn = await self.get_scn()

        processed_oids = self.create_data_for_get_req(oids, get_mode)

        return await self.get_request_base(
            ip_adress=self.ip_adress,
            community=self.community_read,
            oids=processed_oids
        )

    async def set_request(self, oids: tuple | list | dict) -> tuple:
        """"
        :arg oids: данные для отправки



        Примеры oids:
                        [(Oids.swarcoUTCTrafftechPhaseCommand.value, Unsigned32('2')),
                        (Oids.swarcoUTCTrafftechPlanCommand.value,
                        self.matching_types_set_req.get(Oids.swarcoUTCTrafftechPlanCommand.value)(val)('2')),
                        ('1.3.6.1.4.1.1618.3.7.2.2.1.0', Unsigned32('2'))
                        ]
                        ----------------------------------------------------------------------------------------
                        {
                        Oids.swarcoUTCTrafftechPhaseCommand.value: Unsigned32('2'),
                        '1.3.6.1.4.1.1618.3.7.2.2.1.0': Unsigned32('2')
                        }

        """

        if not oids:
            self.errorIndication, self.varBinds = EntityJsonResponce.NO_DATA_FOR_REQ.value, []
            return None, [], self

        if isinstance(self, (PotokP, PeekUG405)):
            if not self.scn:
                self.scn = await self.get_scn()

        self.set_entity += [Oids(oid).name if oid in {o.value for o in Oids} else oid for oid in oids]
        processed_oids = self.create_data_for_set_req(oids)

        return await self.set_request_base(
            ip_adress=self.ip_adress,
            community=self.community_write,
            oids=processed_oids
        )

    @staticmethod
    def check_type_oid(oid: Oids | str) -> str:
        """
        Метод проверяет корректность типа переданного оида
        :param oid: Проверяемый оид
        :return: оид типа str
        """
        if type(oid) is not str:
            if isinstance(oid, Oids):
                oid = Oids(oid).value
            else:
                raise ValueError(f'{ErrorMessages.BAD_TYPE_OID.value}, type oid: {type(oid)}, val oid: {oid}')

        return oid

    # def parse_varBinds(self, varBinds: list) -> dict:
    #
    #     part_of_json = {}
    #     for oid, val in varBinds:
    #         oid, val = oid.__str__(), val.prettyPrint()
    #         if isinstance(self, (PotokP, PeekUG405)):
    #             if oid.endswith(self.scn):
    #                 oid = oid.replace(self.scn, '')
    #         oid_name, oid_val = Oids(oid).name, Oids(oid).value
    #         oid = f'{oid_name}[{oid_val}]'
    #         if (Oids.swarcoUTCTrafftechPhaseStatus.name in oid_name or Oids.swarcoUTCTrafftechPhaseCommand.name
    #                 in oid_name or Oids.utcReplyGn.name in oid_name):
    #             num_stage = self.convert_val_to_num_stage_get_req(val)
    #             val = f'num_stage[{num_stage}], val_stage[{val}]'
    #         part_of_json[oid] = val
    #
    #         if self.set_entity:
    #             part_of_json = {'raw_data': part_of_json}
    #
    #     return part_of_json

    def parse_varBinds(self, varBinds: list) -> dict:

        part_of_json, oids = {}, []
        for oid, val in varBinds:
            oid, val = oid.__str__(), val.prettyPrint()
            if isinstance(self, (PotokP, PeekUG405)):
                if oid.endswith(self.scn):
                    oid = oid.replace(self.scn, '')
            oid_name, oid_val = Oids(oid).name, Oids(oid).value
            oid = f'{oid_name}[{oid_val}]'
            if (Oids.swarcoUTCTrafftechPhaseStatus.name in oid_name or Oids.swarcoUTCTrafftechPhaseCommand.name
                    in oid_name or Oids.utcReplyGn.name in oid_name):
                num_stage = self.convert_val_to_num_stage_get_req(val)
                val = f'num_stage[{num_stage}], val_stage[{val}]'

            if self.get_entity:
                part_of_json[oid] = val
            elif self.set_entity:
                oids.append({oid: val})
            else:
                raise ValueError('Программный сбой')
            #
            # if not self.get_entity:
            #     part_of_json[oid] = val
            # elif :

            if self.set_entity:
                part_of_json = {'raw_data': {'oids': oids}}

        return part_of_json


class BaseSTCIP(BaseSNMP):
    convert_val_to_num_stage_set_req: Callable
    converted_values_all_red: dict
    community_write = os.getenv('communitySTCIP_w')
    community_read = os.getenv('communitySTCIP_w')

    converted_values_flash_dark = {
        '1': '2', 'true': '2', 'on': '2', 'вкл': '2', '2': '2',
        '0': '0', 'false': '0', 'off': '0', 'выкл': '0',
    }
    matching_types_set_req = {
        Oids.swarcoUTCTrafftechPhaseCommand.value: Unsigned32,
        Oids.swarcoUTCTrafftechPlanCommand.value: Unsigned32
    }

    """ GET REQUEST """

    """ SET REQUEST """

    async def set_stage(self, value='0', timeout=1, retries=2) -> tuple:
        """"
        Устанавливает  фазу.
        :param value:  Номер фазы в десятичном виде
        :param retries:
        :param timeout:
        :return: ErrorIndication, varBinds
        """

        self.set_entity['set_stage'] = value
        converted_val = self.convert_val_to_num_stage_set_req(value.lower())
        oids = [
            (Oids.swarcoUTCTrafftechPhaseCommand.value, Unsigned32(converted_val)),
        ]
        return await self.set_request_base(self.ip_adress, self.community_write, oids, timeout=timeout, retries=retries)

    async def set_allred(self, value='0', timeout=1, retries=2) -> tuple:
        """"
        Устанавливает или сбрасывает режим КК
        :param retries:
        :param timeout:
        :param value: значение. см ассоциации в self.converted_values_all_red
        :return: ErrorIndication, varBinds
        """
        if isinstance(self, SwarcoSTCIP):
            oid = Oids.swarcoUTCTrafftechPlanCommand.value
        else:
            oid = Oids.potokS_UTCCommandAllRed.value

        value = self.converted_values_all_red.get(value.lower())

        oids = (
            (oid, Unsigned32(value)),
        )
        return await self.set_request_base(self.ip_adress, self.community_write, oids, timeout=timeout, retries=retries)

    async def set_flash(self, value='0', timeout=1, retries=2) -> tuple:
        """"
        Устанавливает ЖМ(или сбрасывает ранее установленный в swarcoUTCCommandFlash)
        :param retries:
        :param timeout:
        :param value: 2 -> устанавливает ОС, 0 -> сбрасывает ранее установленный ЖМ
        """

        value = self.converted_values_flash_dark.get(value.lower())

        oids = (
            (Oids.swarcoUTCCommandFlash.value, Integer32(value)),
        )
        return await self.set_request_base(self.ip_adress, self.community_write, oids, timeout=timeout, retries=retries)

    async def set_dark(self, value='0', timeout=1, retries=2) -> tuple:
        """"
        Устанавливает ОС(или сбрасывает ранее установленный в swarcoUTCCommandDark)
        :param value: 2 -> устанавливает ОС, 0 -> сбрасывает ранее установленный ОС
        :return: Возвращает значение установленного swarcoUTCCommandDark
        """

        value = self.converted_values_flash_dark.get(value.lower())
        oids = (
            (Oids.swarcoUTCCommandDark.value, Integer32(value)),
        )
        return await self.set_request_base(self.ip_adress, self.community_write, oids, timeout=timeout, retries=retries)


class BaseUG405(BaseSNMP):
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

    community_read = os.getenv('communityUG405_r')
    community_write = os.getenv('communityUG405_w')

    scn_required_oids = {
        Oids.utcReplyGn.value, Oids.utcReplyFR.value, Oids.utcReplyDF.value, Oids.utcControlTO.value,
        Oids.utcControlFn.value, Oids.potokP_utcReplyPlanStatus.value, Oids.potokP_utcReplyPlanSource.value,
        Oids.potokP_utcReplyPlanSource.value, Oids.potokP_utcReplyDarkStatus.value,
        Oids.potokP_utcReplyLocalAdaptiv.value, Oids.potokP_utcReplyHardwareErr.value,
        Oids.potokP_utcReplySoftwareErr.value, Oids.potokP_utcReplyElectricalCircuitErr.value,
        Oids.utcReplyMC.value, Oids.utcReplyCF.value, Oids.utcReplyVSn.value
    }

    # Ключи, прописанные вручную, рабочая версия
    # set_stage_UG405_peek_values = {'1': '01', '2': '02', '3': '04', '4': '08',
    #                                '5': '10', '6': '20', '7': '40', '8': '80',
    #                                '9': '0001', '10': '0002', '11': '0004', '12': '0008',
    #                                '13': '0010', '14': '0020', '15': '0040', '16': '0080'}

    def __init__(self, ip_adress, scn=None, host_id=None):
        super().__init__(ip_adress, host_id)
        self.ip_adress = ip_adress
        self.scn = self.convert_scn(scn) if scn else scn
        self.host_id = host_id


    @staticmethod
    def convert_scn(scn: str) -> str:
        """ Функция получает на вход строку, которую необходимо конвертировать в SCN
            для управления и мониторинга по протоколу UG405.
            Например: convert_scn(CO1111)
        """
        return f'.1.{str(len(scn))}.{".".join([str(ord(c)) for c in scn])}'

    def add_scn_to_oids(self, oids: set | tuple | list | str, scn: str = None) -> str | list:
        """
        Метод добавляет scn к оиду, если он необходим.
        :param oids: один оид в виде строки или коллекция оидов, где каждый элемент коллекции - оид типа str
        :param scn: если None, то берём scn из self
        :return: если на вход дан один оид(str) то возвращаем также один оид + scn в виде строки.
                 если на вход дана коллекция, возвращаем коллекцию оидов с scn
        """
        scn = self.scn if scn is None else scn
        if type(oids) == str:
            return oids + scn

        new_oids = []
        for oid in oids:
            oid = self.check_type_oid(oid)
            if oid in self.scn_required_oids:
                new_oids.append(oid + scn)
            else:
                new_oids.append(oid)
        return new_oids

    def remove_scn_from_oid(self, oid: str) -> str:
        """
        Метод удаляет scn у оида если scn присутсвтует в нём.
        :arg oid: оид, который необходимо проверить на наличие в нём scn
        :return oid: возвращает оид без scn
        """
        return oid.replace(self.scn, '') if self.scn in oid else oid

    @staticmethod
    def convert_val_to_num_stage_get_req(val: str):
        try:
            if val not in (' ', '@'):
                return int(math.log2(int(val, 16))) + 1
            elif val == ' ':
                return 6
            elif val == '@':
                return 7
            else:
                return None
        except ValueError:
            return None

    """ GET REQUEST """

    async def get_scn(self):

        if isinstance(self, PeekUG405):

            errorIndication, varBinds, _ = await self.getNext_request_base(self.ip_adress,
                                                                           self.community_read,
                                                                           [Oids.utcType2Reply.value])
            if errorIndication is None and varBinds:
                oid = varBinds[0][0][0].__str__()
                replace_fragment = Oids.utcReplyGn.value
                if replace_fragment in oid:
                    return oid.replace(replace_fragment, "")
            return ''

        elif isinstance(self, PotokP):
            logging.debug(f'get_scn: {self}')
            errorIndication, varBinds, _ = await self.get_request_base(self.ip_adress,
                                                                       self.community_read,
                                                                       (Oids.utcReplySiteID.value,))
            if errorIndication is None and varBinds:
                return self.convert_scn(varBinds[0][1].prettyPrint())
            return ''
        else:
            return ''

    # async def TESTget_utcType2VendorID(self, timeout=0, retries=0):
    #     """
    #     Возвращает значение OperationModeTimeout
    #     :param timeout: Таймаут подключения
    #     :param retries: Количетсво попыток подключения
    #     :return Текущее значение utcType2OperationModeTimeout
    #     """
    #     print('-------')
    #     print(self.ip_adress)
    #     print(self.community)
    #     print('*******')
    #
    #     oids = [
    #         ObjectType(ObjectIdentity('UTMC-UTMCFULLUTCTYPE2-MIB', 'utcType2HardwareType', 0)),
    #         ObjectType(ObjectIdentity('UTMC-UTMCFULLUTCTYPE2-MIB', 'utcType2VendorID', 0)),
    #         ObjectType(ObjectIdentity('UTMC-UTMCFULLUTCTYPE2-MIB', 'utcType2HardwareID', 0)),
    #     ]
    #
    #     result, val = await self.get_request_base(self.ip_adress,
    #                                               self.community,
    #                                               oids
    #                                               )

    """ archive methods(not usage) """

    """ SET REQUEST """


class SwarcoSTCIP(BaseSTCIP):
    converted_values_all_red = {
        '1': '119', 'true': '119', 'on': '119', 'вкл': '119', '2': '119', '119': '119',
        '0': '100', 'false': '100', 'off': '100', 'выкл': '100',
    }

    get_state_oids = {
        Oids.swarcoUTCStatusEquipment.value,
        Oids.swarcoUTCTrafftechPhaseStatus.value,
        Oids.swarcoUTCTrafftechPlanCurrent.value,
        Oids.swarcoUTCDetectorQty.value,
        Oids.swarcoSoftIOStatus.value,
    }

    def __init__(self, ip_adress, host_id=None):
        super().__init__(ip_adress, host_id)
        self.set_controller_type()
        # self._get_current_state = False

    @staticmethod
    def convert_val_to_num_stage_get_req(val: str) -> int | None:
        values = {'2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '1': 8, '0': 0}
        return values.get(val)

    @staticmethod
    def convert_val_to_num_stage_set_req(val: str) -> int | None:
        values = {'1': 2, '2': 3, '3': 4, '4': 5, '5': 6, '6': 7, '7': 8, '8': 1, 'ЛОКАЛ': 0, '0': 0}
        return values.get(val)

    """ GET REQUEST """

    def _mode_define(self, equipment_status: str, plan: str, softstat180_181: str, num_logics: str) -> str:
        """ Определяет текщий ружим ДК.
        :arg equipment_status (str): Текущий режим работы контроллера:
                                     workingProperly(1),
                                     powerUp(2),
                                     dark(3),
                                     flash(4),
                                     partialFlash(5),
                                     allRed(6)

        :arg plan (str): Текущий номер плана
        :arg softstat180_181 (str): Текущее состояние входов 180 и 181
        :arg num_logics (str): Количество детекторных логик

        :return str: Возращает текущий режим ДК(Фикс/Адаптива/КУ и т.д)
        """

        if equipment_status != '1':
            val_mode = equipment_status
        elif plan == '16':
            val_mode = '11'
        elif plan == '15':
            val_mode = '10'
        elif softstat180_181 is None or '1' in softstat180_181 or num_logics == '0':
            val_mode = '12'
        elif softstat180_181 == '00' and num_logics.isdigit() and int(num_logics) > 0:
            val_mode = '8'
        else:
            val_mode = '--'

        return self.statusMode.get(val_mode)

    def get_current_mode(self, varBinds: list) -> tuple:
        equipment_status = plan = softstat180_181 = num_logics = stage = None
        new_varBins = []
        user_oids = self.req_data.get('request')
        logger.debug(user_oids)
        for data in varBinds:
            oid, val = data[0].__str__(), data[1].prettyPrint()

            if oid in self.get_state_oids:
                if oid == Oids.swarcoUTCStatusEquipment.value:
                    equipment_status = val
                elif oid == Oids.swarcoUTCTrafftechPhaseStatus.value:
                    stage = self.convert_val_to_num_stage_get_req(val)
                elif oid == Oids.swarcoUTCTrafftechPlanCurrent.value:
                    plan = val
                elif oid == Oids.swarcoUTCDetectorQty.value:
                    num_logics = val
                elif oid == Oids.swarcoSoftIOStatus.value:
                    softstat180_181 = val[179:181] if len(val) > 180 else None
                if user_oids is not None and Oids(oid).name in user_oids:
                    logger.debug(user_oids)
                    new_varBins.append(data)
            else:
                new_varBins.append(data)
        mode = self._mode_define(equipment_status, plan, softstat180_181, num_logics)
        curr_state = {
            EntityJsonResponce.CURRENT_MODE.value: mode,
            EntityJsonResponce.CURRENT_STAGE.value: str(stage),
            EntityJsonResponce.CURRENT_PLAN.value: plan,
        }
        # for oid, val in varBinds:
        #     print(f'{Oids(oid.__str__()).value}||||| val: {val.prettyPrint()}')
        return new_varBins, curr_state

    """ SET REQUEST """


class PotokS(BaseSTCIP):

    converted_values_all_red = {
        '1': '2', 'true': '2', 'on': '2', 'вкл': '2',
        '0': '0', 'false': '0', 'off': '0', 'выкл': '0',
    }
    # get_val_stage = {
    #     str(k) if k < 66 else str(0): v if v < 65 else 0 for k, v in zip(range(2, 67), range(1, 66))
    # }
    # # set_val_stage = {
    # #     str(k) if k < 65 else 'ЛОКАЛ': str(v) if k < 65 else '0' for k, v in zip(range(1, 68), range(2, 69))
    # # }
    #
    # set_val_stage = {
    #     str(k): str(v) if k > 0 else '0' for k, v in zip(range(65), range(1, 66))
    # }
    get_state_oids = {
        Oids.swarcoUTCStatusEquipment.value,
        Oids.swarcoUTCTrafftechPhaseStatus.value,
        Oids.swarcoUTCTrafftechPlanCurrent.value,
        Oids.potokS_UTCStatusMode.value,
    }

    def __init__(self, ip_adress, host_id=None):
        super().__init__(ip_adress, host_id)
        self.set_controller_type()

    """ GET REQUEST """

    @staticmethod
    def convert_val_to_num_stage_get_req(val: str) -> int | None:

        values = {
            str(k) if k < 66 else str(0): v if v < 65 else 0 for k, v in zip(range(2, 67), range(1, 66))
        }
        return values.get(val)

    @staticmethod
    def convert_val_to_num_stage_set_req(val: str) -> int | None:
        values = {str(k): str(v) if k > 0 else '0' for k, v in zip(range(65), range(1, 66))}
        return values.get(val)

    def _mode_define(self, equipment_status: str, plan: str, status_mode: str) -> str:
        """ Определяет текщий ружим ДК.
        :arg equipment_status (str): Текущий режим работы контроллера:
                                     workingProperly(1),
                                     powerUp(2),
                                     dark(3),
                                     flash(4),
                                     partialFlash(5),
                                     allRed(6)

        :arg plan (str): Текущий номер плана
        :arg softstat180_181 (str): Текущее состояние входов 180 и 181
        :arg num_logics (str): Количество детекторных логик

        :return str: Возращает текущий режим ДК(Фикс/Адаптива/КУ и т.д)
        """

        if equipment_status != '1':
            val_mode = equipment_status
        elif status_mode == '11' and plan == '16':
            val_mode = status_mode
        elif status_mode != '11' and status_mode in ('8', '10', '12'):
            val_mode = status_mode
        else:
            val_mode = '--'
        return self.statusMode.get(val_mode)

    def get_current_mode(self, varBinds: list) -> tuple:
        equipment_status = plan = status_mode = stage = None
        new_varBins = []
        for data in varBinds:
            oid, val = data[0].__str__(), data[1].prettyPrint()
            if oid in self.get_state_oids:
                if oid == Oids.swarcoUTCStatusEquipment.value:
                    equipment_status = val
                elif oid == Oids.swarcoUTCTrafftechPhaseStatus.value:
                    stage = self.convert_val_to_num_stage_get_req(val)
                elif oid == Oids.swarcoUTCTrafftechPlanCurrent.value:
                    plan = val
                elif oid == Oids.potokS_UTCStatusMode.value:
                    status_mode = val
                if self.user_oids and (oid in self.user_oids):
                    new_varBins.append(data)
            else:
                new_varBins.append(data)
        mode = self._mode_define(equipment_status, plan, status_mode)
        curr_state = {
            EntityJsonResponce.CURRENT_MODE.value: mode,
            EntityJsonResponce.CURRENT_STAGE.value: stage,
            EntityJsonResponce.CURRENT_PLAN.value: plan,
        }
        return new_varBins, curr_state

    # def parse_varBinds_get_state(self, varBinds: list) -> tuple:
    #
    #     equipment_status, status_mode, stage, det_count, plan, *rest = [data[1].prettyPrint() for data in varBinds]
    #     mode = self._mode_define(equipment_status, plan, status_mode)
    #
    #     get_mode_data = (
    #         mode,
    #         self.get_val_stage.get(stage),
    #         int(plan) if plan.isdigit() else plan,
    #         int(det_count) if det_count.isdigit() else det_count,
    #     )
    #     return get_mode_data

    # async def get_current_state(self, timeout=0, retries=0) -> tuple:
    #     """
    #     Метод запроса значений необходимых оидов для получения текущего состояния ДК
    #     :param retries:
    #     :param timeout:
    #     :return tuple: (errorIndication, varBinds)
    #     """
    #     self.type_request = EntityJsonResponce.TYPE_GET_STATE
    #     self.json_body_second_part = JsonBody.JSON_GET_STATE_POTOK_S_BODY.value
    #     logger.debug(f'перед await get_current_mode')
    #     oids = [
    #         Oids.swarcoUTCStatusEquipment,
    #         Oids.potokUTCStatusMode,
    #         Oids.swarcoUTCTrafftechPhaseStatus,
    #         Oids.swarcoUTCDetectorQty,
    #         Oids.swarcoUTCTrafftechPlanCurrent,
    #     ]
    #     return await self.get_request_base(self.ip_adress,
    #                                        self.community_read,
    #                                        oids,
    #                                        timeout=timeout, retries=retries)

    """ SET REQUEST """

    async def set_restartProgramm(self, value='1', timeout=1, retries=2) -> tuple:
        """"
        Перезапускает рабочую программу
        :param retries:
        :param timeout:
        :param value: 1 -> команда на перезапуск рабочей программы
        """

        oids = (
            (Oids.potokS_UTCCommandRestartProgramm.value, Unsigned32(value)),
        )
        return await self.set_request_base(self.ip_adress, self.community_write, oids, timeout=timeout, retries=retries)

    async def set_potokUTCSetGetLocal(self, value=0, timeout=0, retries=0):
        """"
        Устанавливает/сбрасывает локальный режим
        :param value: 1 -> устанавливает Устанавливает локальный режим, 0 -> сбрасывает установленный локальный режим
        """
        oids = [ObjectType(ObjectIdentity(self.get_swarcoUTCSetGetLocal), Unsigned32(value))]
        return await self.set_request(self.ip_adress, self.community_write, oids, timeout=timeout, retries=retries)

    async def set_potokUTCprohibitionManualPanel(self, value=0, timeout=0, retries=0):
        """
        Устанавливает запрет использования ВПУ(1 -> ВКЛ, 0 -> ВЫКЛ) potokUTCprohibitionManualPanel
        :param timeout: таймаут подключения
        :param retries: количество попыток подключения
        """
        oids = [ObjectType(ObjectIdentity(self.potokUTCprohibitionManualPanel), Unsigned32(value))]
        return await self.set_request(self.ip_adress, self.community_write, oids, timeout=timeout, retries=retries)


class PotokP(BaseUG405):

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

    get_state_oids = {
        Oids.utcType2OperationMode.value,
        Oids.utcReplyCF.value,
        Oids.utcReplyFR.value,
        Oids.potokP_utcReplyDarkStatus.value,
        Oids.utcReplyMC.value,
        Oids.potokP_utcReplyPlanStatus.value,
        Oids.utcReplyGn.value,
        Oids.utcReplyDF.value,
        Oids.potokP_utcReplyLocalAdaptiv.value,
    }


    def __init__(self, ip_adress, host_id=None, scn=None):
        super().__init__(ip_adress, scn, host_id)
        self.set_controller_type()
        print(f'scn: {scn}')

    # super().__init__(ip_adress, host_id, scn)
    # self.set_controller_type()
    # print(f'scn: {scn}')

    # @staticmethod
    # def make_val_stages_for_get_stage_UG405_potok(option):
    #     """ В зависимости от опции функция формирует словарь с номером и значением фазы
    #     """
    #     # print(f'option: {option}')
    #     if option == 'get':
    #         mask_after_8stages_get = ['01', '02', '04', '08', '10', '20', '40', '80']
    #         stages = ['01', '02', '04', '08', '10', '6', '@', '80']
    #
    #         # одна итерация цикла 8 фаз. В stages изначально уже лежат 8 фаз
    #         # поэтому range(7) -> 8 + 7 * 8 = 64. тогда range(8) -> 8 + 8 * 8, range(9) -> 8 + 9 * 8 и т.д.
    #         for i in range(7):
    #             temp_lst = [
    #                 f'{el}{"00" * (i + 1)}' if el != '40' else f'{el}{"00" * (i + 1)}@' for el in mask_after_8stages_get
    #             ]
    #             stages = stages + temp_lst
    #         # print(stages)
    #
    #         get_val_stage_UG405_POTOK = {k: v for v, k in enumerate(stages, 1)}
    #         return get_val_stage_UG405_POTOK
    #         # print(get_val_stage_UG405_POTOK)
    #     elif option == 'set':
    #         stg_mask = ['01', '02', '04', '08', '10', '20', '40', '80']
    #         return {k: v for k, v in enumerate((f'{i}{j * "00"}' for j in range(8) for i in stg_mask), 1)}
    #         # mask_after_8stages_set = ['01', '02', '04', '08', '10', '20', '40', '80']
    #         # # stgs = [f'{i}{j*"00"}' for i in mask_after_8stages_set for j in range(8)]
    #         # stages = [f'{el}{"00" * (i + 1)}' for el in mask_after_8stages_set for i in range(7)]
    #         #
    #         # for i in range(7):
    #         #     temp_lst = [
    #         #         f'{el}{"00" * (i + 1)}' for el in mask_after_8stages_set
    #         #     ]
    #         #     stages = stages + temp_lst
    #         # set_val_stage_UG405_POTOK = {str(k): v for k, v in enumerate(stages, 1)}
    #         # # print(set_val_stage_UG405_POTOK)
    #         # return set_val_stage_UG405_POTOK

    # @staticmethod
    # def convert_val_to_num_stage_get_req(val: str) -> int | None:
    #
    #     mask_after_8stages_get = ['01', '02', '04', '08', '10', '20', '40', '80']
    #     stages = ['01', '02', '04', '08', '10', '6', '@', '80']
    #
    #     # одна итерация цикла 8 фаз. В stages изначально уже лежат 8 фаз
    #     # поэтому range(7) -> 8 + 7 * 8 = 64. тогда range(8) -> 8 + 8 * 8, range(9) -> 8 + 9 * 8 и т.д.
    #     for i in range(7):
    #         temp_lst = [
    #             f'{el}{"00" * (i + 1)}' if el != '40' else f'{el}{"00" * (i + 1)}@' for el in mask_after_8stages_get
    #         ]
    #         stages = stages + temp_lst
    #     # print(stages)
    #     values = {k: v for v, k in enumerate(stages, 1)}
    #     return values.get(val)

    @staticmethod
    def convert_val_to_num_stage_set_req(val: str) -> int | None:

        stg_mask = ['01', '02', '04', '08', '10', '20', '40', '80']
        values = {str(k): v for k, v in enumerate((f'{i}{j * "00"}' for j in range(8) for i in stg_mask), 1)}
        return values.get(val)

    def convert_values_flash_dark(self, val):
        converted_values_flash_dark = {
            '1': '2', 'true': '2', 'on': '2', 'вкл': '2', '2': '2',
            '0': '0', 'false': '0', 'off': '0', 'выкл': '0',
        }
        return converted_values_flash_dark.get(val)

    """ GET REQUEST """

    def _mode_define(self, utcType2OperationMode: str, isFlash: str, isDark: str,
                     isManual: str, plan: str, hasDetErrors: str, localAdaptiv: str) -> str:
        """ Определяет текщий ружим ДК.
        :arg equipment_status (str): Текущий режим работы контроллера:
                                     workingProperly(1),
                                     powerUp(2),
                                     dark(3),
                                     flash(4),
                                     partialFlash(5),
                                     allRed(6)

        :arg plan (str): Текущий номер плана
        :arg softstat180_181 (str): Текущее состояние входов 180 и 181
        :arg num_logics (str): Количество детекторных логик

        :return str: Возращает текущий режим ДК(Фикс/Адаптива/КУ и т.д)
        """
        # utcType2OperationMode, hasErrors, isFlash, isDark, isManual, plan, stage, hasDetErrors,
        # localAdaptiv

        if isFlash is not None and isFlash.isdigit() and int(isFlash) in range(1, 5):
            val_mode = '4'
        elif isDark == '1':
            val_mode = '3'
        elif isManual == '1':
            val_mode = '10'
        elif utcType2OperationMode == '3' and plan == '0':
            val_mode = '1'
        elif localAdaptiv == '1' and hasDetErrors == '0' and plan != '0':
            val_mode = '8'
        elif (localAdaptiv == '0' or hasDetErrors == '1') and plan != '0':
            val_mode = '12'
        else:
            val_mode = '--'
        return self.statusMode.get(val_mode)

        # if equipment_status != '1':
        #     val_mode = equipment_status
        # elif status_mode == '11' and plan == '16':
        #     val_mode = status_mode
        # elif status_mode != '11' and status_mode in ('8', '10', '12'):
        #     val_mode = status_mode
        # else:
        #     val_mode = '--'
        # return self.statusMode.get(val_mode)

    def get_current_mode(self, varBinds: list) -> tuple:
        utcType2OperationMode = hasErrors = isFlash = isDark = isManual = plan = stage = \
            hasDetErrors = localAdaptiv = None

        new_varBins = []
        for data in varBinds:
            oid, val = data[0].__str__(), data[1].prettyPrint()
            oid = oid.replace(self.scn, '') if oid.endswith(self.scn) else oid
            if oid in self.get_state_oids:
                if oid == Oids.utcType2OperationMode.value:
                    utcType2OperationMode = val
                elif oid == Oids.utcReplyCF.value:
                    hasErrors = val
                elif oid == Oids.utcReplyFR.value:
                    isFlash = val
                elif oid == Oids.potokP_utcReplyDarkStatus.value:
                    isDark = val
                elif oid == Oids.utcReplyMC.value:
                    isManual = val
                elif oid == Oids.potokP_utcReplyPlanStatus.value:
                    plan = val
                elif oid == Oids.utcReplyGn.value:
                    stage = self.convert_val_to_num_stage_get_req(val)
                elif oid in Oids.utcReplyDF.value:
                    hasDetErrors = val
                elif oid in Oids.potokP_utcReplyLocalAdaptiv.value:
                    localAdaptiv = val
                # if self.user_oids and (oid in self.user_oids):
                #     new_varBins.append(data)
            else:
                new_varBins.append(data)

        mode = self._mode_define(utcType2OperationMode, isFlash, isDark, isManual, plan, hasDetErrors, localAdaptiv)
        curr_state = {
            EntityJsonResponce.CURRENT_MODE.value: mode,
            EntityJsonResponce.CURRENT_STAGE.value: stage,
            EntityJsonResponce.CURRENT_PLAN.value: plan,
        }
        return new_varBins, curr_state

    """*******************************************************************
    ***                          SET-REQUEST                          ****   
    **********************************************************************
    """

    async def set_stage(self, value='0', timeout=0, retries=0):
        """"
        Устанавливает  фазу.
        :param value:  Номер фазы в десятичном виде
        :param retries:
        :param timeout:
        :return: ErrorIndication, varBinds
        """

        if not self.scn:
            self.scn = await self.get_scn()

        if value.lower() in {'0', 'локал', 'false', 'сброс', 'reset'}:
            oids = (
                (Oids.utcType2OperationMode.value, Integer32(1)),
                (Oids.utcControlTO.value + self.scn, Integer32(0)),
            )
        else:
            converted_val = self.convert_val_to_num_stage_set_req(value)
            oids = (
                (Oids.utcType2OperationModeTimeout.value, Integer32(90)),
                (Oids.utcType2OperationMode.value, Integer32(3)),
                (Oids.utcControlTO.value + self.scn, Integer32(1)),
                (Oids.utcControlFn.value + self.scn, OctetString(hexValue=converted_val)),
            )
        return await self.set_request_base(self.ip_adress, self.community_write, oids, timeout=timeout, retries=retries)

    async def set_dark(self, value='0', timeout=0, retries=0):
        """"
        Устанавливает  фазу.
        :param value:  Номер фазы в десятичном виде
        :param retries:
        :param timeout:
        :return: ErrorIndication, varBinds
        """

        if not self.scn:
            self.scn = await self.get_scn()

        oids = (
            (Oids.utcType2OperationMode.value, Integer32(3)),
            (Oids.utcControlTO.value + self.scn, Integer32(1)),
            (Oids.utcControlLO.value + self.scn, Integer32(self.convert_values_flash_dark(value))),
        )

        return await self.set_request_base(self.ip_adress, self.community_write, oids, timeout=timeout, retries=retries)

    async def set_flash(self, value='0', timeout=0, retries=0):
        """"
        Устанавливает  фазу.
        :param value:  Номер фазы в десятичном виде
        :param retries:
        :param timeout:
        :return: ErrorIndication, varBinds
        """

        if not self.scn:
            self.scn = await self.get_scn()

        oids = (
            (Oids.utcType2OperationMode.value, Integer32(3)),
            (Oids.utcControlTO.value + self.scn, Integer32(1)),
            (Oids.utcControlFF.value + self.scn, Integer32(self.convert_values_flash_dark(value))),
        )

        return await self.set_request_base(self.ip_adress, self.community_write, oids, timeout=timeout, retries=retries)

    async def set_restartProgramm(self, value='1', timeout=0, retries=0):

        if not self.scn:
            self.scn = await self.get_scn()

        oids = (
            (Oids.potokP_utcControRestartProgramm.value + self.scn, Integer32(value)),
        )
        return await self.set_request_base(self.ip_adress, self.community_write, oids, timeout=timeout, retries=retries)


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

    def __init__(self, ip_adress, host_id=None, scn=None):
        super().__init__(ip_adress, scn, host_id)
        self.set_controller_type()
        print(f'scn: {scn}')

    """ GET REQUEST """

    """ archive methods(not usage) """

    """ SET REQUEST """

    async def set_utcControlFn(self, value: str, timeout=1, retries=1):
        """
            Устанавливает Fn бит(фаза).
            :param timeout: Таймаут подключения
            :param retries: Количетсво попыток подключения
            :param value -> str. В аргумент необходимо передавать номер фазы в десятичном виде.
        """
        converted_to_hex_val = self.val_stage_set_request.get(value)
        oids = [ObjectType(ObjectIdentity(self.utcControlTO + self.scn), Integer32(1)),
                ObjectType(ObjectIdentity(self.utcControlFn + self.scn), OctetString(hexValue=converted_to_hex_val))]
        return await self.set_request(self.ip_adress, self.community, oids, timeout=timeout, retries=retries)

    async def set_stage(self, value: str, timeout=1, retries=1):
        """
            Устанавливает фазу.
            :param timeout: Таймаут подключения
            :param retries: Количетсво попыток подключения
            :param converted_to_hex_val -> В аргумент необходимо передавать значение 1 или 0.
        """
        # print('set_stage_UG405_peek_values')
        # print(self.val_stage_set_request)

        if value == '0':
            oids = [ObjectType(ObjectIdentity(self.utcType2OperationMode), Integer32(1)),
                    ObjectType(ObjectIdentity(self.utcControlTO + self.scn), Integer32(0))]
            return await self.set_request(self.ip_adress, self.community, oids, timeout=timeout, retries=retries)

        converted_to_hex_val = self.val_stage_set_request.get(value)

        lock = asyncio.Lock()
        async with lock:
            result = await self.get_utcType2OperationMode()

            print(f' async with lock get_utcType2OperationMode')
            print(f' result,  {result}')

        result = result[0]
        if result == '1':
            async with lock:
                print('async with lock 1')
                oids = [ObjectType(ObjectIdentity(self.utcType2OperationModeTimeout), Integer32(90)),
                        ObjectType(ObjectIdentity(self.utcType2OperationMode), Integer32(2))]
                res = await self.set_request(self.ip_adress, self.community, oids, timeout=timeout, retries=retries)
                print(f'resval 1: {res}')
            async with lock:
                print('async with lock 2')
                oids = [ObjectType(ObjectIdentity(self.utcType2OperationMode), Integer32(3))]
                res = await self.set_request(self.ip_adress, self.community, oids, timeout=timeout, retries=retries)
                print(f'res, val 2: {res}')
        elif result in ('2', '3'):
            async with lock:
                print('async with lock elif val in (...)')
                oids = [ObjectType(ObjectIdentity(self.utcType2OperationMode), Integer32(3))]
                res = await self.set_request(self.ip_adress, self.community, oids, timeout=timeout, retries=retries)
                print(f'result, val async with lock elif val in (...): {res}')
        else:
            raise ValueError
        async with lock:
            print('async with lock установить фазу')
            oids = [ObjectType(ObjectIdentity(self.utcType2OperationMode), Integer32(3)),
                    ObjectType(ObjectIdentity(self.utcControlTO + self.scn), Integer32(1)),
                    ObjectType(ObjectIdentity(self.utcControlFn + self.scn),
                               OctetString(hexValue=converted_to_hex_val))]
            return await self.set_request(self.ip_adress, self.community, oids, timeout=timeout, retries=retries)

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


"""" SSH MANAGEMENT """


class ConnectionSSH(BaseCommon):
    access_levels = {
        'swarco_itc': (os.getenv('swarco_itc_login'), os.getenv('swarco_itc_password')),
        'swarco_r': (os.getenv('swarco_r_login'), os.getenv('swarco_r_password')),
        'peek_r': (os.getenv('peek_r_login'), os.getenv('peek_r_password')),
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

    @staticmethod
    async def read_timed(stream: asyncssh.SSHReader,
                         timeout: float = 1,
                         bufsize: int = 1024) -> str:
        """Read data from a stream with a timeout."""
        ret = ''
        while True:
            try:
                ret += await asyncio.wait_for(stream.read(bufsize), timeout)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                return ret

    async def acreate_proc(self, ip: str, username: str, password: str, commands: Iterable, type_req: str = None):
        errorIndication = varBinds = None
        # self.type_curr_request = EntityJsonResponce.TYPE_SSH_REQUEST_SET.value
        try:
            async with asyncssh.connect(host=ip,
                                        username=username,
                                        password=password,
                                        kex_algs="+diffie-hellman-group1-sha1",
                                        encryption_algs='+aes256-cbc',
                                        known_hosts=None) as conn:
                async with conn.create_process(term_type="ansi", encoding='latin-1', recv_eof=True) as proc:
                    await self.read_timed(proc.stdout, timeout=3, bufsize=4096)
                    for command in commands:
                        proc.stdin.write(command)
                    # await self.read_timed(proc.stdout, timeout=3, bufsize=4096)
                    response = await self.read_timed(proc.stdout, timeout=3, bufsize=4096)
                    logger.debug(response)
                    err, varBinds = None, response.encode('iso-8859-1')
                    logger.debug(response)

        except asyncssh.misc.PermissionDenied:
            errorIndication, varBinds = 'Permission denied', []
        except (OSError, asyncssh.Error) as exc:
            errorIndication, varBinds = 'SSH connection failed', []
        except Exception as err:
            errorIndication, varBinds = 'System error', []
            logger.error('Ошибка выполнения программы: {}'.format(err))
        finally:
            return errorIndication, varBinds, self, type_req


            #     # r_enc = r.decode('iso-8859-1').encode('utf-8')
            # return response


class SwarcoSSH(ConnectionSSH):
    inp_stages = {str(stage): str(inp) for stage, inp in zip(range(1, 9), range(104, 112))}

    @staticmethod
    def make_any_commands(commands_from_user, separ=','):
        return (command + '\n' for command in commands_from_user.split(separ))

    @staticmethod
    def commands_set_stage(num_stage):
        return itertools.chain('inp102=1\n', f'inp{SwarcoSSH.inp_stages.get(num_stage)}=1\n', 'instat102 ?\n')

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

    def parse_stdout_from_shell(self, varBinds: list) -> tuple:
        pass



    # async def run_client():
    #     async with asyncssh.connect(host='10.45.154.16',
    #                                 # username=os.getenv('swarco_itc_login'),
    #                                 # password=os.getenv('swarco_itc_password'),
    #                                 username='itc',
    #                                 password='level1NN',
    #                                 kex_algs="+diffie-hellman-group1-sha1",
    #                                 known_hosts=None) as conn:
    #         async with conn.create_process(term_type="ansi", encoding='latin-1', recv_eof=True) as proc:
    #             response = await read_timed(proc.stdout, timeout=3, bufsize=4096)
    #             proc.stdin.write('lang UK\n')
    #             proc.stdin.write('l2\n')
    #             proc.stdin.write('2727\n')
    #             print('Response:', response)
    #             for i in range(1, 4):
    #                 if i != 2:
    #                     proc.stdin.write(f'inp10{i}=1\n')
    #             proc.stdin.write('CBMEM10 ?\n')
    #
    #             response = await read_timed(proc.stdout, timeout=3, bufsize=4096)
    #             print('Response:', response)
    #             with open('log', 'w') as f:
    #                 f.write(response)
    #
    #             logger.debug(response)
    #             r = response.encode('iso-8859-1')
    #             logger.debug(r)
    #             r_enc = r.decode('iso-8859-1').encode('utf-8')
    #             logger.debug(r_enc)
    #             print(r)
    #             print(r_enc.decode('utf-8').splitlines())
    #             for line in r_enc.decode('utf-8').splitlines():
    #                 print(f'line: {line}')
    #
    #             return response


class AsyncSwarcoSsh(SwarcoSSH):

    async def set_stage(self, val: str) -> tuple:
        """"
        Устанавливает фазу.
        :arg val: номер фазы
        :return: Состояние входов 102-112
        """
        username, password = self.access_levels.get('swarco_itc')
        commands = itertools.chain(self.commands_l2(), self.commands_reset_inp102_111(), self.commands_set_stage(val))
        return await self.acreate_proc(
            ip=self.ip_adress,
            username=username,
            password=password,
            commands=commands
        )




"""" WEB MANAGEMENT """


class PeekWeb(BaseCommon):
    # MAN_INPUTS = {'MPP_MAN', 'MPP_FL', 'MPP_OFF', 'MPP_PH1', 'MPP_PH2', 'MPP_PH3',
    #               'MPP_PH4', 'MPP_PH5', 'MPP_PH6', 'MPP_PH7', 'MPP_PH8'}
    MAN_INPUTS_MPP_PH = {'MPP_PH1', 'MPP_PH2', 'MPP_PH3', 'MPP_PH4',
                         'MPP_PH5', 'MPP_PH6', 'MPP_PH7', 'MPP_PH8'}
    MAN_INPUTS_STAGES = {'1': 'MPP_PH1', '2': 'MPP_PH2', '3': 'MPP_PH3', '4': 'MPP_PH4',
                         '5': 'MPP_PH5', '6': 'MPP_PH6', '7': 'MPP_PH7', '8': 'MPP_PH8',
                         '0': 'reset_man'}

    ACTUATOR_RESET = '0'
    ACTUATOR_OFF = '1'
    ACTUATOR_ON = '2'
    ACTUATOR_VALUES = {
        'ВФ': ACTUATOR_RESET,
        'ВЫКЛ': ACTUATOR_OFF,
        'ВКЛ': ACTUATOR_ON
    }

    ACTUATOR_VALUES2 = {
        ACTUATOR_RESET: 'ВФ',
        ACTUATOR_OFF: 'ВЫКЛ',
        ACTUATOR_ON: 'ВКЛ'
    }

    synonyms_red_yellow_dark = {
        '1': 'ВКЛ',
        '0': 'ВФ'
    }

    INPUTS = 'INPUTS'
    USER_PARAMETERS = 'USER_PARAMETERS'
    CURRENT_STATE = 'STATE'

    GET_INPUTS = 'GET_INPUTS'
    SET_INPUTS = 'SET_INPUTS'
    GET_USER_PARAMETERS = 'GET_USER_PARAMETERS'
    SET_USER_PARAMETERS = 'SET_USER_PARAMETERS'
    GET_CURRENT_STATE = 'GET_CURRENT_MODE'

    routes_url = {
        GET_INPUTS: '/hvi?file=cell1020.hvi&pos1=0&pos2=-1',
        SET_INPUTS: '/hvi?file=data.hvi&page=cell1020.hvi',
        GET_USER_PARAMETERS: '/hvi?file=cell6710.hvi&pos1=0&pos2=-1',
        SET_USER_PARAMETERS: '/hvi?file=data.hvi&page=cell6710.hvi',
        GET_CURRENT_STATE: '/hvi?file=m001a.hvi&pos1=0&pos2=-1'
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    }
    cookies = {'uic': '3333'}
    allowed_inputs = {'MKEY1', 'MKEY2', 'MKEY3', 'MKEY4', 'MKEY5',
                      'MPP_MAN', 'MPP_FL', 'MPP_OFF', 'MPP_PH1', 'MPP_PH2', 'MPP_PH3', 'MPP_PH4', 'MPP_PH5',
                      'MPP_PH6', 'MPP_PH7', 'MPP_PH8',
                      'CP_OFF', 'CP_FLASH', 'CP_RED', 'CP_AUTO'}

    JSON_SET_COMMAND_BODY = (
        EntityJsonResponce.RESULT.value,
        EntityJsonResponce.TYPE_COMMAND.value,
        EntityJsonResponce.VALUE.value
    )

    def __init__(self, ip_adress: str, host_id: str = None):
        super().__init__(ip_adress, host_id)
        self.ip_adress = ip_adress
        self.host_id = host_id
        self.controller_type = AvailableControllers.PEEK.value
        self.last_read_parameters = {}
        self.last_set_commands = []
        # self.inputs = {}
        # self.user_parameters = {}

    def parse_inps_and_user_param_content(self, content: str, create_self_attr: bool = False):

        parsed_data = {}
        for line in (
                line.split(';')[1:] for line in content.splitlines() if line.startswith(':D')
        ):
            index, num, name, val1, val2, val3 = line
            # val1, val2 и val3 зависят от типа получаемых данных.
            # если получаем ВВОДЫ:
            # val1 -> Состояние val2 -> Время, val3 -> АКТУАТОР
            # если Параметры программы:
            # val1 -> Значение, val2 -> Мин. val3 -> Макс
            parsed_data[name] = index, val1, val2, val3

        if create_self_attr:
            self.last_read_parameters = {parsed_data.get(k)[0]: k for k in parsed_data}
            logger.debug(parsed_data)
            # if 'MPP_MAN' in parsed_data:
            #     logger.debug({parsed_data.get(k)[0]: k for k in parsed_data})
            #     self.inputs = {parsed_data.get(k)[0]: k for k in parsed_data}
            # elif 'FIX_TIME' in parsed_data:
            #     self.user_parameters = {parsed_data.get(k)[0]: k for k in parsed_data}
        # logger.debug('self.inputs {}'.format(self.inputs))
        # logger.debug('self.user_parameters %s', self.user_parameters)


        return parsed_data

    def parse_varBinds(self, content: str):
        if self.get_entity:
            content = [
                line.split(';')[3:][0] for line in content.replace(" ", '').splitlines() if line.startswith(':D')
            ]
            mode, stage = content[6].split('(')
            stage = stage.replace(')', '')
            plan = re.sub('[^0-9]', '', content[0])
            plan = str(int(plan) if plan.isdigit() else plan)
            param_plan = content[1]
            current_time = content[2]
            current_err = content[3]
            current_state = content[4]
            current_mode = self.statusMode.get(mode)
            part_of_json = {
            EntityJsonResponce.CURRENT_MODE.value: current_mode,
            EntityJsonResponce.CURRENT_STAGE.value: stage,
            EntityJsonResponce.CURRENT_PLAN.value: plan,
            EntityJsonResponce.CURRENT_PARAM_PLAN.value: param_plan,
            EntityJsonResponce.CURRENT_TIME.value: current_time,
            EntityJsonResponce.CURRENT_ERRORS.value: current_err,
            EntityJsonResponce.CURRENT_STATE.value: current_state,
        }
        elif self.set_entity:
            part_of_json = {'raw_data': {'web_parameters': self.last_set_commands}}
        else:
            raise ValueError
        # logger.debug(self.last_set_commands)

        return part_of_json

    def put_to_last_val(self, data):
        self.last_set_commands.append(data)

    def _check_errors_after_web_request(self, content, type_request):

        result_text_message = None
        if type(content) == str and len(content) > 100:
            error_request = None
        elif content == TimeoutError:
            if type_request == EntityJsonResponce.TYPE_WEB_REQUEST_SET:
                result_text_message = EntityJsonResponce.COMMAND_SEND_ERROR.value
            error_request = EntityJsonResponce.TIMEOUT_ERROR_WEB_REQUEST_MSG.value
        elif content == TypeError:
            if type_request == EntityJsonResponce.TYPE_WEB_REQUEST_SET:
                result_text_message = EntityJsonResponce.COMMAND_SEND_ERROR.value
            error_request = EntityJsonResponce.TYPE_CONTROLLER_ERROR_MSG.value
        else:
            raise ValueError
        return error_request, result_text_message

    def get_current_mode(self, content: str):
        content = [
            line.split(';')[3:][0] for line in content.replace(" ", '').splitlines() if line.startswith(':D')
        ]
        mode, stage = content[6].split('(')
        stage = int(stage.replace(')', ''))
        plan = re.sub('[^0-9]', '', content[0])
        plan = int(plan) if plan.isdigit() else plan
        param_plan = int(content[1]) if content[1].isdigit() else content[1]
        current_time = content[2]
        current_err = content[3]
        current_state = content[4]
        current_mode = self.statusMode.get(mode)

        processed_data = {
            EntityJsonResponce.CURRENT_MODE.value: current_mode,
            EntityJsonResponce.CURRENT_STAGE.value: stage,
            EntityJsonResponce.CURRENT_PLAN.value: plan,
            EntityJsonResponce.CURRENT_PARAM_PLAN.value: param_plan,
            EntityJsonResponce.CURRENT_TIME.value: current_time,
            EntityJsonResponce.CURRENT_ERRORS.value: current_err,
            EntityJsonResponce.CURRENT_STATE.value: current_state,
        }

        return [], processed_data

    async def get_content_from_web(self, route_type, timeout=1) -> tuple:
        url = f'http://{self.ip_adress}{self.routes_url.get(route_type)}'
        errorIndication = content = None
        try:
            timeout = aiohttp.ClientTimeout(timeout)
            async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies, timeout=timeout) as session:
                async with session.get(url, timeout=timeout) as s:
                    if s.status != 200:
                        raise TypeError(EntityJsonResponce.TYPE_CONTROLLER_ERROR_MSG.value)
                    content = await s.text()
                    errorIndication = None

        except aiohttp.client_exceptions.ClientConnectorError:
            errorIndication, content = aiohttp.client_exceptions.ClientConnectorError, []
        except asyncio.TimeoutError:
            errorIndication, content = EntityJsonResponce.TIMEOUT_ERROR_WEB_REQUEST_MSG.value, []
        except TypeError:
            errorIndication, content = EntityJsonResponce.TYPE_CONTROLLER_ERROR_MSG.value, []
        finally:
            return errorIndication, content

    async def get_request(self, get_mode: bool = True, timeout=1) -> tuple:
        """
        Метод запроса контента web страницы получения текущего состояния ДК
        :param get_mode:
        :param timeout:
        :return tuple: (errorIndication, varBinds)
        """
        self.put_to_get_entity('get_mode')
        self.put_to_req_data({'protocol': 'http', 'type': 'get'})
        errorIndication, content = await self.get_content_from_web(self.GET_CURRENT_STATE, timeout=timeout)
        self.errorIndication, self.varBinds = errorIndication, content
        return errorIndication, content, self

    async def set_stage(self, stage_to_set: str, timeout=3) -> tuple:


        self.put_to_req_data({'protocol': 'http', 'type': 'set', 'request_time': self.set_curr_datetime()})
        self.set_entity['set_stage'] = stage_to_set

        input_name_to_set = self.MAN_INPUTS_STAGES.get(stage_to_set)
        errorIndication, inputs_web_content = await self.get_content_from_web(self.GET_INPUTS)
        # error_request, result_text_msg = self._check_errors_after_web_request(inputs_web_content,
        #                                                                       EntityJsonResponce.TYPE_WEB_REQUEST_SET)
        if errorIndication is None:
            inputs = self.parse_inps_and_user_param_content(inputs_web_content, create_self_attr=True)
            timeout = aiohttp.ClientTimeout(timeout)
            async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies, timeout=timeout) as session:
                set_CP_AUTO = False
                async with asyncio.TaskGroup() as tg1:
                    params_to_set = []
                    blocked_inps = [
                        'MPP_FL', 'MPP_OFF', 'CP_OFF', 'CP_FLASH', 'CP_RED',
                    ]
                    for inp in blocked_inps:
                        if inputs.get(inp)[1] == '1':
                            set_CP_AUTO = True
                            if inp.startswith('MPP_'):
                                params_to_set.append((inputs.get(inp)[0], self.ACTUATOR_OFF))
                            else:
                                params_to_set.append(params_to_set.append((inputs.get(inp)[0], self.ACTUATOR_RESET)))
                    if params_to_set:
                        tasks_res = [
                            tg1.create_task(self.set_val_to_web(self.SET_INPUTS, session, params_to_set))
                        ]

                if set_CP_AUTO:
                    await self.set_val_to_web(self.SET_INPUTS, session,
                                              (inputs.get('CP_AUTO')[0], self.ACTUATOR_RESET))
                    await self.set_val_to_web(self.SET_INPUTS, session,
                                              (inputs.get('CP_AUTO')[0], self.ACTUATOR_ON))

                async with asyncio.TaskGroup() as tg:
                    data_param_to_set = []
                    if set_CP_AUTO:
                        data_param_to_set.append((inputs.get('CP_AUTO')[0], self.ACTUATOR_RESET))

                    if input_name_to_set == 'reset_man':
                        data_param_to_set.append((inputs.get('MPP_MAN')[0], self.ACTUATOR_OFF))
                        for inp in self.MAN_INPUTS_MPP_PH:
                            data_param_to_set.append((inputs.get(inp)[0], self.ACTUATOR_RESET))
                    else:
                        for inp in inputs:
                            if inp == 'MPP_MAN':
                                data_param_to_set.append((inputs.get(inp)[0], self.ACTUATOR_ON))
                            elif (inp in self.MAN_INPUTS_MPP_PH and inp != input_name_to_set
                                  and inputs.get(inp)[1] == '1'):
                                data_param_to_set.append((inputs.get(inp)[0], self.ACTUATOR_OFF))
                            elif inp == input_name_to_set:
                                data_param_to_set.append((inputs.get(inp)[0], self.ACTUATOR_ON))
                    tasks_res = [tg.create_task(self.set_val_to_web(self.SET_INPUTS, session, data_params))
                                 for data_params in data_param_to_set]

            if all(res.result() == 200 for res in tasks_res):
                errorIndication = None

        return errorIndication, self.last_set_commands, self

        # processed_data = (
        #     error_request,
        #     AvailableControllers.PEEK.value,
        #     self.host_id,
        #     result_text_msg,
        #     EntityJsonResponce.SET_STAGE_MPP_MAN.value,
        #     stage_to_set
        # )
        #
        # return BaseCommon.make_json_responce(self.ip_adress,
        #                                      json_entity=self.base_json_entity + self.JSON_SET_COMMAND_BODY,
        #                                      varBinds=processed_data,
        #                                      )

    # async def set_val_common(self, set_type, data, timeout=3):
    #
    #     self.put_to_req_data({'protocol': 'http', 'type': 'set', 'request_time': self.set_curr_datetime()})
    #
    #     set_CP_AUTO = False
    #     if set_type == self.SET_USER_PARAMETERS:
    #         # type_command_ = EntityJsonResponce.SET_USER_PARAMETERS_WEB.value
    #         part_url = self.GET_USER_PARAMETERS
    #     elif set_type == self.SET_INPUTS:
    #         # type_command_ = EntityJsonResponce.SET_MAN_INPUTS_WEB.value
    #         part_url = self.GET_INPUTS
    #     else:
    #         raise TypeError
    #
    #     errorIndication, inputs_web_content = await self.get_content_from_web(part_url)
    #
    #     if errorIndication is None:
    #         params_from_web = self.parse_inps_and_user_param_content(inputs_web_content, create_self_attr=True)
    #         params_to_set = {}
    #         for param in data.split(';'):
    #             if param in {'CP_RED=ВФ', 'CP_RED=ВЫКЛ', 'MPP_FL=ВЫКЛ', 'MPP_FL=ВФ', 'MPP_OFF=ВКЛ', 'MPP_OFF=ВФ'}:
    #                 set_CP_AUTO = True
    #             param, val = param.split('=')
    #             if param in params_from_web:
    #                 if set_type == 'SET_INPUTS':
    #                     val = self.ACTUATOR_VALUES.get(val)
    #                 params_to_set[params_from_web.get(param)[0]] = val
    #
    #         if not params_to_set:
    #             raise ValueError
    #
    #         timeout = aiohttp.ClientTimeout(3)
    #         async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies, timeout=timeout) as session:
    #             async with asyncio.TaskGroup() as tg:
    #                 tasks_res = [tg.create_task(self.set_val_to_web(set_type, session, data_params))
    #                              for data_params in params_to_set.items()]
    #             if set_CP_AUTO:
    #                 await self.set_val_to_web(set_type, session, (params_from_web.get('CP_AUTO')[0], '2'))
    #                 await self.set_val_to_web(set_type, session, (params_from_web.get('CP_AUTO')[0], '0'))
    #
    #         if all(res.result() == 200 for res in tasks_res):
    #             errorIndication = None
    #         else:
    #             errorIndication = EntityJsonResponce.COMMAND_SEND_ERROR.value
    #
    #     return errorIndication, self.last_set_commands, self

    async def set_val_common(self, set_type, data, timeout=3):

        self.put_to_req_data({'protocol': 'http', 'type': 'set', 'request_time': self.set_curr_datetime()})

        set_CP_AUTO = False
        if set_type == self.SET_USER_PARAMETERS:
            # type_command_ = EntityJsonResponce.SET_USER_PARAMETERS_WEB.value
            part_url = self.GET_USER_PARAMETERS
        elif set_type == self.SET_INPUTS:
            # type_command_ = EntityJsonResponce.SET_MAN_INPUTS_WEB.value
            part_url = self.GET_INPUTS
        else:
            raise TypeError

        errorIndication, inputs_web_content = await self.get_content_from_web(part_url)

        if errorIndication is None:
            params_from_web = self.parse_inps_and_user_param_content(inputs_web_content, create_self_attr=True)
            params_to_set = {}
            params_to_set2 = []
            for param in data.split(';'):
                if param in {'CP_RED=ВФ', 'CP_RED=ВЫКЛ', 'MPP_FL=ВЫКЛ', 'MPP_FL=ВФ', 'MPP_OFF=ВКЛ', 'MPP_OFF=ВФ'}:
                    set_CP_AUTO = True
                param, val = param.split('=')
                if param in params_from_web:
                    if set_type == 'SET_INPUTS':
                        val = self.ACTUATOR_VALUES.get(val)
                    params_to_set2.append((params_from_web.get(param)[0], val))
                    # params_to_set[params_from_web.get(param)[0]] = val

            if not params_to_set2:
                raise ValueError

            timeout = aiohttp.ClientTimeout(timeout)
            async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies, timeout=timeout) as session:
                async with asyncio.TaskGroup() as tg:
                    # tasks_res = [tg.create_task(self.set_val_to_web(set_type, session, data_params))
                    #              for data_params in params_to_set.items()]
                    tasks_res = [tg.create_task(self.set_val_to_web(set_type, session, data_params))
                                 for data_params in params_to_set2]
                if set_CP_AUTO:
                    await self.set_val_to_web(set_type, session, (params_from_web.get('CP_AUTO')[0], '2'))
                    await self.set_val_to_web(set_type, session, (params_from_web.get('CP_AUTO')[0], '0'))

            if all(res.result() == 200 for res in tasks_res):
                errorIndication = None
            else:
                errorIndication = EntityJsonResponce.COMMAND_SEND_ERROR.value

        return errorIndication, self.last_set_commands, self

    async def set_val_to_web(self, type_set_request, session, data_params, ):

        index, value = data_params
        self.put_to_last_val({self.last_read_parameters.get(index): self.ACTUATOR_VALUES2.get(value)})

        if type_set_request == self.SET_INPUTS:
            params = {'par_name': f'XIN.R20/{index}', 'par_value': value}
            url = f'http://{self.ip_adress}{self.routes_url.get(self.SET_INPUTS)}'
        elif type_set_request == self.SET_USER_PARAMETERS:
            url = f'http://{self.ip_adress}{self.routes_url.get(self.SET_USER_PARAMETERS)}'
            params = {'par_name': f'PARM.R1/{index}', 'par_value': value}
        else:
            raise TypeError

        async with session.post(url=url, data=params) as response:
            await response.text()
            return response.status

    async def set_flash(self, value: str) -> tuple:
        self.set_entity['set_flash'] = value
        return await self.set_val_common(self.SET_INPUTS, f'MPP_FL={self.synonyms_red_yellow_dark.get(value)}')

    async def set_dark(self, value: str) -> tuple:
        self.set_entity['set_dark'] = value
        return await self.set_val_common(self.SET_INPUTS, f'MPP_OFF={self.synonyms_red_yellow_dark.get(value)}')

    async def set_allred(self, value: str) -> tuple:
        self.set_entity['set_red'] = value
        val_to_set = 'CP_RED=ВКЛ' if value.lower() in ('1', 'true', 'вкл') else 'CP_RED=ВФ'
        if val_to_set != 'CP_RED=ВКЛ':
            await self.set_val_common(self.SET_INPUTS, 'CP_RED=ВЫКЛ')
        logger.debug(val_to_set)
        return await self.set_val_common(self.SET_INPUTS, val_to_set)

    async def reset_all_man_inputs(self):
        self.set_entity['reset_mpp_inputs'] = True
        inputs = itertools.chain(['MPP_MAN=ВФ', 'MPP_FL=ВФ', 'MPP_OFF=ВФ'], [f'MPP_PH{i}=ВФ' for i in range(1, 9)])
        return await self.set_val_common(self.SET_INPUTS, ';'.join(list(inputs)))



        # res, actuator_val = self.validate_val(value, self.type_set_request_cp_red)
        #
        # if not res:
        #     err_message = actuator_val
        #     return err_message
        # inputs_to_set = self.make_inputs_to_set_reset_flash_dark(True, 'CP_RED', actuator_val)
        #
        # return await self.main_async(inputs_to_set,
        #                              self.type_set_request_man_flash_dark_allred,
        #                              True if actuator_val == self.ACTUATOR_RESET else False)
    #
    # async def get_data_from_web2(self, path_to_hvi, type, session, data=None):
    #     async def get_request(s):
    #         url = f'http://{self.ip_adress}{path_to_hvi}'
    #         elements = {}
    #         async with s.get(url=url) as response:
    #             resp_result = await response.text()
    #
    #             for line in (
    #                     line.split(';')[1:] for line in resp_result.splitlines() if line.startswith(':D')
    #             ):
    #                 index, num, name, val1, val2, val3 = line
    #                 # val1, val2 и val3 зависят от типа получаемых данных.
    #                 # если получаем ВВОДЫ:
    #                 # val1 -> Состояние val2 -> Время, val3 -> АКТУАТОР
    #                 # если Параметры программы:
    #                 # val1 -> Значение, val2 -> Мин. val3 -> Макс
    #                 elements[name] = index, val1, val2, val3
    #
    #                 print(f'ner_line = {line}')
    #             print(f'elements = {elements}')
    #             return elements
    #
    #     if session is None:
    #         timeout = aiohttp.ClientTimeout(3)
    #         async with aiohttp.ClientSession(headers=self.headers, cookies=self.cookies, timeout=timeout) as session:
    #             return await get_request(session)
    #     else:
    #         return await get_request(session)

    # f'http://{self.ip_adress}/hvi?file=data.hvi&page=cell6710.hvi'
    # {'par_name': 'PARM.R1/1', 'par_value': '0'}
    # index, value = data_params
    # if type == self.INPUTS:
    #     params = {'par_name': f'XIN.R20/{index}', 'par_value': value}
    #     url = f'http://{self.ip_adress}{self.url_set_inp}'
    # elif type_set_request == self.type_set_request_user_parameter:
    #     url = f'http://{self.ip_adress}{self.url_set_user_parameters}'
    #     params = {'par_name': f'PARM.R1/{index}', 'par_value': value}
    # elif type_set_request == self.type_set_request_man_flash_dark_allred:
    #     params = {'par_name': f'XIN.R20/{index}', 'par_value': value}
    #     url = f'http://{self.ip_adress}{self.url_set_inp}'
    # else:
    #     raise TypeError
    #
    # print(f'params: {params}')

    # return [
    #     line.split(';')[1:] for line in data.splitlines() if line.startswith(':D')
    # ]

    # try:
    #     with requests.Session() as session:
    #         response = session.get(
    #             url=f'http://{self.ip_adress}{self.url_inputs}',
    #             headers=self.headers,
    #             cookies=self.cookies,
    #             timeout=2
    #         )
    #     inputs = (
    #         line.split(';')[1:] for line in response.content.decode("utf-8").splitlines() if line.startswith(':D')
    #     )
    #     return inputs
    # except requests.exceptions.ConnectTimeout as err:
    #     return 'ConnectTimeoutError'
    # except Exception as err:
    #     return 'common'


""" Arhive """
# class PeekWeb:
#     MAN_INPUTS = {'MPP_MAN', 'MPP_FL', 'MPP_OFF', 'MPP_PH1', 'MPP_PH2', 'MPP_PH3',
#                   'MPP_PH4', 'MPP_PH5', 'MPP_PH6', 'MPP_PH7', 'MPP_PH8'}
#     MAN_INPUTS_STAGES = {'MPP_PH1', 'MPP_PH2', 'MPP_PH3', 'MPP_PH4',
#                          'MPP_PH5', 'MPP_PH6', 'MPP_PH7', 'MPP_PH8'}
#
#     actuator_values = {
#         'ВФ': '//*[@id="button_div"]/ul/li[1]/button',
#         'ВЫКЛ': '//*[@id="button_div"]/ul/li[2]/button',
#         'ВКЛ': '//*[@id="button_div"]/ul/li[3]/button'
#     }
#
#     allowed_inputs = {'MKEY1', 'MKEY2', 'MKEY3', 'MKEY4', 'MKEY5',
#                       'MPP_MAN', 'MPP_FL', 'MPP_OFF', 'MPP_PH1', 'MPP_PH2', 'MPP_PH3', 'MPP_PH4', 'MPP_PH5',
#                       'MPP_PH6', 'MPP_PH7', 'MPP_PH8',
#                       'CP_OFF', 'CP_FLASH', 'CP_RED', 'CP_AUTO'}
#
#     button_3_entrance = '//*[@id="buttonpad"]/form[1]/ul[1]/li[3]/button'
#     button_entrance = '//*[@id="buttonpad"]/form[1]/ul[4]/li/button'
#
#     span_refresh_change = '//*[@id="refresh_button"]'
#     span_start = '//*[@id="mainnav"]/li[1]/a'
#
#     def __init__(self, ip_adress: str, num_host: str = None):
#         self.ip_adress = ip_adress
#         self.driver = None
#
#         self.short_pause = 0.5
#         self.middle_pause = 1
#         self.long_pause = 4
#         # print(f'timeout из init:')
#         # print(f'self.short_pause: {self.short_pause}')
#         # print(f'self.middle_pause: {self.middle_pause}')
#         # print(f'self.long_pause: {self.long_pause}')
#
#         # span_user_inputs = '//*[@id="mainnav"]/li[6]/ul/li[10]/ul/li[4]/a/span'   оригинал :)
#         ###########################################################################################
#
#     @staticmethod
#     def _make_inputs_and_user_parameters(inputs, user_parameters):
#         set_stageMAN = reset_stageMAN = set_reset_dark = set_reset_flash = False
#         if inputs:
#             inps_dict = {}
#             for inp, val in (i.split('=') for i in inputs):
#                 inps_dict[inp] = val
#                 set_stageMAN = True if inp == 'MPP_MAN' and val == 'ВКЛ' else False
#                 reset_stageMAN = True if inp == 'MPP_MAN' and val in ('ВЫКЛ, ВФ') else False
#                 set_reset_flash = True if inp == 'MPP_FL' else False
#                 set_reset_dark = True if inp == 'MPP_OFF' else False
#         else:
#             inps_dict = None
#         if user_parameters:
#             # user_parameters = (i.split('=') for i in user_parameters)
#             # user_parameters = {i[0]: i[1] for i in user_parameters}
#             user_parameters_dict = {inp: val for inp, val in (up.split('=') for up in user_parameters)}
#         else:
#             user_parameters_dict = None
#         return inps_dict, user_parameters_dict
#
#     def _start_and_login(self):
#         """ Метод, в котором производится нажатие в нужные элементы чтобы залогинится """
#
#         time.sleep(self.middle_pause)
#         self.driver.switch_to.parent_frame()
#         self.driver.switch_to.frame('menu_frame')
#
#         ### Пример поиска элемента
#         # content = driver.find_elements(By.TAG_NAME, "span")
#         # content = [el.text for el in content]
#         # print(content)
#
#         element = self.driver.find_element(By.TAG_NAME, 'ul')
#         element = element.find_elements(By.TAG_NAME, 'li')
#         main_page = [el.text for el in element]
#
#         if 'Рисунок перекрёстка' in main_page:
#             span_entrance = f'//*[@id="mainnav"]/li[3]/a'
#             span_user_inputs = '//*[@id="mainnav"]/li[7]/ul/li[10]/ul/li[4]/a/span'
#             span_user_parameters = '//*[@id="mainnav"]/li[6]/ul/li[3]/a/span'
#         else:
#             span_entrance = '//*[@id="mainnav"]/li[2]/a'
#             span_user_inputs = '//*[@id="mainnav"]/li[6]/ul/li[10]/ul/li[4]/a/span'
#             span_user_parameters = '//*[@id="mainnav"]/li[5]/ul/li[3]/a/span'
#         # Клик в Вход
#         element_input = self.driver.find_element(By.XPATH, span_entrance)
#         element_input.click()
#         time.sleep(self.middle_pause)
#         # Логинимся 3333
#         self.driver.switch_to.parent_frame()
#         self.driver.switch_to.frame('content_frame')
#         element_input = self.driver.find_element(By.XPATH, self.button_3_entrance)
#         for i in range(4):
#             element_input.click()
#         element_input = self.driver.find_element(By.XPATH, self.button_entrance)
#         element_input.click()
#         time.sleep(self.middle_pause)
#
#         return span_user_inputs, span_user_parameters
#
#     def _detect_span_inputs_and_user_parameterts(self):
#         time.sleep(self.middle_pause)
#         self.driver.switch_to.parent_frame()
#         self.driver.switch_to.frame('menu_frame')
#
#         element = self.driver.find_element(By.TAG_NAME, 'ul')
#         element = element.find_elements(By.TAG_NAME, 'li')
#         main_page = [el.text for el in element]
#         # print(main_page)
#         if 'Рисунок перекрёстка' in main_page:
#             span_entrance = f'//*[@id="mainnav"]/li[3]/a'
#             span_user_inputs = '//*[@id="mainnav"]/li[7]/ul/li[10]/ul/li[4]/a/span'
#             span_user_parameters = '//*[@id="mainnav"]/li[6]/ul/li[3]/a/span'
#         else:
#             span_entrance = '//*[@id="mainnav"]/li[2]/a'
#             span_user_inputs = '//*[@id="mainnav"]/li[6]/ul/li[10]/ul/li[4]/a/span'
#             span_user_parameters = '//*[@id="mainnav"]/li[5]/ul/li[3]/a/span'
#
#         return span_user_inputs, span_user_parameters
#
#     def _set_INPUTS(self, num_inp, actuator_val):
#         # Двойной клик в нужный вход в колонке АКТУАТОР:
#
#         WebDriverWait(self.driver, 10).until(
#             EC.presence_of_element_located((By.XPATH, f'//*[@id="data"]/table/tbody/tr[{num_inp}]/td[5]')))
#         element_input = self.driver.find_element(By.XPATH,
#                                                  f'//*[@id="data"]/table/tbody/tr[{num_inp}]/td[5]')
#         action = ActionChains(self.driver)
#         action.double_click(element_input)
#         action.perform()
#         time.sleep(self.short_pause)
#         # Клик в АКТУАТОР(ВКЛ/ВЫКЛ/ВФ)
#         actuator_value = self.actuator_values.get(actuator_val)
#         element_input = self.driver.find_element(By.XPATH, actuator_value)
#         element_input.click()
#         time.sleep(self.middle_pause)
#
#     def _set_USER_PARAMETERS(self, id_user_parameter, value):
#         """ Метод, в котором осуществляется клик в нужное значение нужного параметра программы(юзер-параметра)
#             В цикле for на каждой итерации осуществляется клик в парметр программы(по индексу), который
#             является ключом словаря, затем клик в значение(значение словаря)
#             :param dict filtered_user_parameters_to_set: словарь с офтильтрованнами параметрами программы.
#         """
#
#         # button_1_UP = '//*[@id="buttonpad"]/ul[1]/li[1]/button'
#         # button_2_UP = '//*[@id="buttonpad"]/ul[1]/li[2]/button'
#         # button_3_UP = '//*[@id="buttonpad"]/ul[1]/li[3]/button'
#         # button_4_UP = '//*[@id="buttonpad"]/ul[2]/li[1]/button'
#         # button_5_UP = '//*[@id="buttonpad"]/ul[2]/li[2]/button'
#         # button_6_UP = '//*[@id="buttonpad"]/ul[2]/li[3]/button'
#         # button_7_UP = '//*[@id="buttonpad"]/ul[3]/li[1]/button'
#         # button_8_UP = '//*[@id="buttonpad"]/ul[3]/li[2]/button'
#         # button_9_UP = '//*[@id="buttonpad"]/ul[3]/li[3]/button'
#         # button_0_UP = '//*[@id="buttonpad"]/ul[4]/li[1]/button'
#         # button_OK_UP = '//*[@id="buttonpad"]/ul[4]/li[4]/button'
#
#         buttons = {'1': '//*[@id="buttonpad"]/ul[1]/li[1]/button', '2': '//*[@id="buttonpad"]/ul[1]/li[2]/button',
#                    '3': '//*[@id="buttonpad"]/ul[1]/li[3]/button', '4': '//*[@id="buttonpad"]/ul[2]/li[1]/button',
#                    '5': '//*[@id="buttonpad"]/ul[2]/li[2]/button', '6': '//*[@id="buttonpad"]/ul[2]/li[3]/button',
#                    '7': '//*[@id="buttonpad"]/ul[3]/li[1]/button', '8': '//*[@id="buttonpad"]/ul[3]/li[2]/button',
#                    '9': '//*[@id="buttonpad"]/ul[3]/li[3]/button', '0': '//*[@id="buttonpad"]/ul[4]/li[1]/button',
#                    'OK': '//*[@id="buttonpad"]/ul[4]/li[4]/button'
#                    }
#
#         up_index = f'//*[@id="data"]/table/tbody/tr[{id_user_parameter}]/td[3]'
#         element_input = self.driver.find_element(By.XPATH, up_index)
#         action = ActionChains(self.driver)
#         action.double_click(element_input)
#         action.perform()
#         time.sleep(self.short_pause)
#         for number in value:
#             self.driver.find_element(By.XPATH, buttons.get(number)).click()
#             time.sleep(self.short_pause)
#         # # Клик в OK
#         element_input = self.driver.find_element(By.XPATH, buttons.get('OK'))
#         element_input.click()
#         time.sleep(self.short_pause)
#
#     def _goto_content_frame(self, span_name):
#         self.driver.switch_to.parent_frame()
#         self.driver.switch_to.frame('menu_frame')
#         # Клик во ВВОДЫ/Параметры программы(в зависимости что передано в span_name)
#         WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, span_name)))
#         element_input = self.driver.find_element(By.XPATH, span_name)
#         element_input.click()
#         time.sleep(self.middle_pause)
#         # Клик в обновить/изменить
#         self.driver.switch_to.parent_frame()
#         time.sleep(self.short_pause)
#         self.driver.switch_to.frame('inst_frame')
#         time.sleep(self.short_pause)
#         WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, self.span_refresh_change)))
#         element_input = self.driver.find_element(By.XPATH, self.span_refresh_change)
#         element_input.click()
#         time.sleep(self.middle_pause)
#         # Переход в content_frame чтобы далее устанавливать значения(для INPUTS или USER_PARAMETERS)
#         self.driver.switch_to.parent_frame()
#         self.driver.switch_to.frame('content_frame')
#         time.sleep(self.short_pause)
#
#     def _click_to_span_refresh(self):
#         # Клик в обновить/изменить
#         self.driver.switch_to.parent_frame()
#         time.sleep(self.short_pause)
#         # self.driver.switch_to.parent_frame()
#         self.driver.switch_to.frame('inst_frame')
#         time.sleep(self.short_pause)
#         WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, self.span_refresh_change)))
#         element_input = self.driver.find_element(By.XPATH, self.span_refresh_change)
#         element_input.click()
#         time.sleep(self.middle_pause)
#
#     def _make_curr_inputs_and_states(self):
#
#         table_INPUTS = self.driver.find_element(By.TAG_NAME, 'table')
#         table_INPUT_elements = table_INPUTS.find_elements(By.TAG_NAME, 'tr')
#
#         MPP_INPUTS = ('MPP_PH1', 'MPP_PH2', 'MPP_PH3', 'MPP_PH4', 'MPP_PH5', 'MPP_PH6', 'MPP_PH7',
#                       'MPP_PH8', 'MPP_FL', 'MPP_OFF')
#
#         INPS = {}
#         for num_row, row_content in enumerate([el.text.split() for el in table_INPUT_elements]):
#             if len(row_content) == 5 and num_row > 0:
#                 num, name, state, time_state, actuator_val = row_content
#                 if name in MPP_INPUTS and actuator_val == '-' and state == '1':
#                     INPS[name] = num, state, actuator_val
#                 elif name == 'MPP_MAN':
#                     MPP_MAN = (num, state, actuator_val)
#             else:
#                 continue
#         print('INPS:')
#         print(INPS)
#         return INPS
#
#     def _manage_set_inputs(self, inputs, set_man=False, reset_man=False):
#
#         table_INPUTS = self.driver.find_element(By.TAG_NAME, 'table')
#         table_INPUT_elements = table_INPUTS.find_elements(By.TAG_NAME, 'tr')
#
#         inputs_to_set = {}
#
#         print(f'set_man: {set_man}')
#         print(f'reset_man: {reset_man}')
#
#         print(inputs)
#         print('----!!!!--------')
#         for row in [el.text.split() for el in table_INPUT_elements]:
#             # if not inputs:
#             #     break
#
#             # Проверка корректности считанных данных
#             if len(row) == 5:
#                 num, name, state, time_state, actuator_val = row
#             else:
#                 continue
#
#             # Если необходимо установить фазу, добавляем в inputs_to_set
#             if name == 'MPP_MAN' and set_man:
#                 if state != '1':
#                     print(*row)
#                     inputs_to_set[name] = num, 'ВКЛ'
#                 continue
#             # Если необходимо установить фазу и у какого то ввода MPP_PHx значение 1, то его добавляем в inputs_to_set
#             if set_man and name in self.MAN_INPUTS_STAGES and name not in inputs and state == '1':
#                 inputs_to_set[name] = num, 'ВЫКЛ'
#                 continue
#
#             if name in inputs:
#                 inputs_to_set[name] = num, inputs.get(name)
#                 inputs.pop(name)
#
#         print(f'-- inputs_to_set 1 -- {inputs_to_set}')
#         if set_man and 'MPP_MAN' in inputs_to_set.keys():
#             inputs_to_set['MPP_MAN'] = inputs_to_set.pop('MPP_MAN')
#         elif reset_man:
#             tmp_inputs = {'MPP_MAN': inputs_to_set.pop('MPP_MAN')}
#             inputs_to_set = tmp_inputs | inputs_to_set
#             print(f'-- inputs_to_set -- {inputs_to_set}')
#
#         print(f'-- inputs_to_set перед for -- {inputs_to_set}')
#         for num, val in inputs_to_set.values():
#             self._set_INPUTS(num, val)
#
#         time.sleep(self.long_pause)
#
#     def session_manager(self, increase_the_timeout=False, inputs=None, user_parameters=None):
#         """ Метод создаёт web сессию, в которрй совершаются действия в зависимости от переданных аргументов:
#         :param bool increase_the_timeout: увеличивает таймаут с каждым новым вызовом метода у экземпляра
#         :param bool session_for_greenroad: если метод вызван для "Зелёной улицы" приложения Engineering_tool_kit,
#                то при наличии :arg: resetting_the_desired_values - не будет сбрасывать MPP_MAN
#         :param tuple inputs: словарь "Вводов", которые необходимо актировать. Ключ словаря - название Ввода, значение -
#                значение Актутора, которое необходимо установить
#         :param dict user_parameters: словарь "параметров программы", которые необходимо установить.
#                Ключ словаря - str, которая должна содердать ращзделитель "_". Всё, что до "_" -> произольно. После
#                "_" -> индекс параметра. Например: UP_2, UP->произвольная часть, 2->индекс параметра.
#                Значение словаря - str/int -> значение, которе будет утсановлено в поле "Значение".
#                Например: UP_2: 154 -> установить значение 154 для юзер параметра с индексом 2
#         :param dict resetting_the_desired_values: ключ - str Актуатор(ВФ, ВЫКЛ, ВКЛ), который будет установлен для
#                Вводов, текущее значение которых содержится в tuple значении словаря.
#                Например: {'ВЫКЛ: (ВКЛ, )'} - это значит ВЫКЛ будет установлено для всех Вводов, текущее сотсояние
#                которых 'ВКЛ'
#                Еще пример: {'ВФ: (ВКЛ, ВЫКЛ)'} - это значит ВФ будет установлено для всех Вводов, текущее сотсояние
#                которых 'ВКЛ' или 'ВЫКЛ'
#         :param kwargs: можно передавать Вводы или параметры программы вместо ipputs/user_parameters.
#                Например: MPP_MAN=ВКЛ, MPP_PH1=ВЫКЛ, CP_RED=ВКЛ, UP_1=154, UP_3=1 и т.д.
#         :param expected_state_for_greenroad: фаза, которую необходимо включить из Engineering_tool_kit_v1.0 "greenroad"
#         """
#
#         if inputs is None and user_parameters is None:
#             raise ValueError('inputs и user_parameters могут быть пустыми одновременно')
#         elif inputs and not isinstance(inputs, Iterable):
#             raise ValueError('inputs должен быть итерируемым объектом')
#         elif user_parameters and not isinstance(user_parameters, Iterable):
#             raise ValueError('user_parameters должен быть итерируемым объектом')
#
#         if increase_the_timeout:
#             self.short_pause += 1
#             self.middle_pause += 2
#             self.long_pause += 2
#
#         inputs, user_parameters = PeekWeb._make_inputs_and_user_parameters(inputs, user_parameters)
#
#         print(f'inputs = {inputs}, user_parameters = {user_parameters},')
#         # print(f'set_stageMAN = {set_stageMAN}, reset_stageMAN = {reset_stageMAN},')
#         # print(f'set_reset_flash = {set_reset_flash}, set_reset_dark = {set_reset_dark},')
#
#         ##############################################################
#
#         # Боевой вариант
#         options = Options()
#         # options.add_argument('--headless')
#         # options.add_argument('--disable-gpu')
#         self.driver = webdriver.Chrome(options=options)
#         self.driver.get('http://' + self.ip_adress)
#         time.sleep(self.short_pause)
#         self.driver.get('http://' + self.ip_adress + '/hvi?file=dummy.hvi&uic=3333')
#         time.sleep(self.short_pause)
#         self.driver.get('http://' + self.ip_adress)
#
#         # Тест вариант
#         # self.driver = webdriver.Chrome()
#         # self.driver.get('http://localhost/')
#         # time.sleep(self.short_pause)
#         # self.driver.get('http://localhost' + '/hvi?file=dummy.hvi&uic=3333')
#         # time.sleep(self.short_pause)
#         # self.driver.get('http://localhost/')
#         # time.sleep(self.middle_pause)
#
#         span_inputs, span_user_parameters = self._detect_span_inputs_and_user_parameterts()
#         time.sleep(self.middle_pause)
#
#         if inputs:
#             self.driver.refresh()
#             time.sleep(self.short_pause)
#             self._goto_content_frame(span_inputs)
#
#             self._manage_set_inputs(inputs)
#
#             # table_INPUTS = self.driver.find_element(By.TAG_NAME, 'table')
#             # table_INPUT_elements = table_INPUTS.find_elements(By.TAG_NAME, 'tr')
#             #
#             # print(inputs)
#             # print('----!!!!--------')
#             # cnt, len_inputs, num_MPP_MAN = 0, len(inputs), None
#             # for row in [el.text.split() for el in table_INPUT_elements]:
#             #     if len(row) == 5:
#             #         num, name, state, time_state, actuator_val = row
#             #     else:
#             #         continue
#             #     # print(f'num: {num}, name: {name},state: {state},time_state: {time_state},actuator_val: {actuator_val}')
#             #     if name not in inputs and set_stage_MAN and name in self.MAN_INPUTS:
#             #         if name == 'MPP_MAN' and state == '0':
#             #             num_MPP_MAN = num
#             #         elif state == '1' and name != 'MPP_MAN':
#             #             self._set_INPUTS(num, 'ВЫКЛ')
#             #     elif name in inputs:
#             #         val_actuator_to_set = inputs.get(name)
#             #         val_actuator_to_curr = 'ВФ' if actuator_val == '-' else actuator_val
#             #         if val_actuator_to_set != val_actuator_to_curr:
#             #             self._set_INPUTS(num, inputs.get(name))
#             #             cnt += 1
#             # if num_MPP_MAN:
#             #     self._set_INPUTS(num_MPP_MAN, 'ВКЛ')
#             # Возврат в начало, если не будем далее работать с параметрами программы
#
#         if user_parameters:
#             self.driver.refresh()
#             self._goto_content_frame(span_user_parameters)
#
#             table_UP = self.driver.find_element(By.TAG_NAME, 'table')
#             table_UP_elements = table_UP.find_elements(By.TAG_NAME, 'tr')
#
#             print([el.text for el in table_UP_elements])
#
#             # Установка UP
#             cnt, len_inputs = 1, len(inputs)
#             for row in [el.text.split() for el in table_UP_elements]:
#                 if len(row) == 5:
#                     num, name, val_cur, val_min, val_max = row
#                 else:
#                     continue
#                 if name in user_parameters:
#                     val_up_to_set = user_parameters.get(name)
#                     if val_up_to_set != val_cur:
#                         self._set_USER_PARAMETERS(num, val_up_to_set)
#                     cnt += 1
#                 if cnt >= len_inputs:
#                     print(f'if cnt >= len_inputs:')
#                     break
#         self.driver.refresh()
#         time.sleep(self.middle_pause)
#         self.driver.close()
#
#     def set_stage(self, value, increase_the_timeout=False):
#         if increase_the_timeout:
#             self.short_pause += 1
#             self.middle_pause += 2
#             self.long_pause += 2
#
#         ##############################################################
#
#         # Боевой вариант
#         options = Options()
#         options.add_argument('--headless')
#         options.add_argument('--disable-gpu')
#         options.add_argument('--no-sandbox')
#         options.add_argument('--disable-dev-shm-usage')
#
#         self.driver = webdriver.Chrome(options=options)
#         self.driver.get('http://' + self.ip_adress)
#         time.sleep(self.short_pause)
#         self.driver.get('http://' + self.ip_adress + '/hvi?file=dummy.hvi&uic=3333')
#         time.sleep(self.short_pause)
#         self.driver.get('http://' + self.ip_adress)
#
#         # Тест вариант
#         # self.driver = webdriver.Chrome()
#         # self.driver.get('http://localhost/')
#         # time.sleep(self.short_pause)
#         # self.driver.get('http://localhost' + '/hvi?file=dummy.hvi&uic=3333')
#         # time.sleep(self.short_pause)
#         # self.driver.get('http://localhost/')
#         # time.sleep(self.middle_pause)
#
#         time.sleep(self.middle_pause)
#
#         span_inputs, _ = self._detect_span_inputs_and_user_parameterts()
#         time.sleep(self.middle_pause)
#
#         self.driver.refresh()
#         time.sleep(self.short_pause)
#         self._goto_content_frame(span_inputs)
#
#         if value.isdigit() and int(value) in range(1, 9):
#             inputs = {'MPP_MAN': 'ВКЛ', f'MPP_PH{value}': 'ВКЛ'}
#             set_man, reset_man = True, False
#         elif value.lower() in ('0', 'false', 'reset', 'local', 'сброс', 'локал'):
#             inputs = {'MPP_MAN' if i == 0 else f'MPP_PH{i}': 'ВЫКЛ' if i == 0 else 'ВФ' for i in range(9)}
#             set_man, reset_man = False, True
#         else:
#             return
#
#         self._manage_set_inputs(inputs, set_man, reset_man)
#
#     def set_flash(self, value, increase_the_timeout=False):
#         if increase_the_timeout:
#             self.short_pause += 1
#             self.middle_pause += 2
#             self.long_pause += 2
#
#         ##############################################################
#
#         # Боевой вариант
#         options = Options()
#         # options.add_argument('--headless')
#         # options.add_argument('--disable-gpu')
#         self.driver = webdriver.Chrome(options=options)
#         self.driver.get('http://' + self.ip_adress)
#         time.sleep(self.short_pause)
#         self.driver.get('http://' + self.ip_adress + '/hvi?file=dummy.hvi&uic=3333')
#         time.sleep(self.short_pause)
#         self.driver.get('http://' + self.ip_adress)
#
#         # Тест вариант
#         # self.driver = webdriver.Chrome()
#         # self.driver.get('http://localhost/')
#         # time.sleep(self.short_pause)
#         # self.driver.get('http://localhost' + '/hvi?file=dummy.hvi&uic=3333')
#         # time.sleep(self.short_pause)
#         # self.driver.get('http://localhost/')
#         # time.sleep(self.middle_pause)
#
#         time.sleep(self.middle_pause)
#
#         span_inputs, _ = self._detect_span_inputs_and_user_parameterts()
#         time.sleep(self.middle_pause)
#
#         self.driver.refresh()
#         time.sleep(self.short_pause)
#         self._goto_content_frame(span_inputs)
#
#         if value.lower() in ('1', 'true', 'set', 'on', 'установить'):
#             inputs = {'MPP_FL': 'ВКЛ'}
#         elif value.lower() in ('0', 'false', 'reset', 'off', 'сброс'):
#             inputs = {'MPP_FL': 'ВЫКЛ'}
#         else:
#             return
#
#         self._manage_set_inputs(inputs, )
