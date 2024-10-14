import asyncio
import inspect
import json
from enum import Enum

from toolkit.sdp_lib import controller_management
import logging

logger = logging.getLogger(__name__)


def test_for_logger():
    logger.debug('deeeee')


class Controller:

    def __new__(cls, ip_adress, type_object, scn: str = None, num_host: str = None):
        logger.debug('ya в new, type_object = %s', type_object)
        scn = scn if scn else None
        if type_object == AvailableProtocolsManagement.POTOK_STCIP.value:
            return controller_management.PotokS(ip_adress, num_host)
        elif type_object == AvailableProtocolsManagement.POTOK_UG405.value:
            return controller_management.PotokP(ip_adress, num_host=num_host, scn=scn)
        elif type_object == AvailableProtocolsManagement.SWARCO_STCIP.value:
            return controller_management.SwarcoSTCIP(ip_adress, num_host)
        elif type_object == AvailableProtocolsManagement.SWARCO_SSH.value:
            return controller_management.SwarcoSSH(ip_adress, num_host)
        elif type_object == AvailableProtocolsManagement.PEEK_UG405.value:
            return controller_management.PeekUG405(ip_adress, scn, num_host)
        elif type_object == AvailableProtocolsManagement.PEEK_WEB.value:
            return controller_management.PeekWeb(ip_adress, num_host)


class AvailableProtocolsManagement(Enum):
    """ Протоколы управления """
    POTOK_UG405 = 'POTOK_UG405'
    POTOK_STCIP = 'POTOK_STCIP'
    SWARCO_STCIP = 'SWARCO_STCIP'
    SWARCO_SSH = 'SWARCO_SSH'
    PEEK_UG405 = 'PEEK_UG405'
    PEEK_WEB = 'PEEK_WEB'


class AvailableControllers(Enum):
    """ Доступные типы контроллера """
    SWARCO = 'SWARCO'
    POTOK_P = 'ПОТОК (P)'
    POTOK_S = 'ПОТОК (S)'
    PEEK = 'PEEK'


class GetDataFromController:
    def __init__(self, request):
        self.request = request
        self.data_request = request.data.get('data', {})
        self.processed_data = {}

    def create_objects_methods(self):
        objects_methods = []

        logger.debug(self.request.data.get('data'))
        # print(self.data_request.items())
        for ip_adress, data in self.request.data.get('data').items():
            if not isinstance(data, dict):
                continue
            # print(f'ip_adress---- {ip_adress}')
            # print(f'data---- {data}')
            # print(data.get('num_host'))
            # print(data.get('type_controller'))
            # print(data.get('scn'))
            num_host = data.get('num_host')
            controller_type = data.get('type_controller')
            scn = data.get('scn')
            controller_type_request = self.get_type_object_get_request(controller_type.upper())
            obj = Controller(ip_adress, controller_type_request, scn, num_host)
            if obj is None:
                self.processed_data[num_host] = 'Сбой отправки запроса. Проверьте корректность данных'
                continue
            objects_methods.append(obj.get_current_mode)
        return objects_methods

    def get_data_from_controllers(self, objects_methods):

        get_data_manager = controller_management.GetDataControllerManagement()

        raw_data_from_controllers = asyncio.run(get_data_manager.collect_data_from_hosts(objects_methods, option='get'))
        processed_data = get_data_manager.data_processing(raw_data_from_controllers)
        return self.processed_data | processed_data

    def get_type_object_get_request(self, controller_type: str):

        if controller_type == AvailableControllers.POTOK_P.value:
            return AvailableProtocolsManagement.POTOK_UG405.value
        elif controller_type == AvailableControllers.POTOK_S.value:
            return AvailableProtocolsManagement.POTOK_STCIP.value
        elif controller_type == AvailableControllers.SWARCO.value:
            return AvailableProtocolsManagement.SWARCO_STCIP.value
        elif controller_type == AvailableControllers.PEEK.value:
            return AvailableProtocolsManagement.PEEK_UG405.value


class SetRequestToController:

    def __init__(self, request):
        self.request = request
        # self.data_request = json.loads(request.body.decode("utf-8")).get('data')
        # print(f'self.data_request: {self.data_request}')
        # print(f'self.request: {self.request}')
        self.data_request = request.data.get('data')

        print(f'request.data = self.data_request: {self.data_request}')
        # self.data_request = request.POST.dict()
        logger.debug(self.request.data.get('data'))

    def set_command_request(self):

        set_stage = ('ФАЗА MAN', 'ФАЗА SNMP')
        set_flash = ('ЖМ MAN', 'ЖМ SNMP')
        set_dark = ('ОС MAN', 'ОС SNMP')
        set_user_params_peek_web = 'ПАРАМЕТРЫ ПРОГРАММЫ'

        result = msg = num_host = None

        for num_host, data_request in self.data_request.items():
            data_request = data_request.split(';')
            if len(data_request) != 5:
                continue
            ip_adress, type_of_controller, scn, command, value = data_request
            command, type_of_controller = command.upper(), type_of_controller.upper()
            type_of_controller_management = self.get_type_object_set_request(type_of_controller, command)
            host = Controller(ip_adress, type_of_controller_management, scn)
            print(f'host -> {host}')

            if command in set_stage:
                if inspect.iscoroutinefunction(host.set_stage):
                    isError = asyncio.run(host.set_stage(value))
                    result, msg = self.get_result_command(isError, host)
                else:
                    result = host.set_stage(value)
                print('command in set_stage')
            elif command in set_flash:
                if inspect.iscoroutinefunction(host.set_flash):
                    print('elif command in set_flash:')
                    isError = asyncio.run(host.set_flash(value))
                    result, msg = self.get_result_command(isError, host)
                else:
                    result = host.set_flash(value)
                print('command in host.set_flash(value)')
            elif command in set_dark:
                print('elif command in set_dark:')
                if inspect.iscoroutinefunction(host.set_dark):
                    isError = asyncio.run(host.set_dark(value))
                    result, msg = self.get_result_command(isError, host)
                else:
                    result = host.set_dark(value)
                print('command in host.set_dark(value)')
            elif command == 'ВВОДЫ':
                result = host.session_manager(inputs=(inp for inp in value.split(',')))
            elif command == set_user_params_peek_web:
                isError = asyncio.run(host.set_user_parameters(params=value))
                result, msg = self.get_result_command(isError, host)

        return num_host, result, msg

    def get_type_object_set_request(self, controller_type, command):

        SNMP = 'SNMP'
        MAN = 'MAN'
        INPUTS = 'ВВОДЫ'
        USER_PARAMETERS = 'ПАРАМЕТРЫ ПРОГРАММЫ'

        command = command.upper()

        if controller_type == AvailableControllers.POTOK_P.value:
            if SNMP in command:
                return AvailableProtocolsManagement.POTOK_UG405.value
        elif controller_type == AvailableControllers.POTOK_S.value:
            if SNMP in command:
                return AvailableProtocolsManagement.POTOK_STCIP.value
        elif controller_type == AvailableControllers.SWARCO.value:
            if SNMP in command:
                return AvailableProtocolsManagement.SWARCO_STCIP.value
            elif MAN in command:
                return AvailableProtocolsManagement.SWARCO_SSH.value
        elif controller_type == AvailableControllers.PEEK.value:
            if SNMP in command:
                return AvailableProtocolsManagement.PEEK_UG405.value
            elif MAN in command or INPUTS in command:
                return AvailableProtocolsManagement.PEEK_WEB.value
            elif command == USER_PARAMETERS:
                return AvailableProtocolsManagement.PEEK_WEB.value

    def get_result_command(self, res, host):

        print(f'get_result_command res: {res}')

        messages = {
            'type_controller_error': 'Ошибка: проверьте корректность типа контроллера',
            'success': 'Команда успешно отправлена',
            'No SNMP response received before timeout': 'Ошибка отправки команды: хост недоступен',
            'ConnectTimeoutError': 'Ошибка отправки команды: хост недоступен',
            'common': 'Ошибка отправки команды',
            'Invalid value': 'Ошибка отправки команды: недопустимое значение',
            'Not params to set': 'Проверьте корректность название/значение устанавливаемого параметра',
            'No Such Object currently exists at this OID': 'Ошибка отправки команды: неверный тип дк по указаглму ip'
        }

        if isinstance(host, controller_management.SwarcoSSH):
            if res is None:
                result, msg = False, messages.get('common')
            else:
                result, msg = True, res
        elif isinstance(host, (controller_management.PotokS, controller_management.PotokP,
                               controller_management.SwarcoSTCIP, controller_management.PeekUG405)):
            if res is None or not res:
                result, msg = True, messages.get('success')
            else:
                result, msg = False, messages.get(res.__str__(), messages.get('common'))

        elif isinstance(host, controller_management.PeekWeb):
            if res is None or not res:
                result, msg = True, messages.get('success')
            else:
                result, msg = False, messages.get(res, messages.get('common'))
        else:
            result = msg = None

        return result, msg
