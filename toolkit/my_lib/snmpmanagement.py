import os
import socket


from pysnmp.hlapi.asyncio import *
from pysnmp.proto.rfc1902 import OctetString

from configuration import auth

snmp_get = 'snmpget.exe'
snmp_set = 'snmpset.exe'

try:
    community_swarco, community_peek = auth('snmp')
except:
    community_swarco, community_peek = 'pass', 'pass'
    pass

# print('snmpmanagement is called')

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

        get_val_stage_UG405_POTOK = {k: v for v, k in enumerate(stages, 1)}
        return get_val_stage_UG405_POTOK
        # print(get_val_stage_UG405_POTOK)
    elif option == 'set':
        mask_after_8stages_set = ['01', '02', '04', '08', '10', '20', '40', '80']
        stages = ['01', '02', '04', '08', '10', '20', '40', '80']
        for i in range(7):
            temp_lst = [
                f'{el}{"00" * (i + 1)}' for el in mask_after_8stages_set
            ]
            stages = stages + temp_lst
        set_val_stage_UG405_POTOK = {str(k): v for k, v in enumerate(stages, 1)}
        # print(set_val_stage_UG405_POTOK)
        return set_val_stage_UG405_POTOK

"""**************************************************************************
***                          Configuration Peek                          ****   
*****************************************************************************
"""
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
# print(set_stage_UG405_peek_values)
# set_stage_UG405_peek_values = {'1': '01', '2': '02', '3': '04', '4': '08',
#                                '5': '10', '6': '20', '7': '40', '8': '80',
#                                '9': '0001', '10': '0002', '11': '0004', '12': '0008',
#                                '13': '0010', '14': '0020', '15': '0040', '16': '0080'}
# Ключи oid UG405 Peek
peek_utcType2OperationModeTimeout = 'utcType2OperationModeTimeout'
peek_utcType2OperationMode = 'utcType2OperationMode'
peek_utcControlLO = 'utcControlLO'
peek_utcControlFF = 'utcControlFF'
peek_utcControlTO = 'utcControlTO'
peek_utcControlFn = 'utcControlFn'
peek_utcReplyGn = 'utcReplyGn'
# oid для UG405 Peek
oids_UG405_PEEK = {peek_utcReplyGn: '.1.3.6.1.4.1.13267.3.2.5.1.1.3',
                   peek_utcControlLO: '.1.3.6.1.4.1.13267.3.2.4.2.1.11',
                   peek_utcControlFF: '.1.3.6.1.4.1.13267.3.2.4.2.1.20',
                   peek_utcControlTO: '.1.3.6.1.4.1.13267.3.2.4.2.1.15',
                   peek_utcControlFn: '.1.3.6.1.4.1.13267.3.2.4.2.1.5',
                   peek_utcType2OperationModeTimeout: '.1.3.6.1.4.1.13267.3.2.2.4.0',
                   peek_utcType2OperationMode: '.1.3.6.1.4.1.13267.3.2.4.1.0'
                   }


"""*********************************************************************************
***                          Configuration Potok UG405                          ****   
************************************************************************************
"""

# Ключи значения фаз для get запросов UG405 Potok
# get_val_stage_UG405_POTOK = {
#     '01': 1, '02': 2, '04': 3, '08': 4,
#     '10': 5, '6': 6, '@': 7, '80': 8,
#     '0100': 9, '0200': 10, '0400': 11, '0800': 12,
#     '1000': 13, '2000': 14, '4000@': 15, '8000': 16,
#     '010000': 17, '020000': 18, '040000': 19, '080000': 20,
#     '100000': 21, '200000': 22, '400000@': 23, '800000': 24,
#     '01000000': 25, '02000000': 26, '04000000@': 27, '08000000': 28,
#     '10000000': 29, '20000000': 30, '40000000@': 31, '80000000': 32,
#     '0100000000': 33, '0200000000': 34, '0400000000@': 35, '0800000000': 36,
#     '1000000000': 37, '2000000000': 38, '4000000000@': 39, '8000000000': 40,
#     '010000000000': 41, '020000000000': 42, '040000000000@': 43, '080000000000': 44,
#     '100000000000': 45, '200000000000': 46, '400000000000@': 47, '800000000000': 48,
#     '01000000000000': 49, '02000000000000': 50, '04000000000000@': 51, '08000000000000': 52,
#     '10000000000000': 53, '20000000000000': 54, '40000000000000@': 55, '80000000000000': 56,
#     '0100000000000000': 57, '0200000000000000': 58, '0400000000000000@': 59, '0800000000000000': 60,
#     '1000000000000000': 61, '2000000000000000': 62, '4000000000000000@': 63, '8000000000000000': 64
#
# }
get_val_stage_UG405_POTOK = val_stages_for_get_stage_UG405_potok(option='get')
# Ключи значения фаз для set запросов UG405 Potok
set_stage_UG405_potok_values = val_stages_for_get_stage_UG405_potok(option='set')
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
set_reset_dark_potok_UG405 = 'Включить/Выключить ОС'
set_reset_yellow_flash_potok_UG405 = 'Включить/Выключить ЖМ'
set_stage_potok_UG405 = 'Установка фазы'
allow_bit_potok_UG405 = 'Разрешающий бит(TO)'
operaion_mode_potok_UG405 = 'Получение режимов работы ДК(OperationMode)'
operaion_mode_timeout_potok_UG405 = 'Таймаут на ожидание команды(OperationModeTimeout)'
get_current_stage_potok_UG405 = 'Получение фазы'
get_current_plan_potok_UG405 = 'Возвращает номер плана'
get_dark_potok_UG405 = 'Получение состояния ОС'
get_yellow_flash_potok_UG405 = 'Получение состояния ЖМ'
set_restart_programm_potok_UG405 = 'Перезапуск программы'

# oid для UG405 Potok
oids_UG405_POTOK = {get_current_stage_potok_UG405: '.1.3.6.1.4.1.13267.3.2.5.1.1.3',
                    get_current_plan_potok_UG405: '.1.3.6.1.4.1.13267.1.2.9.1.3',
                    get_dark_potok_UG405: '.1.3.6.1.4.1.13267.3.2.5.1.1.45',
                    get_yellow_flash_potok_UG405: '.1.3.6.1.4.1.13267.3.2.5.1.1.36',
                    allow_bit_potok_UG405: '.1.3.6.1.4.1.13267.3.2.4.2.1.15',
                    set_reset_dark_potok_UG405: '.1.3.6.1.4.1.13267.3.2.4.2.1.11',
                    set_reset_yellow_flash_potok_UG405: '.1.3.6.1.4.1.13267.3.2.4.2.1.20',
                    set_stage_potok_UG405: '.1.3.6.1.4.1.13267.3.2.4.2.1.5',
                    operaion_mode_potok_UG405: '.1.3.6.1.4.1.13267.3.2.4.1.0',
                    operaion_mode_timeout_potok_UG405: '.1.3.6.1.4.1.13267.3.2.2.4.0',
                    set_restart_programm_potok_UG405: '.1.3.6.1.4.1.13267.3.2.4.2.1.5.5'}


"""*********************************************************************************
***                          Configuration Potok STCIP                          ****   
************************************************************************************
"""
# Ключи значения фаз для get запросов STCIP Potok
# get_val_stage_STCIP_potok = {'2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '9': 8,
# get_val_stage_STCIP_potok = {str(k): str(v) for k, v in zip(range(2, 66), range(1, 65))}
# Словарь вида: {'2': '1', '3': '2', '4': '3'...'65': '64'}
get_val_stage_STCIP_potok = {
    str(k): str(v) for k, v in zip(range(2, 66), range(1, 65))
}
#                              '10': 9, '11': 10, '12': 11, '13': 12, '14': 13, '15': 14, '16': 15, '17': 16}

# Ключи значения фаз для set запросов STCIP Potok
# set_stage_STCIP_potok_values = {'1': '2', '2': '3', '3': '4', '4': '5', '5': '6',
#                                 '6': '7', '7': '8', '8': '9', '9': '10', '10': '11',
#                                 '11': '12', '12': '13', '13': '14', '14': '15',
#                                 '15': '16', '16': '17', 'ЛОКАЛ': '0'}
# Словарь вида: {'1': '2', '2': '3', '3': '4'....'ЛОКАЛ: '0'}
set_stage_STCIP_potok_values = {
    str(k) if k < 65 else 'ЛОКАЛ': str(v) if k < 65 else '0' for k, v in zip(range(1, 68), range(2, 69))
}
# Ключи oid STCIP Potok
dark_potok_STCIP = 'Установить и получить состояние ОС'
yellow_flash_potok_STCIP = 'Установить и получить состояние ЖМ'
all_red_potok_STCIP = 'Установить и получить режим КК'
set_stage_potok_STCIP = 'Установить и получить фазу'
get_mode_stip_potok = 'Возвращает статусы работы ДК(КУ, РУ и др.)'
get_status_stip_potok = 'Возвращает статусы работы ДК(Нормальная, ОС, ЖМ, КК)'
get_current_stage_potok_STCIP = 'Получить текущую фазу'
get_current_plan_potok_STCIP = 'Возвращает текущий план'
set_restart_programm_potok_STCIP = 'Перезапуск программы'
# oid для STCIP Potok
oids_STCIP_POTOK = {get_current_stage_potok_STCIP: '1.3.6.1.4.1.1618.3.7.2.11.2.0',
                    get_current_plan_potok_STCIP: '1.3.6.1.4.1.1618.3.7.2.1.2.0',
                    dark_potok_STCIP: '1.3.6.1.4.1.1618.3.2.2.2.1.0',
                    yellow_flash_potok_STCIP: '1.3.6.1.4.1.1618.3.2.2.1.1.0',
                    set_stage_potok_STCIP: '1.3.6.1.4.1.1618.3.7.2.11.1.0',
                    get_mode_stip_potok: '1.3.6.1.4.1.1618.3.6.2.2.2.0',
                    get_status_stip_potok: '1.3.6.1.4.1.1618.3.6.2.1.2.0',
                    all_red_potok_STCIP: '1.3.6.1.4.1.1618.3.2.2.4.1.0',
                    set_restart_programm_potok_STCIP: '.1.3.6.1.4.1.1618.3.2.2.3.1.0'}


"""**********************************************************************************
***                          Configuration Swarco STCIP                          ****   
*************************************************************************************
"""
# Ключи значения фаз для get запросов STCIP Swarco
get_val_stage_STCIP_swarco = {'2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6, '8': 7, '1': 8}
# Ключи значения фаз для set запросов STCIP Swarco
set_stage_STCIP_swarco_values = {'1': '2', '2': '3', '3': '4', '4': '5',
                                 '5': '6', '6': '7', '7': '8', '8': '1',
                                 'ЛОКАЛ': '0'}
# Ключи oid STCIP Swarco
swarco_swarcoUTCTrafftechPhaseCommand = 'swarcoUTCTrafftechPhaseCommand'
swarco_swarcoUTCCommandDark = 'swarcoUTCCommandDark'
swarco_swarcoUTCCommandFlash = 'swarcoUTCCommandFlash'
swarco_swarcoUTCTrafftechPlanCommand = 'swarcoUTCTrafftechPlanCommand'
swarco_swarcoUTCStatusEquipment = 'swarcoUTCStatusEquipment'
swarco_swarcoUTCTrafftechPhaseStatus = 'swarcoUTCTrafftechPhaseStatus'
swarco_swarcoUTCTrafftechPlanCurrent = 'swarcoUTCTrafftechPlanCurrent'
# oid для STCIP Swarco
oids_STCIP_SWARCO = {swarco_swarcoUTCTrafftechPhaseStatus: '1.3.6.1.4.1.1618.3.7.2.11.2.0',
                     swarco_swarcoUTCTrafftechPlanCurrent: '1.3.6.1.4.1.1618.3.7.2.1.2.0',
                     swarco_swarcoUTCTrafftechPhaseCommand: '1.3.6.1.4.1.1618.3.7.2.11.1.0',
                     swarco_swarcoUTCCommandDark: '1.3.6.1.4.1.1618.3.2.2.2.1.0',
                     swarco_swarcoUTCCommandFlash: '1.3.6.1.4.1.1618.3.2.2.1.1.0',
                     swarco_swarcoUTCTrafftechPlanCommand: '1.3.6.1.4.1.1618.3.7.2.2.1.0',
                     swarco_swarcoUTCStatusEquipment: '1.3.6.1.4.1.1618.3.6.2.1.2.0'}

# ************************************************************************************ #

"""*******************************************************************
***                          GET-REQUEST                          ****   
**********************************************************************
"""

"""************************* Peek *************************"""

def get_stage_ug405_peek(ip_adress: str, scn_no_convert: str):
    """  Возвращает номер текущей фазы """

    scn = convert_scn(scn_no_convert)
    community = community_peek
    oid = f'{oids_UG405_PEEK.get(peek_utcReplyGn)}{scn}'
    stage6 = [' \n']
    bad_scn = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')
        val_list = proc.readlines()
        val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
        # print(val_list)
        # print(val_string)
        if 'Timeout' not in val_string and val_string != '0000' and val_list != stage6:
            return get_val_stage_UG405_PEEK.get(val_string)
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


def get_LO_ug405_peek(ip_adress, scn_no_convert):

    scn = convert_scn(scn_no_convert)
    community = community_peek
    oid = f'{oids_UG405_PEEK.get(peek_utcControlLO)}{scn}'
    bad_scn = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')

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


def get_FF_ug405_peek(ip_adress, scn_no_convert):

    scn = convert_scn(scn_no_convert)
    community = community_peek
    oid = f'{oids_UG405_PEEK.get(peek_utcControlFF)}{scn}'
    bad_scn = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')

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


def get_OperationModeTimeout_ug405_peek(ip_adress: str) -> str:

    community = community_peek
    oid = f'{oids_UG405_PEEK.get(peek_utcType2OperationModeTimeout)}'
    bad_scn = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')

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


def get_OperationMode_ug405_peek(ip_adress):

    community = community_peek
    oid = f'{oids_UG405_PEEK.get(peek_utcType2OperationMode)}'
    bad_scn = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')

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

############################################################

"""********************* Potok UG_405 *********************"""

def get_stage_ug405_potok(ip_adress: str, scn_no_convert: str):
    """  Возвращает номер текущей фазы """

    scn = convert_scn(scn_no_convert)
    community = community_peek
    oid = f'{oids_UG405_POTOK.get(get_current_stage_potok_UG405)}{scn}'
    stage6 = [' \n']
    bad_scn = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        # val_list = proc.stdout.readlines()
        # val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')

        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')
        val_list = proc.readlines()
        val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
        # print(val_list)
        # print(val_string)
        if val_list != stage6 and 'Timeout' not in val_string:
            return get_val_stage_UG405_POTOK.get(val_string)
        elif val_list == stage6:
            return 6
        elif i == 3:
            return 'None'
        elif 'Timeout' in val_string:
            continue
        elif val_list == bad_scn:
            return 'Bad scn'


def get_allow_bit_ug405_potok(ip_adress: str, scn_no_convert: str):
    scn = convert_scn(scn_no_convert)
    community = community_peek
    oid = f'{oids_UG405_POTOK.get(allow_bit_potok_UG405)}{scn}'
    bad_scn = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        # val_list = proc.stdout.readlines()
        # val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')

        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')
        val_list = proc.readlines()
        val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')

        # print(val_list)
        # print(val_string, type(val_string))
        if 'Timeout' not in val_string:
            return val_string
        elif i == 3:
            return 'None'
        elif 'Timeout' in val_string:
            continue
        elif val_list == bad_scn:
            return 'Bad scn'


def get_plan_ug405_potok(ip_adress: str, scn_no_convert: str):
    """  Возвращает номер текущего плана """

    scn = convert_scn(scn_no_convert)
    community = community_peek
    oid = f'{oids_UG405_POTOK.get(get_current_plan_potok_UG405)}{scn}'
    bad_scn = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        # val_list = proc.stdout.readlines()
        # val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')

        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')
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


def get_dark_ug405_potok(ip_adress: str, scn_no_convert: str):
    """ Возвращает значение (INTEGER):
        0 - ВЫКЛ выключен
        1 - ВЫКЛ включен
    """

    scn = convert_scn(scn_no_convert)
    community = community_peek
    oid = f'{oids_UG405_POTOK.get(get_dark_potok_UG405)}{scn}'
    bad_scn = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        # val_list = proc.stdout.readlines()
        # val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')

        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')
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


def get_flash_ug405_potok(ip_adress: str, scn_no_convert: str):
    """ Возвращает значение (INTEGER):
        0 - ЖМ выключен
        1 - по рассписанию
        2 - удаленно
        3 - в ручную
        4 - аварийный
    """

    scn = convert_scn(scn_no_convert)
    community = community_peek
    oid = f'{oids_UG405_POTOK.get(get_yellow_flash_potok_UG405)}{scn}'
    bad_scn = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        # val_list = proc.stdout.readlines()
        # val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')
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


def get_val_OperationMode_ug405_potok(ip_adress):

    community = community_peek
    oid = f'{oids_UG405_PEEK.get(peek_utcType2OperationMode)}'
    bad_scn = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        # val_list = proc.stdout.readlines()
        # val_string = " ".join(val_list).rstrip().replace('.', '').replace(' ', '')
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')
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

############################################################

"""********************* Potok STCIP **********************"""

def get_stage_stcip_potok(ip_adress: str):
    """  Возвращает номер текущей фазы """

    community = community_swarco
    oid = oids_STCIP_POTOK.get(get_current_stage_potok_STCIP)
    bad_oid = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')

        val = proc.readline().rstrip().replace(" ", '').replace('.', '')
        if 'Timeout' not in val and val != bad_oid:
            return get_val_stage_STCIP_potok.get(val)
        elif i == 3:
            return 'None'
        elif 'Timeout' in val:
            continue


def get_plan_stcip_potok(ip_adress: str):
    """  Возвращает номер текущего плана """

    community = community_swarco
    oid = oids_STCIP_POTOK.get(get_current_plan_potok_STCIP)
    bad_oid = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')

        val = proc.readline().rstrip().replace(" ", '').replace('.', '')
        if 'Timeout' not in val and val != bad_oid:
            return val
        elif i == 3:
            return 'None'
        elif 'Timeout' in val:
            continue


def get_mode_stcip_potok(ip_adress: str):
    """Возвращает статусы работы ДК: (INTEGER):
        0 - нет информации
        10 - ручное управление (Р)
        11 - удаленное управление (Ц)
        12 - рабочая программа (Ф или А)
    """

    community = community_swarco
    oid = oids_STCIP_SWARCO.get(get_mode_stip_potok)
    bad_oid = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')

        val = proc.readline().rstrip().replace(" ", '').replace('.', '')
        if 'Timeout' not in val and val != bad_oid:
            return val
        elif i == 3:
            return 'None'
        elif 'Timeout' in val:
            continue


def get_status_stcip_potok(ip_adress: str):
    """Возвращает статусы работы ДК: (INTEGER):
        0 - нет информации (Неизвестно)
        1 - рабочая программа (Ф или А)
        3 - ОС
        4 - ЖМ
        6 - КК
    """

    community = community_swarco
    oid = oids_STCIP_POTOK.get(get_status_stip_potok)
    bad_oid = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')

        val = proc.readline().rstrip().replace(" ", '').replace('.', '')
        if 'Timeout' not in val and val != bad_oid:
            return val
        elif i == 3:
            return 'None'
        elif 'Timeout' in val:
            continue


def get_dark_stcip_potok(ip_adress: str):

    community = community_swarco
    oid = oids_STCIP_SWARCO.get(dark_potok_STCIP)
    bad_oid = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')

        val = proc.readline().rstrip().replace(" ", '').replace('.', '')
        if 'Timeout' not in val and val != bad_oid:
            return val
        elif i == 3:
            return 'None'
        elif 'Timeout' in val:
            continue


def get_flash_stcip_potok(ip_adress: str):
    """ Возвращает значение (INTEGER):
        0 - ЖМ выключить
        2 - ЖМ включить
    """

    community = community_swarco
    oid = oids_STCIP_SWARCO.get(yellow_flash_potok_STCIP)
    bad_oid = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')

        val = proc.readline().rstrip().replace(" ", '').replace('.', '')
        if 'Timeout' not in val and val != bad_oid:
            return val
        elif i == 3:
            return 'None'
        elif 'Timeout' in val:
            continue


def get_all_red_stcip_potok(ip_adress: str):
    """ Возвращает значение (INTEGER):
        0 - КК выключить
        2 - КК включить
    """

    community = community_swarco
    oid = oids_STCIP_SWARCO.get(all_red_potok_STCIP)
    bad_oid = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')

        val = proc.readline().rstrip().replace(" ", '').replace('.', '')
        if 'Timeout' not in val and val != bad_oid:
            return val
        elif i == 3:
            return 'None'
        elif 'Timeout' in val:
            continue

############################################################

"""********************* Swarco STCIP *********************"""

def get_stage_stcip_swarco(ip_adress: str):
    """  Возвращает номер текущей фазы """

    community = community_swarco
    oid = oids_STCIP_SWARCO.get(swarco_swarcoUTCTrafftechPhaseStatus)
    bad_oid = ['\n']

    for i in range(4):
        # proc = subprocess.Popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}',
        #                         stdout=subprocess.PIPE, text=True)
        # val = proc.stdout.readline().rstrip().replace(" ", '').replace('.', '')
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')
        val = proc.readline().rstrip().replace(" ", '').replace('.', '')
        if 'Timeout' not in val and val != bad_oid:
            # proc.kill()
            return get_val_stage_STCIP_swarco.get(val)
        elif i == 3:
            # proc.kill()
            return 'None'
        elif 'Timeout' in val:
            # proc.kill()
            continue


def get_plan_stcip_swarco(ip_adress: str):
    """  Возвращает номер текущего плана """

    community = community_swarco
    oid = oids_STCIP_SWARCO.get(swarco_swarcoUTCTrafftechPlanCurrent)
    bad_oid = ['\n']

    for i in range(4):
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')
        val = proc.readline().rstrip().replace(" ", '').replace('.', '')
        if 'Timeout' not in val and val != bad_oid:
            return val
        elif i == 3:
            return 'None'
        elif 'Timeout' in val:
            continue


def get_status_stcip_swarco(ip_adress: str):
    """Возвращает значение "swarcoUTCStatusEquipment" (INTEGER):
        noInformation(0),
        workingProperly(1),
        powerUp(2),
        dark(3),
        flash(4),
        partialFlash(5),
        allRed(6)
    """

    community = community_swarco
    oid = oids_STCIP_SWARCO.get(swarco_swarcoUTCStatusEquipment)
    bad_oid = ['\n']

    for i in range(4):

        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')

        val = proc.readline().rstrip().replace(" ", '').replace('.', '')
        if 'Timeout' not in val and val != bad_oid:
            return val
        elif i == 3:
            return 'None'
        elif 'Timeout' in val:
            continue


def get_dark_stcip_swarco(ip_adress: str):
    """ Возвращает значение  swarcoUTCCommandDark (INTEGER):
         commandDarkNormal(0),
         commandDarkTimed(1),
         commandDarkPermanent(2) --> вкл. режим ОС(18 план)
     """

    community = community_swarco
    oid = oids_STCIP_SWARCO.get(swarco_swarcoUTCCommandDark)
    bad_oid = ['\n']

    for i in range(4):
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')
        val = proc.readline().rstrip().replace(" ", '').replace('.', '')
        if 'Timeout' not in val and val != bad_oid:
            return val
        elif i == 3:
            return 'None'
        elif 'Timeout' in val:
            continue


def get_flash_stcip_swarco(ip_adress: str):
    """ Возвращает значение  swarcoUTCCommandFlash (INTEGER):
        commandFlashNormal(0),
        commandFlashTimed(1),
        commandFlashPermanent(2) --> вкл. режим ЖМ(17 план)
    """

    community = community_swarco
    oid = oids_STCIP_SWARCO.get(swarco_swarcoUTCCommandFlash)

    for i in range(4):
        proc = os.popen(f'{snmp_get} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}')
        val = proc.readline().rstrip().replace(" ", '').replace('.', '')
        if 'Timeout' not in val:
            return val
        elif i == 3:
            return 'None'
        elif 'Timeout' in val:
            continue

##############################################################


"""*******************************************************************
***                          SET-REQUEST                          ****   
**********************************************************************
"""

"""************************* Peek *************************"""

def set_operation_timeout_ug405_peek(ip_adress: str,  value='90'):
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

    errorIndication, errorStatus, errorIndex, varBinds = next(
        setCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=1),
            UdpTransportTarget((ip_adress, 161), timeout=1, retries=2),
            ContextData(),
            ObjectType(ObjectIdentity(oid), value)
        )
    )


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

def set_operation_timeout_ug405_potok(ip_adress: str,  value='90'):
    """ Функция устанавливает таймаут  для OperationMode(Utc Control(3))
        Необходимо передать ip и значение таймаута. Если не передать значение,
        по умолчанию устанавливает 90 секунд
    """

    community = community_peek
    oid = f'{oids_UG405_POTOK.get(operaion_mode_timeout_potok_UG405)}'

    os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}' 
             f' -val:{value} -tp:int')

    # subprocess.Popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}'
    #                  f' -val:{value} -tp:int')


def set_operation_mode_ug405_potok(ip_adress: str, value='3'):
    """ Функция устанавливает режим operation mode:(Standalone(1), Utc Control(3)).
        Необходимо передать ip и значение, которое необходимо установить для
        operation mode. Если значение не передать, по умолчанию установит
        Utc Control(3)
    """

    community = community_peek
    oid = f'{oids_UG405_PEEK.get(peek_utcType2OperationMode)}'

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}' 
                 f' -val:{value} -tp:int')
        # subprocess.Popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}'
        #                  f' -val:{value} -tp:int', shell=True)


def set_Fn_ug405_potok(ip_adress: str, scn_no_convert: str, value):
    """ Функция устанавливает set запрос фазы (Fn бит)
        Необходимо передать ip, scn в виде "COxxxx"(например "СO1111",
        значение фазы в виде: "Фаза 1", "Фаза 2"..."Фаза n"
    """
    if value not in set_stage_UG405_potok_values:
        return

    scn = convert_scn(scn_no_convert)
    community = community_peek
    oid = f'{oids_UG405_POTOK.get(set_stage_potok_UG405)}{scn}'
    value = set_stage_UG405_potok_values.get(value)
    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}' 
                 f' -val:{value} -tp:hex')


def set_TO_ug405_potok(ip_adress, scn_no_convert, value='1'):
    """ Функция устанавливает  значение в TO бит.
        Необходимо передать ip, scn в виде "COxxxx"(например "СO1111", значение 0 или 1.
        Если значение не передать, по умолчанию установит 1.
    """

    scn = convert_scn(scn_no_convert)
    community = community_peek
    oid = f'{oids_UG405_POTOK.get(allow_bit_potok_UG405)}{scn}'

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}' 
                         f' -val:{value} -tp:int')


def set_reset_dark_ug405_potok(ip_adress, scn_no_convert, value='0'):
    """ Функция устанавливает  режим ОС.
        Необходимо передать ip, scn в виде "COxxxx"(например "СO1111", значение 0 или 1.
        Если значение не передать, по умолчанию установит 0.
    """

    scn = convert_scn(scn_no_convert)
    community = community_peek
    oid = f'{oids_UG405_POTOK.get(set_reset_dark_potok_UG405)}{scn}'

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}' 
                 f' -val:{value} -tp:int')


def set_reset_yellow_flash_ug405_potok(ip_adress, scn_no_convert, value=0):
    """ Функция устанавливает  режим ЖМ..
        Необходимо передать ip, scn в виде "COxxxx"(например "СO1111", значение 0 или 1.
        Если значение не передать, по умолчанию установит 0.
    """

    scn = convert_scn(scn_no_convert)
    community = community_peek
    oid = f'{oids_UG405_POTOK.get(set_reset_yellow_flash_potok_UG405)}{scn}'

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}' 
                 f' -val:{value} -tp:int')


def restart_programm_ug405_potok(ip_adress, scn_no_convert, value='1'):
    """ Функция перезапускает программу ДК..
        Необходимо передать ip, scn в виде "COxxxx"(например "СO1111".
    """

    scn = convert_scn(scn_no_convert)
    community = community_peek
    oid = f'{oids_UG405_POTOK.get(set_restart_programm_potok_UG405)}{scn}'

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}' 
                 f' -val:{value} -tp:int')

##############################################################

"""********************* Potok STCIP **********************"""

def set_reset_dark_stcip_potok(ip_adress, value='0'):
    """ Функция включает/выключает режим ОС..
        Необходимо передать ip и значение: 2 -> включить ОС, 0 -> выключить ОС.
        Если не передать значение, установит 0(выключить ОС)
    """

    community = community_swarco
    oid = f'{oids_STCIP_POTOK.get(dark_potok_STCIP)}'

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}' 
                 f' -val:{value} -tp:int')


def set_reset_yellow_flash_stcip_potok(ip_adress, value='0'):
    """ Функция включает/выключает режим ЖМ..
        Необходимо передать ip и значение: 2 -> включить ЖМ, 0 -> выключить ЖМ.
        Если не передать значение, установит 0(выключить ЖМ)
    """

    community = community_swarco
    oid = f'{oids_STCIP_POTOK.get(yellow_flash_potok_STCIP)}'

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}' 
                 f' -val:{value} -tp:int')


def set_reset_all_red_stcip_potok(ip_adress, value='0'):
    """ Функция включает/выключает режим КК..
        Необходимо передать ip и значение: 2 -> включить КК, 0 -> выключить КК.
        Если не передать значение, установит 0(выключить КК)
    """

    community = community_swarco
    oid = f'{oids_STCIP_POTOK.get(all_red_potok_STCIP)}'

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}' 
                 f' -val:{value} -tp:int')


def set_stage_stcip_potok(ip_adress, value='ЛОКАЛ'):
    """ Функция устанавливает set запрос фазы
        Необходимо передать ip, значение фазы в виде: "Фаза 1", "Фаза 2"..."Фаза n".
        Если не указать значение, то по умолчанию установит 0(перевод в "Локал")
    """

    if value not in set_stage_STCIP_potok_values:
        return

    community = community_swarco
    oid = f'{oids_STCIP_POTOK.get(set_stage_potok_STCIP)}'
    value = set_stage_STCIP_potok_values.get(value)

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}' 
                 f' -val:{value} -tp:uint')


def restart_programm_stcip_potok(ip_adress, value='1'):
    """ Функция перезапускает программу ДК..
        Необходимо передать ip, scn в виде "COxxxx"(например "СO1111".
    """

    community = community_swarco
    oid = f'{oids_STCIP_POTOK.get(set_restart_programm_potok_STCIP)}'

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}' 
                 f' -val:{value} -tp:int')

##############################################################

"""********************* Swarco STCIP *********************"""

def set_set_reset_dark_stcip_swarco(ip_adress, value='0'):
    """ Функция включает/выключает режим ОС..
        Необходимо передать ip и значение: 2 -> включить ОС, 0 -> выключить ОС.
        Если не передать значение, установит 0(выключить ОС)
    """

    community = community_swarco
    oid = f'{oids_STCIP_SWARCO.get(swarco_swarcoUTCCommandDark)}'

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}' 
                 f' -val:{value} -tp:int')


def set_set_reset_yellow_flash_stcip_swarco(ip_adress, value='0'):
    """ Функция включает/выключает режим ЖМ..
        Необходимо передать ip и значение: 2 -> включить ЖМ, 0 -> выключить ЖМ.
        Если не передать значение, установит 0(выключить ЖМ)
    """

    community = community_swarco
    oid = f'{oids_STCIP_SWARCO.get(swarco_swarcoUTCCommandFlash)}'

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}' 
                 f' -val:{value} -tp:int')


def set_set_reset_all_red_stcip_swarco(ip_adress, value='100'):
    """ Функция включает/выключает режим КК..
        Необходимо передать ip и значение: 119 -> включить КК, 100 -> выключить КК.
        По умолчанию выключает  КК -> val=100
    """

    community = community_swarco
    oid = f'{oids_STCIP_SWARCO.get(swarco_swarcoUTCTrafftechPlanCommand)}'

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}' 
                 f' -val:{value} -tp:uint')


def set_stage_stcip_swarco(ip_adress: str, value: str = 'ЛОКАЛ'):
    """ Функция устанавливает set запрос фазы
        Необходимо передать ip, значение фазы в виде: "Фаза 1", "Фаза 2"..."Фаза n".
        Если не указать значение, то по умолчанию установит 0(перевод в "Локал")
    """

    if value not in set_stage_STCIP_swarco_values:
        return

    community = community_swarco
    oid = f'{oids_STCIP_SWARCO.get(swarco_swarcoUTCTrafftechPhaseCommand)}'
    value = set_stage_STCIP_swarco_values.get(value)

    for i in range(2):
        os.popen(f'{snmp_set} -q -r:{ip_adress} -v:2c -t:1 -c:{community} -o:{oid}' 
                 f' -val:{value} -tp:uint')

##############################################################

"""****************** Different functions ******************"""

def convert_scn(scn):
    """ Функция получает на вход строку, которую необходимо конвертировать в SCN
        для управления и мониторинга по протоколу UG405.
        Например: convert_scn(CO1111)
    """
    len_scn = str(len(scn)) + '.'
    convert_to_ASCII = [str(ord(c)) for c in scn]
    scn = f'.1.{len_scn}{".".join(convert_to_ASCII)}'
    return scn


def check_host_tcp(ip_adress: str, port=80, timeout=2):
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


