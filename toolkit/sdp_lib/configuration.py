from datetime import datetime
from cryptography.fernet import Fernet
# import py7zr

key = b'KwTaJUNIInP0OkUSbZ_FDNRta7i_uq6dKd1cn7S_ILg='


API_KEY_SDP_BOT = '6780965651:AAHZeXU8EYiYNDnfmIrDmhCdxZx-4EOwNKs'
# chat_id_logi = '-1002014919954' # тестовая группа Логи_Тест
chat_id_logi = "-1002098352808" # Боевая группа Логи


access_levels = {
    'root': 'rootty',
    'admin': 'adminsdp24',
    'user': 'helpmeplease'
}

# login_for_app_admin = 'admin'
# password_for_app_admin = 'adminsdp24'
#
# login_for_app_user = 'user'
# password_for_app_app_user = 'helpmeplease'
#
#
# login_for_app_root = 'root'
# password_for_app_root = 'rootty'

filename_exec = 'set requests.py'


snmp_management_first_line = '*config hosts for snmp management*'
filter_snmp_first_line = '*config hosts for filter snmp management*'
swarco_ssh_management_first_line = '*config hosts for swarco ssh management*'
peek_web_management_first_line = '*config hosts for peek_web_management*'
greenroad_first_line = '*config hosts greenroad*'


action_snmp_management = 'snmp management'
action_swarco_ssh = 'swarco_ssh'
action_swarco_ssh_from_user_file = 'swarco_ssh_from_user_file'
action_filter_snmp = 'filter snmp'
action_filter_snmp_from_user_file = 'action_filter_snmp_from_user_file'
action_peek_web_management_MPP = 'peek_mpp_management'
action_peek_web_management_UP = 'peek_up_management'
action_greenroad = 'greenroad'
action_new_greenroad = 'new_greenroad'
action_peek_web_management_set_any_number_of_inputs = 'peek_web_management_set_any_number_of_inputs'

flag_set_stage_snmp = 'ФАЗА'
flag_set_local_snmp = 'ЛОКАЛ'
flag_set_reset_yellow_flash_snmp = 'ЖМ'
flag_set_reset_dark_snmp = 'ОС'
flag_set_reset_all_red_snmp = 'КК'
flag_restart_programm_potok_snmp = 'РЕСТАРТ ПРОГРАММЫ ПОТОК'
flag_restart_web_admin = 'РЕСТАРТ ВЕБ ПОТОК'
flag_reboot_controller = 'ПЕРЕЗАГРУЗКА ДК'





flag_swarco_ssh_management = 'swarco_ssh_management'

path_to_restart_web_admin = r'restart_web_admin/restart_web_admin.exe'
restart_web_admin = 'restart_web_admin'


flag_greenroad_swarco_ssh = 'swarco ssh'
flag_greenroad_peek_web = 'peek web'
flag_greenroad_snmp = 'snmp'

interval_to_set_stage_before_10_second = 3
interval_to_set_stage_after_10_second = 10
timeout_for_dark_yellow_red = 9999999
interval_to_set_dark_flash_red = 4

flag_filter_snmp = 'flag_filter_snmp'

flag_reboot = 'reboot'

type_controller_swarco = 'STCIP_Swarco'
type_controller_peek = 'UG405_Peek'
type_controller_potokUG405 = 'UG405_Potok'
type_controller_potokSTCIP = 'STCIP_Potok'



path_to_file_log_ssh_filter_snmp = 'logs/log_ssh_filter_snmp.txt'
path_to_file_log_ssh_set_inp_outp_Mreg = 'logs/log_ssh_set_inp_outp_Mreg.txt'
path_to_faults_log = 'logs/faults_log.txt'
path_to_file_greenroad_log = 'logs/greenroad_log.txt'

path_to_faults_log_webdriver = 'logs/faults_webdriver.txt'


path_to_60_stcip = 'etc/swarco/60_stcip'
path_to_60_stcip_ishodniy = 'etc/swarco/60_stcip_ishodniy'
path_to_60_stcip_modify = 'etc/swarco/60_stcip_modify'
path_to_S79UG405init = 'etc/peek/S79UG405init'
path_to_etc_peek = 'etc/peek/'
path_to_S79UG405init_ishodniy = 'etc/peek/S79UG405init_ishodniy'
path_to_S79UG405init_modify = 'etc/peek/S79UG405init_modify'
path_to_tmp_temp_S79UG405init = 'temp/S79UG405init_from_host'
desired_line_in_path_to_S79UG405init_ishodniy = '/opt/bin/ug405/001Startup &'



path_to_S79UG405init_on_server = '/opt/rc.d/S79UG405init'
path_to_60_stcip_on_server = '/home/swarco/stcip/etc/init.d/60_stcip'

temp_path = 'temp/'
path_to_60_stcip_from_host_to_compare = 'temp/60_stcip_from_host'
path_to_saved_conflicts_txt = 'conflicts/'

path_to_img_swarco_inputs = 'images/inputs_swarco2.png'
path_to_img_swarco_bin_vals = 'images/degree_and_sf.png'

path_snmpget = r"toolkit\my_lib\SnmpGet.exe"
path_snmpset = r"toolkit\my_lib\SnmpSet.exe"


name_configuration = 'configuration'

name_command_swarco_ssh_for_log_greenroad = 'swarco ssh'
name_command_snmp_for_log_greenroad = 'snmp'

link_potok_reboot = 'system_reboot'

# green road
type_command_swarco_ssh = 'swarco ssh'
type_command_peek_web = 'peek web'
type_command_snmp = 'snmp'





def decrypt(filename, _key):
    f = Fernet(_key)
    with open(filename, 'rb') as file:
        encrypted_data = file.read()
    decrypted_data = f.decrypt(encrypted_data)
    return decrypted_data.decode('utf-8')

# with py7zr.SevenZipFile('configuration.7z', mode='r', password='pass1234') as z:
#
#     # print(z.extractall('temp/test_arch'))
#     with open(z.getnames()[0], 'r') as file:
#         data = file.read().splitlines()
#         print(data)
#     print(z.getnames())


def auth(flag=None):
    if flag is None:
        return
    try:
        data = decrypt(name_configuration, key).splitlines()

        if flag == 'snmp' and len(data) >= 11:
            return data[10], data[11]
        elif flag == 'ssh swarco l2' and len(data) >= 5:
            return data[3], data[4]
        elif flag == 'ssh swarco a':
            return data[2], data[5]
        elif flag == 'ssh swarco i' and len(data) >= 8:
            return data[1], data[7]
        elif flag == 'ssh swarco r' and len(data) >= 7:
            return data[0], data[6]
        elif flag == 'ssh peek' and len(data) >= 9:
            return data[0], data[8]
        elif flag == 'ftp peek p' and len(data) >= 13:
            return data[12], data[12]
        elif flag == 'net adimot' and len(data) >= 10:
            return data[9]
        else:
            print('Error read data from file')

    except FileNotFoundError as err:
        with open('log_start.txt', 'a', encoding='UTF-8') as file2:
            file2.write(f'Ошибка: Файл не найден {datetime.now().strftime("%H:%M:%S")}\n')


# print(auth('ssh swarco a'))
# print('configuration.py is called')


