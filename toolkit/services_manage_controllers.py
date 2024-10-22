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
        result_req = await asyncio.gather(*objects_methods)
        logger.debug(f'result-->>> {result_req}')

        return error_hosts, result_req

    def get_type_object(self, controller_type: str):

        if controller_type == AvailableControllers.POTOK_P.value:
            return AvailableProtocolsManagement.POTOK_UG405.value
        elif controller_type == AvailableControllers.POTOK_S.value:
            return AvailableProtocolsManagement.POTOK_STCIP.value
        elif controller_type == AvailableControllers.SWARCO.value:
            return AvailableProtocolsManagement.SWARCO_STCIP.value
        elif controller_type == AvailableControllers.PEEK.value:
            return AvailableProtocolsManagement.PEEK_WEB.value