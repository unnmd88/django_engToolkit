import asyncio
import inspect
from enum import Enum
from toolkit.sdp_lib import controller_management


class AvailableControllers(Enum):
    """ Доступные типы контроллера """
    SWARCO = 'SWARCO'
    POTOK_P = 'ПОТОК (P)'
    POTOK_S = 'ПОТОК (S)'
    PEEK = 'PEEK'


class GetDataFromController:
    def __init__(self, request):
        self.request = request
        self.data_request = request.GET.dict()

    def create_objects_methods(self):
        objects_methods = []

        for num_host, data_request in self.data_request.items():
            data_request = data_request.split(';')
            if len(data_request) != 3:
                continue
            ip_adress, controller_type, scn = data_request
            controller_type_request = self.get_type_object_get_request(controller_type.upper())
            obj = controller_management.Controller(ip_adress, controller_type_request, scn, num_host)
            if obj is None:
                continue
            objects_methods.append(obj.get_current_mode)
        return objects_methods

    def get_data_from_controllers(self, objects_methods):

        get_data_manager = controller_management.GetDataControllerManagement()

        raw_data_from_controllers = asyncio.run(get_data_manager.main(objects_methods, option='get'))
        processed_data = get_data_manager.data_processing(raw_data_from_controllers)
        return processed_data

    def get_type_object_get_request(self, controller_type: str):

        if controller_type == AvailableControllers.POTOK_P.value:
            return controller_management.AvailableProtocolsManagement.POTOK_UG405.value
        elif controller_type == AvailableControllers.POTOK_S.value:
            return controller_management.AvailableProtocolsManagement.POTOK_STCIP.value
        elif controller_type == AvailableControllers.SWARCO.value:
            return controller_management.AvailableProtocolsManagement.SWARCO_STCIP.value
        elif controller_type == AvailableControllers.PEEK.value:
            return controller_management.AvailableProtocolsManagement.PEEK_UG405.value


class SetRequestToController:
    def __init__(self, request):
        self.request = request
        self.data_request = request.POST.dict()

    def set_command_request(self):

        set_stage = ('ФАЗА MAN', 'ФАЗА SNMP')
        set_flash = ('ЖМ MAN', 'ЖМ SNMP')
        set_dark = ('ОС MAN', 'ОС SNMP')

        result = None

        for num_host, data_request in self.data_request.items():
            data_request = data_request.split(';')
            if len(data_request) != 5:
                continue
            ip_adress, type_of_controller, scn, command, value = data_request
            command, type_of_controller = command.upper(), type_of_controller.upper()
            type_of_controller_management = self.get_type_object_set_request(type_of_controller, command)
            host = controller_management.Controller(ip_adress, type_of_controller_management, scn)
            print(f'host -> {host}')

            if command in set_stage:
                if inspect.iscoroutinefunction(host.set_stage):
                    result = asyncio.run(host.set_stage(value))
                else:
                    result = host.set_stage(value)
                print('command in set_stage')
            elif command in set_flash:
                if inspect.iscoroutinefunction(host.set_flash):
                    result = asyncio.run(host.set_flash(value))
                else:
                    result = host.set_flash(value)
                print('command in host.set_flash(value)')
            elif command in set_dark:
                if inspect.iscoroutinefunction(host.set_dark):
                    result = asyncio.run(host.set_dark(value))
                else:
                    result = host.set_dark(value)
                print('command in host.set_dark(value)')
            elif command == 'ВВОДЫ':
                result = host.session_manager(inputs=(inp for inp in value.split(',')))

        return result

    def get_type_object_set_request(self, controller_type, command):

        SNMP = 'SNMP'
        MAN = 'MAN'
        INPUTS = 'ВВОДЫ'

        command = command.upper()

        if controller_type == AvailableControllers.POTOK_P.value:
            if SNMP in command:
                return controller_management.AvailableProtocolsManagement.POTOK_UG405.value
        elif controller_type == AvailableControllers.POTOK_S.value:
            if SNMP in command:
                return controller_management.AvailableProtocolsManagement.POTOK_STCIP.value
        elif controller_type == AvailableControllers.SWARCO.value:
            if SNMP in command:
                return controller_management.AvailableProtocolsManagement.SWARCO_STCIP.value
            elif MAN in command:
                return controller_management.AvailableProtocolsManagement.SWARCO_SSH.value
        elif controller_type == AvailableControllers.PEEK.value:
            if SNMP in command:
                return controller_management.AvailableProtocolsManagement.PEEK_UG405.value
            elif MAN in command or INPUTS in command:
                return controller_management.AvailableProtocolsManagement.PEEK_WEB.value