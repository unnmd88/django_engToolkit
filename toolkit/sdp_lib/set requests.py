import sys
from sys import argv
import time

import asyncio

import ssh_sftp_ftp_management
from web_management import PeekWeb, PotokWeb

import configuration
import sdp_func_lib
import controller_management

protocols = ('Поток_UG405', 'Поток_STCIP', 'Swarco_STCIP', 'Peek_UG405')
# if __name__ == '__main__':
#     sys.exit()
def make_obj_snmp(protocol, ip_adress, scn=None):
    print(protocol, ip_adress)
    if protocol == 'Swarco_STCIP':
        print('11111')
        obj = snmp_managemement_v3.SwarcoSTCIP(ip_adress)
    elif protocol == 'Поток_STCIP':
        obj = snmp_managemement_v3.PotokS(ip_adress)
    elif protocol == 'Поток_UG405':
        obj = snmp_managemement_v3.Potok(ip_adress, scn)
    elif protocol == 'Peek_UG405':
        obj = snmp_managemement_v3.PeekUG405(ip_adress, scn)
    else:
        obj = None

    return obj


async def main(inner_data):
    """
    :param inner_data:
    :return:
    """
    tasks = []

    for method, value in inner_data:
        tasks.append(method(value))

    result = await asyncio.gather(*tasks)
    print(f'result::- {result}')


def make_methods_for_snmp_commands(num_host, ip_adress, protocol, scn, value, request):

    tasks = []

    host = snmp_managemement_v3.GetDataControllerManagement()
    host = host.create_snmp_object_get_request(num_host, ip_adress, protocol, scn)

    if 'фаза' in request:
        tasks.append((host.set_stage, value))
    elif 'жм' in request:
        tasks.append((host.set_flash, value))
    elif 'ос' in request:
        tasks.append((host.set_dark, value))
    elif 'кк' in request:
        tasks.append((host.set_allred, value))
    return tasks

print(f'argv: {argv}')

num_host, ip_adress, protocol, scn, request, value = argv[1].split(';')
request = request.lower()

if 'snmp' in request:
    methods = make_methods_for_snmp_commands(num_host, ip_adress, protocol, scn, value, request)
    asyncio.run(main(methods))
    sys.exit()
elif 'фаза man' in request and protocol == protocols[2]:

    host = snmp_managemement_v3.SwarcoSSH(ip_adress)
    res = host.set_stage(value)
    print(res)
elif 'фаза man' in request and protocol == protocols[3]:
    host = snmp_managemement_v3.PeekWeb(ip_adress)
    if value != '0':
        host.session_manager(inputs=(f"MPP_PH{value}=ВКЛ", f"MPP_MAN=ВКЛ"))
    else:
        host.session_manager(inputs=[f'MPP_MAN=ВФ' if inp == 0 else f'MPP_PH{inp}=ВФ' for inp in range(9)])
elif 'вводы' in request and protocol == protocols[3]:
    host = snmp_managemement_v3.PeekWeb(ip_adress)
    inputs = value.upper().replace(" ", '').split(',')
    print(inputs)
    host.session_manager(inputs=inputs)


sys.exit()

























if type_request == 'snmp_requset':
    ip_adress, protocol, scn, request = argv[2].split(';')
    type_set, value = request.split('=')

    host = snmp_managemement_v3.GetDataControllerManagement()
    host = host.create_snmp_object_get_request(protocol, ip_adress, scn)


    if 'фаза' in type_set.lower():
        tasks.append((host.set_stage, value))
    elif 'жм' in type_set.lower():
        tasks.append((host.set_flash, value))
    elif 'ос' in type_set.lower():
        tasks.append((host.set_dark, value))
    print(f'tasks: {tasks}')
    asyncio.run(main(tasks))

sys.exit()








""" SNMP Management """
def set_stage_all_protocols(ip_adress: str, protocol: str, scn_no_convert: str, value: str = 'ЛОКАЛ', ):

    if protocol == 'UG405_Поток':
        snmpmanagement.set_operation_timeout_ug405_potok(ip_adress)
        snmpmanagement.set_operation_mode_ug405_potok(ip_adress)
        snmpmanagement.set_TO_ug405_potok(ip_adress, scn_no_convert)
        snmpmanagement.set_Fn_ug405_potok(ip_adress, scn_no_convert, value)
    elif protocol == 'STCIP_Поток':
        snmpmanagement.set_stage_stcip_potok(ip_adress, value)
    elif protocol == 'STCIP_Swarco':
        snmpmanagement.set_stage_stcip_swarco(ip_adress, value)
    elif protocol == 'UG405_Peek':
        snmpmanagement.set_operation_timeout_ug405_peek(ip_adress)
        snmpmanagement.set_operation_mode_ug405_peek(ip_adress)
        snmpmanagement.set_TO_ug405_peek(ip_adress, scn_no_convert)
        snmpmanagement.set_Fn_ug405_peek(ip_adress, scn_no_convert, value)


def set_local_all_protocols(ip_adress: str, protocol: str):
    if protocol == 'UG405_Поток':
        snmpmanagement.set_operation_mode_ug405_potok(ip_adress, value='1')
    elif protocol == 'STCIP_Поток':
        snmpmanagement.set_stage_stcip_potok(ip_adress)
    elif protocol == 'STCIP_Swarco':
        snmpmanagement.set_stage_stcip_swarco(ip_adress)
    elif protocol == 'UG405_Peek':
        snmpmanagement.set_operation_mode_ug405_peek(ip_adress, value='1')


def set_reset_dark_all_protocols(ip_adress: str, protocol: str, scn_no_convert: str, value: str = 'False',):
    if value == 'ВКЛ':
        if protocol == 'UG405_Поток':
            snmpmanagement.set_operation_mode_ug405_potok(ip_adress)
            snmpmanagement.set_reset_dark_ug405_potok(ip_adress, scn_no_convert, value='1')
        elif protocol == 'STCIP_Поток':
            snmpmanagement.set_reset_dark_stcip_potok(ip_adress, value='2')
        elif protocol == 'STCIP_Swarco':
            snmpmanagement.set_set_reset_dark_stcip_swarco(ip_adress, value='2')
        elif protocol == 'UG405_Peek':
            snmpmanagement.set_operation_mode_ug405_peek(ip_adress)
            snmpmanagement.set_LO_ug405_peek(ip_adress, scn_no_convert, value='1')
    elif value == 'ВЫКЛ':
        if protocol == 'UG405_Поток':
            snmpmanagement.set_reset_dark_ug405_potok(ip_adress, scn_no_convert)
            snmpmanagement.set_operation_mode_ug405_potok(ip_adress, value='1')
        elif protocol == 'STCIP_Поток':
            snmpmanagement.set_reset_dark_stcip_potok(ip_adress, value='0')
        elif protocol == 'STCIP_Swarco':
            snmpmanagement.set_set_reset_dark_stcip_swarco(ip_adress, value='0')
        elif protocol == 'UG405_Peek':
            snmpmanagement.set_operation_mode_ug405_peek(ip_adress, value='1')
            snmpmanagement.set_LO_ug405_peek(ip_adress, scn_no_convert, value='0')


def set_reset_yellow_flash_all_protocols(ip_adress: str, protocol: str, scn_no_convert: str, value: str = 'False', ):
    if value == 'ВКЛ':
        if protocol == 'UG405_Поток':
            snmpmanagement.set_operation_mode_ug405_potok(ip_adress)
            snmpmanagement.set_reset_yellow_flash_ug405_potok(ip_adress, scn_no_convert, value='1')
        elif protocol == 'STCIP_Поток':
            snmpmanagement.set_reset_yellow_flash_stcip_potok(ip_adress, value='2')
        elif protocol == 'STCIP_Swarco':
            snmpmanagement.set_set_reset_yellow_flash_stcip_swarco(ip_adress, value='2')
        elif protocol == 'UG405_Peek':
            snmpmanagement.set_operation_mode_ug405_peek(ip_adress)
            snmpmanagement.set_FF_ug405_peek(ip_adress, scn_no_convert, value='1')
    elif value == 'ВЫКЛ':
        if protocol == 'UG405_Поток':
            snmpmanagement.set_reset_yellow_flash_ug405_potok(ip_adress, scn_no_convert)
            snmpmanagement.set_operation_mode_ug405_potok(ip_adress, value='1')
        elif protocol == 'STCIP_Поток':
            snmpmanagement.set_reset_yellow_flash_stcip_potok(ip_adress, value='0')
        elif protocol == 'STCIP_Swarco':
            snmpmanagement.set_set_reset_yellow_flash_stcip_swarco(ip_adress, value='0')
        elif protocol == 'UG405_Peek':
            snmpmanagement.set_LO_ug405_peek(ip_adress, scn_no_convert, value='0')
            snmpmanagement.set_operation_mode_ug405_peek(ip_adress, value='1')


def set_reset_all_red_stcip(ip_adress: str, protocol: str, value: str = 'False',):

    if value == 'ВКЛ':
        if protocol == 'STCIP_Поток':
            snmpmanagement.set_reset_all_red_stcip_potok(ip_adress, value='1')
        elif protocol == 'STCIP_Swarco':
            snmpmanagement.set_stage_stcip_swarco(ip_adress)
            snmpmanagement.set_set_reset_all_red_stcip_swarco(ip_adress, value='119')
    elif value == 'ВЫКЛ':
        if protocol == 'STCIP_Поток':
            snmpmanagement.set_reset_all_red_stcip_potok(ip_adress)
        elif protocol == 'STCIP_Swarco':
            snmpmanagement.set_set_reset_all_red_stcip_swarco(ip_adress)


def restart_programm_potok(ip_adress: str, protocol: str):
    if protocol == 'UG405_Поток':
        snmpmanagement.restart_programm_ug405_potok(ip_adress, scn_no_convert)
    elif protocol == 'STCIP_Поток':
        snmpmanagement.restart_programm_stcip_potok(ip_adress)


""" Restart web potok """



# """ SSH Management swarco """
# def swarco_ssh(ip_adress=None, inp102='-', inp102_value=0, inp_xx='-', inp_xx_value=0):
#
#     print('ya v swarco_ssh')
#     values = {'INPUT 102(РУ)': 'inp 102', 'INPUT 103(ЖМ)': 'inp 103', 'INPUT 104(Ф1)': 'inp 104',
#               'INPUT 105(Ф2)': 'inp 105', 'INPUT 106(Ф3)': 'inp 106', 'INPUT 107(Ф4)': 'inp 107',
#               'INPUT 108(Ф5)': 'inp 108', 'INPUT 109(Ф6)': 'inp 109', 'INPUT 110(Ф7)': 'inp 110',
#               'INPUT 111(Ф8)': 'inp 111', 'INPUT 101(ОС)': 'inp 101', '-': "-"
#               }
#
#     inp102, inp_xx = values[inp102], values[inp_xx]
#     print(f'inp102: {inp102}, inp_xx: {inp_xx}, inp102_value: {inp102_value}')
#     bytes_recv = 6000
#     sleep_1sec = 0.4
#     short_sleep = 0.2
#
#     if inp102 == '-' and inp_xx == '-':
#         return
#
#     # logging.basicConfig()
#     # logging.getLogger("paramiko").setLevel(logging.INFO)
#     # paramiko.util.log_to_file("logs/ssh_swarco", level="INFO")
#
#     data_auth = configuration.auth('ssh swarco a')
#     login_ssh, password_ssh = data_auth[0]
#     login, password = data_auth[1]
#     print(f'login: {login_ssh}, password: {password_ssh}, login: {login}, password:{password}')
#     client = paramiko.SSHClient()
#     client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#     client.connect(hostname=ip_adress,
#                    username=login_ssh,
#                    password=password_ssh,
#                    look_for_keys=False, allow_agent=False)
#
#     with client.invoke_shell() as ssh:
#         ssh.send('lang UK\n')
#         time.sleep(short_sleep)
#
#         ssh.send(f'{login}\n')
#         time.sleep(short_sleep)
#
#         ssh.send(f'{password}\n')
#         # ssh.recv(bytes_recv)
#         time.sleep(short_sleep)
#
#         if inp102 != '-':
#             ssh.send(f'{inp102}={inp102_value}\n\n')
#             # ssh.recv(bytes_recv)
#             time.sleep(sleep_1sec)
#
#         if inp_xx != '-':
#             ssh.send(f'{inp_xx}={inp_xx_value}\n\n')
#             # ssh.recv(bytes_recv)
#             time.sleep(sleep_1sec)
#
#         # for_output = ssh.recv(6000).decode(encoding='utf-8')
#         # print(for_output)
#
#         # with open('logs/ssh_swarco.txt', 'a') as file:
#         #     file.write(f'{datetime.today().strftime("%Y-%m-%d %H:%M:%S")}, '
#         #                f'ip_adress: {ip_adress}\n')
#         #     file.write(f'{ssh.recv(bytes_recv).decode(encoding="utf8")}\n')
#         #     file.write('*' * 75 + '\n')
#
#         ssh.send('exit\n')
#         # ssh.recv(bytes_recv)
#         time.sleep(sleep_1sec)
#         outp = ssh.recv(6000).decode(encoding="latin-1")
#         print(outp)
#         with open('logs/ssh_swarco.txt', 'a', encoding="latin-1") as file:
#             file.write(f'{datetime.today().strftime("%Y-%m-%d %H:%M:%S")}, '
#                        f'ip_adress: {ip_adress}\n')
#             file.write(f'{outp}\n')
#             file.write('*' * 75 + '\n')

""" Web management Peek """



start_time = time.time()
try:
    action = argv[1]
except IndexError:
    action = None
# print(f'argv: {argv}')
if action is None:
    sys.exit()
elif action == configuration.action_snmp_management:
    # flag, ip_adress, protocol, value, scn_no_convert = argv[2:]
    scn_no_convert, ip_adress, protocol, type_request, value = argv[2:]
    if type_request == 'СБРОС':
        type_request = 'ЛОКАЛ'
    # print(argv[2:])

    if type_request == configuration.flag_set_stage_snmp:
        set_stage_all_protocols(ip_adress, protocol, scn_no_convert, value)
        # print('я в set_stage')
        # print(f'это end_time set_stage: {time.time() - start_time}')
    elif type_request == configuration.flag_set_local_snmp:
        set_local_all_protocols(ip_adress, protocol)
        # print('я в flag_set_local_snmp')
        # print(f'это end_time flag_set_local_snmp: {time.time() - start_time}')
    elif type_request == configuration.flag_set_reset_yellow_flash_snmp:
        set_reset_yellow_flash_all_protocols(ip_adress, protocol, scn_no_convert, value)
        # print('я в flag_set_reset_yellow_flash_snmp')
        # print(f'это end_time flag_set_reset_yellow_flash_snmp: {time.time() - start_time}')
    elif type_request == configuration.flag_set_reset_dark_snmp:
        set_reset_dark_all_protocols(ip_adress, protocol, scn_no_convert, value)
        # print('я в flag_set_reset_dark_snmp')
        # print(f'это end_time flag_set_reset_dark_snmp: {time.time() - start_time}')
    elif type_request == configuration.flag_set_reset_all_red_snmp:
        set_reset_all_red_stcip(ip_adress, protocol, value)
        # print('я в flag_set_reset_all_red_snmp')
        # print(f'это end_time flag_set_reset_all_red_snmp: {time.time() - start_time}')
    elif type_request == configuration.flag_restart_programm_potok_snmp:
        restart_programm_potok(ip_adress, protocol)
        # print('я в flag_restart_programm_potok_snmp')
        # print(f'это end_time flag_restart_programm_potok_snmp: {time.time() - start_time}')
    elif type_request == configuration.flag_restart_web_admin:
        sdp_func_lib.set_restart_web_admin(ip_adress)
        # sys.exit()
    elif type_request == configuration.flag_reboot_controller:
        if protocol == configuration.type_controller_swarco or protocol == configuration.type_controller_peek:
            commands = ['reboot \n']
            ssh_sftp_ftp_management.CommandsToShell(ip_adress=ip_adress, controller_type=protocol, commands=commands,
                                                    flag_commands_to_shell=True)
        else:
            PotokWeb(ip_adress, flag='reboot')
elif action == configuration.action_swarco_ssh:
    args = argv[2:]
    # print('я в action == swarco_ssh')
    ssh_sftp_ftp_management.SwarcoWorkStationManagement(flag_make_session=True, args=args)
    # print(args)
elif action == configuration.action_filter_snmp:
    args = argv[2:]
    if args[2] == 'Swarco':
        if args[3] != 'Загрузить json swarco':
            ssh_sftp_ftp_management.SwarcoFilterSnmp(flag_make_session=True, args=args)
        elif args[3] == 'Загрузить json swarco':
            # print('Загрузить json swarco')
            get_json = ssh_sftp_ftp_management.SwarcoGetFile(ip_adress=args[0], flag='get json')
    elif args[2] == 'Peek':
        ssh_sftp_ftp_management.PeekFilterSnmp(args=args)
elif action == configuration.action_peek_web_management_MPP:
    ip_adress, mpp_man, mpp_man_value, input_name, input_value = argv[2:]
    # print(argv[2:])
    host = PeekWeb(ip_adress=ip_adress)
    host.session_refactor(inputs={mpp_man: mpp_man_value, input_name: input_value})
elif action == configuration.action_peek_web_management_UP:
    ip_adress, UP_index, UP_val = argv[2:]
    host = PeekWeb(ip_adress=ip_adress)
    host.session_refactor(user_parameters={UP_index: UP_val})
# elif action == configuration.action_greenroad:
#     ip_adress = argv[3]
#
#     if argv[2] == configuration.flag_greenroad_peek_web:
#         # print('я в peek web')
#         # commands = sdp_func_lib.sorting_data_for_greenroad_web_peek(argv[4])
#         # print(argv[4])
#         commands = argv[4].strip().split(';')
#         # commands = sdp_func_lib.sorting_data_for_greenroad_web_peek(commands)
#         # print(f'commands: {commands}')
#         # sorted_data = sdp_func_lib.sorting_data_for_greenroad_web_peek(intersection_data)
#         # print(f'sorted_data: {sorted_data}')
#         mpp_man = mpp_man_val = mpp_stage = mpp_stage_val = combo_mpp_flash_off = \
#             combo_mpp_flash_off_value = up_index = up_value = '-'
#         for item in commands:
#             if 'MPP_MAN' in item:
#                 mpp_man, mpp_man_val = item.split('=')
#                 # print(f'mpp_man: {mpp_man} mpp_man_val: {mpp_man_val}')
#             elif 'MPP_PH' in item:
#                 mpp_stage, mpp_stage_val = item.split('=')
#                 # print(f'mpp_man: {mpp_stage} mpp_man_val: {mpp_stage_val}')
#             elif ('MPP_FL' or 'MPP_OFF') in item:
#                 combo_mpp_flash_off, combo_mpp_flash_off_value = item.split('=')
#                 # print(f'combo_mpp_flash_off: {combo_mpp_flash_off} combo_mpp_flash_off_value: {combo_mpp_flash_off_value}')
#             # elif 'MPP_OFF' in item:
#             #     combo_mpp_flash_off, combo_mpp_flash_off_value = item.split('=')
#             #     print(f'combo_mpp_flash_off: {combo_mpp_flash_off} combo_mpp_flash_off_value: {combo_mpp_flash_off_value}')
#             elif 'UPi' in item:
#                 up_index = item.split('=')[1]
#                 # print(f'up_index: {up_index}')
#             # elif item == 'UPi':
#             #     up_index, up_value = item.split('=')
#             #     print(f'up_index: {up_index} up_value: {up_value}')
#             elif 'UPv' in item:
#                 up_value = item.split('=')[1]
#                 # print(f'up_value: {up_value}')
#
#         set_MPP_peek_refactor(ip_adress=ip_adress,
#                               mpp_man=mpp_man, mpp_man_value=mpp_man_val,
#                               input1_name=mpp_stage, input1_value=mpp_stage_val,
#                               combo_mpp_flash_off=combo_mpp_flash_off, combo_mpp_flash_off_value=combo_mpp_flash_off_value,
#                               UP_index=up_index, UP_val=up_value)
#
#     elif argv[2] == configuration.flag_greenroad_swarco_ssh:
#         commands = argv[4].split(';')
#         # print(f'commands: {commands}')
#         ssh_sftp_ftp_management.CommandsToShell(
#             ip_adress=ip_adress, controller_type=configuration.type_controller_swarco,
#             flag_commands_swarco_ws=True, write_log=False, commands=commands)
#     elif argv[2] == configuration.flag_greenroad_snmp and argv[6] == configuration.flag_set_stage_snmp:
#         # print(f'argv[6]: {argv[6]}')
#         # print(configuration.flag_greenroad_snmp)
#         scn_no_convert, ip_adress,  protocol, type_request, value = argv[3:]
#         # scn_no_convert, ip_adress, protocol, type_request, value
#         # print(argv[3:])
elif action == configuration.action_new_greenroad and argv[3] == 'WEB_Peek':
    ip_adress = argv[2]
    type_command = argv[4]
    if type_command == 'СБРОС':
        host = PeekWeb(ip_adress)

        # 3 попытки выполнения скрипта по сбросу фазы. Если во время сессии произошла ошибка и мы попали в except-
        # то предринимаем следующую попытку, при это ставим флаг increase_the_timeout=True, который будет увеличивать
        # таймаут на каждой попытке
        for attempt in range(3):
            if attempt < 1:
                try:
                    host.session_refactor(resetting_the_desired_values={'ВЫКЛ': ('ВКЛ',)}, MPP_MAN='ВФ')
                    break
                except Exception as err:
                    pass
            else:
                try:
                    host.session_refactor(increase_the_timeout=True,
                                          resetting_the_desired_values={'ВЫКЛ': ('ВКЛ',)}, MPP_MAN='ВФ')
                    break
                except Exception as err:
                    pass

    elif type_command == 'ФАЗА':
        # stages = {str(num_stage): f'MPP_PH{num_stage}' for num_stage in range(1, 9)}
        host = PeekWeb(ip_adress)
        # 3 попытки выполнения скрипта по установлению фазы. Если во время сессии произошла ошибка и мы попали в except-
        # то предринимаем следующую попытку, при это ставим флаг increase_the_timeout=True, который будет увеличивать
        # таймаут на каждой попытке
        for attempt in range(3):
            if attempt < 1:
                try:
                    host.session_refactor(session_for_greenroad=True,
                                          inputs={'MPP_MAN': 'ВКЛ', f'MPP_PH{argv[5]}': 'ВКЛ'},
                                          resetting_the_desired_values={'ВЫКЛ': ('ВКЛ',)})
                    break
                except Exception as err:
                    pass
            else:
                try:
                    host.session_refactor(increase_the_timeout=True,
                                          inputs={'MPP_MAN': 'ВКЛ', f'MPP_PH{argv[5]}': 'ВКЛ'},
                                          resetting_the_desired_values={'ВЫКЛ': ('ВКЛ',)})
                    break
                except Exception as err:
                    pass



elif action == configuration.action_new_greenroad and argv[3] == 'SSH_Swarco':
    ip_adress = argv[2]
    type_command = argv[4]
    if type_command == 'СБРОС':
        commands = [f'{inp}=0' for inp in range(102, 112) if inp != 103]
        ssh_sftp_ftp_management.CommandsToShell(
            ip_adress=ip_adress, controller_type=configuration.type_controller_swarco,
            flag_commands_swarco_ws=True, write_log=True, flag_reset_inp104_111=True)
    elif type_command == 'ФАЗА':
        # stages = {str(k): str(v) for k, v in zip(range(1, 9), range(104, 112))}
        commands = ['inp102=1', f'inp{int(argv[5]) + 103}=1']
        ssh_sftp_ftp_management.CommandsToShell(
            ip_adress=ip_adress, controller_type=configuration.type_controller_swarco,
            flag_commands_swarco_ws=True, write_log=True, flag_reset_inp104_111=True,  commands=commands)

elif action == configuration.action_peek_web_management_set_any_number_of_inputs:
    ip_adress = argv[2]
    host = PeekWeb(ip_adress=ip_adress)
    host.session_refactor(resetting_the_desired_values={'ВФ': ('ВКЛ', 'ВЫКЛ')})

# print(f'время выполнения скрипта = {time.time() - start_time}')



