import asyncio
import inspect
import json
from enum import Enum

from toolkit.sdp_lib import controller_management
import logging

logger = logging.getLogger(__name__)


# class Controller:
#
#     def __new__(cls, ip_adress, type_object, scn: str = None, host_id: str = None):
#         logger.debug('ya в new, type_object = %s', type_object)
#         scn = scn if scn else None
#         if type_object == AvailableProtocolsManagement.POTOK_STCIP.value:
#             return controller_management.PotokS(ip_adress, host_id)
#         elif type_object == AvailableProtocolsManagement.POTOK_UG405.value:
#             return controller_management.PotokP(ip_adress, host_id=host_id, scn=scn)
#         elif type_object == AvailableProtocolsManagement.SWARCO_STCIP.value:
#             return controller_management.SwarcoSTCIP(ip_adress, host_id)
#         elif type_object == AvailableProtocolsManagement.SWARCO_SSH.value:
#             return controller_management.SwarcoSSH(ip_adress, host_id)
#         elif type_object == AvailableProtocolsManagement.PEEK_UG405.value:
#             return controller_management.PeekUG405(ip_adress, scn, host_id)
#         elif type_object == AvailableProtocolsManagement.PEEK_WEB.value:
#             return controller_management.PeekWeb(ip_adress, host_id)

def create_obj(ip_adress: str, type_object: str, scn: str = None, host_id: str = None):
    logger.debug('ya в create_obj, type_object = %s', type_object)
    scn = scn if scn else None
    if type_object == AvailableProtocolsManagement.POTOK_STCIP.value:
        return controller_management.PotokS(ip_adress, host_id)
    elif type_object == AvailableProtocolsManagement.POTOK_UG405.value:
        return controller_management.PotokP(ip_adress, host_id=host_id, scn=scn)
    elif type_object == AvailableProtocolsManagement.SWARCO_STCIP.value:
        return controller_management.SwarcoSTCIP(ip_adress, host_id)
    elif type_object == AvailableProtocolsManagement.SWARCO_SSH.value:
        return controller_management.SwarcoSSH(ip_adress, host_id)
    elif type_object == AvailableProtocolsManagement.PEEK_UG405.value:
        return controller_management.PeekUG405(ip_adress, scn, host_id)
    elif type_object == AvailableProtocolsManagement.PEEK_WEB.value:
        return controller_management.PeekWeb(ip_adress, host_id)


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
    def __init__(self, data):
        self.data_request = data
        self.processed_data = {}

    # async def get_data_from_controllers(self, objects_methods):
    #     logger.debug(objects_methods)
    #
    #     result = await asyncio.gather(*objects_methods)
    #
    #     print(result)
    #     logger.debug(f'result-->>> {result}')
    #     return result

    async def main(self):
        objects_methods, error_hosts = [], []

        logger.debug(self.data_request)
        # print(self.data_request.items())
        for ip_adress, data in self.data_request.items():
            if not isinstance(data, dict):
                continue
            host_id = data.get('host_id')
            controller_type = data.get('type_controller')
            scn = data.get('scn')
            controller_type_request = self.get_type_object(controller_type.upper())

            obj = create_obj(ip_adress, controller_type_request, scn, host_id)

            if obj is None:
                error_hosts.append({ip_adress: {
                    'host_id': host_id,
                    'type_controller': controller_type,
                    'scn': scn
                }
                })
                continue

            objects_methods.append(asyncio.create_task(obj.get_request(get_mode=True)))
        result_request = await asyncio.gather(*objects_methods)
        logger.debug(f'result-->>> {result_request}')

        return error_hosts, result_request

    def get_type_object(self, controller_type: str):

        if controller_type == AvailableControllers.POTOK_P.value:
            return AvailableProtocolsManagement.POTOK_UG405.value
        elif controller_type == AvailableControllers.POTOK_S.value:
            return AvailableProtocolsManagement.POTOK_STCIP.value
        elif controller_type == AvailableControllers.SWARCO.value:
            return AvailableProtocolsManagement.SWARCO_STCIP.value
        elif controller_type == AvailableControllers.PEEK.value:
            return AvailableProtocolsManagement.PEEK_WEB.value


class SetRequestToController:

    def __init__(self, request):
        self.request = request
        # self.data_request = json.loads(request.body.decode("utf-8")).get('data')
        # print(f'self.data_request: {self.data_request}')
        # print(f'self.request: {self.request}')
        self.data_request = request.data.get('data')

        logger.debug(f'request.data = self.data_request: {self.data_request}')
        # self.data_request = request.POST.dict()
        logger.debug(self.request.data.get('data'))

    async def main(self):

        objects_methods, error_hosts = [], []

        set_stage = ('ФАЗА MAN', 'ФАЗА SNMP')
        set_flash = ('ЖМ MAN', 'ЖМ SNMP')
        set_dark = ('ОС MAN', 'ОС SNMP')
        set_user_params_peek_web = 'ПАРАМЕТРЫ ПРОГРАММЫ'

        logger.debug(f'перед {self.request.data.get("data")}')
        for ip_adress, data in self.data_request.items():
            if not isinstance(data, dict):
                continue
            host_id = data.get('host_id')
            type_of_controller = data.get('type_controller')
            command = data.get('type_command')
            value = data.get('set_val')
            scn = data.get('scn')

            command, type_of_controller = command.upper(), type_of_controller.upper()
            type_of_controller_management = self.get_type_object_set_request(type_of_controller, command)
            obj = create_obj(ip_adress, type_of_controller_management, scn, host_id)
            if obj is None:
                error_hosts.append({ip_adress: {
                    'host_id': host_id,
                    'type_controller': type_of_controller,
                    'scn': scn
                }
                })
                continue

            if command in set_stage:
                if inspect.iscoroutinefunction(obj.set_stage):
                    objects_methods.append(asyncio.create_task(obj.set_stage(value)))
                else:
                    result_req = obj.set_stage(value)

            elif command in set_flash:
                if inspect.iscoroutinefunction(obj.set_flash):
                    result_req = asyncio.run(obj.set_flash(value))
                else:
                    result_req = obj.set_flash(value)

            elif command in set_dark:
                if inspect.iscoroutinefunction(obj.set_dark):
                    result_req = asyncio.run(obj.set_dark(value))
                else:
                    result_req = obj.set_dark(value)
            elif command == 'ВВОДЫ':
                result_req = obj.session_manager(inputs=(inp for inp in value.split(',')))
            elif command == set_user_params_peek_web:
                result_req = asyncio.run(obj.set_user_parameters(params=value))

        result_req = await asyncio.gather(*objects_methods)
        logger.debug(f'result-->>> {result_req}')
        #
        # logger.debug(f'log1 {result_req}')
        #
        # # if result_req is None:
        # #     result_req = True, {
        # #         ip_adress: {
        # #             'request_errors': 'Некорректные данные для отправки команды',
        # #             'host_id': host_id,
        # #             'type_controller': data.get('type_controller'),
        # #             'scn': scn,
        # #             'command': data.get('type_command'),
        # #         }
        # #     }
        # logger.debug(f'log2 {result_req}')
        return error_hosts, result_req

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
