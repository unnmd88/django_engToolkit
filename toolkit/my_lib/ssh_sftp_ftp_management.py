import sys
import time
import os
import platform
import socket
import filecmp
import paramiko
import sdp_func_lib
import configuration
from datetime import datetime
from scp import SCPClient, SCPException
from ftplib import FTP


class FuncLibSDP:

    @staticmethod
    def make_60stcip_S79UG405init(file_to_replace_windows_line_ending=None,
                                  name_finally_file='etc/swarco/60_stcip'):
        """Функция, создающая файл 60_stcip для загрузки на сервер
           path - путь к файлу, содержимое которого будет вставлено в файл 60_stcip, в зависимости от
           выбранной опции: либо из 60_stcip_modify ->  60_stcip либо 60_stcip_ishodniy -> 60_stcip
        """
        if file_to_replace_windows_line_ending is None:
            return
        elif file_to_replace_windows_line_ending == '60_stcip_ishodniy':
            path_to_file_from_get_content = 'etc/swarco/60_stcip_ishodniy'
        elif file_to_replace_windows_line_ending == '60_stcip_modify':
            path_to_file_from_get_content = 'etc/swarco/60_stcip_modify'
        else:
            path_to_file_from_get_content = file_to_replace_windows_line_ending

        FuncLibSDP.replace_windows_line_ending_to_unix_line_ending(path_to_file_from_get_content)

        with open(path_to_file_from_get_content, 'r') as file_from_get_content, \
                open(name_finally_file, 'w') as file_for_host:
            content = file_from_get_content.readlines()
            file_for_host.write(''.join(content))

        FuncLibSDP.replace_windows_line_ending_to_unix_line_ending(name_finally_file)

    @staticmethod
    def replace_windows_line_ending_to_unix_line_ending(path_to_file):
        """ Функция заменяет переводы строк CRLF(Windows) на  LF(Unix) в файле по пути: path_to_file """

        WINDOWS_LINE_ENDING = b'\r\n'
        UNIX_LINE_ENDING = b'\n'

        with open(path_to_file, 'rb') as file:
            content = file.read()
        content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

        with open(path_to_file, 'wb') as file:
            file.write(content)

    @staticmethod
    def get_data_from_list(path_to_user_file):
        with open(path_to_user_file, 'r', encoding='UTF-8') as file:
            data_list = []
            for line in file:
                data_list.append(line.strip().split(':'))
        return data_list


class ConnectionSSH:

    @staticmethod
    def create_ssh_session(ip_adress=None, access_level=None):

        if access_level is None:
            message = f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} < Программная ошибка аторизации >'
            return None, message

        try:
            data_auth = configuration.auth(access_level)
            # print(data_auth)
        except TypeError:
            data_auth = None
        except:
            return

        if data_auth is not None and len(data_auth) == 2:
            login, password = data_auth
            # print(f'login: {login}, password: {password}')
        else:
            message = f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} < Программная ошибка аторизации(нет данных' \
                      f' о логине и пароле >'
            return None, message

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


class SwarcoGetFile(ConnectionSSH):
    """ Класс предлагает возможность скачивание файлов с контроллера(пока реализовано только скачивание json)
        для дк Swarco
    """

    def __init__(self, ip_adress, path_to_file=configuration.path_to_60_stcip_on_server, flag=''):

        self.session_log = []
        self.ip_adress = ip_adress
        self.path_to_file = path_to_file
        self.flag = flag

        if flag == 'get json':
            self.get_json()

    def get_json(self):

        start_time_ssh = time.time()
        time_sleep_short = 0.4

        # Имя компьютера для шапки лога
        try:
            user_host_name = socket.gethostname()
        except:
            user_host_name = platform.node()

        if user_host_name is None:
            user_host_name = 'The name is not defined'

        # Формируем шапку лога сесии
        message = f'\n{"*" * 75}\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")}' \
                  f'\nИмя пользователя: {user_host_name}\nТип контроллера: Swarco\n' \
                  f'Адресс контроллера: {self.ip_adress}\n' \
                  f'Опция: Загрузить json swarco\n' \
                  f'\n< json {self.ip_adress} > :\n\n'
        self.session_log.append(message)

        try:
            os.mkdir(f'{self.ip_adress}_json')
        except FileExistsError:
            pass
        # client -> если подключение по ssh удалось, то вернётся client.connect, иначе None
        client, message = self.create_ssh_session(ip_adress=self.ip_adress, access_level='ssh swarco r')

        # Если client None, запишем соообщение message из self.create_ssh_session
        if client is None:
            self.session_log.append(message)
        # Если client не None(успешное подключение), скачиваем json и пишем в лог message
        else:
            try:
                scp = SCPClient(client.get_transport())
                scp.get('/home/swarco/stcip/etc/stcipd-config.json',
                        local_path=f'{self.ip_adress}_json', recursive=True)
            except SCPException as err:
                scp = SCPClient(client.get_transport())
                scp.get('/home/swarco/stcip/config/stcip-config.json',
                        local_path=f'{self.ip_adress}_json', recursive=True)
            time.sleep(time_sleep_short)
            if os.path.exists(f'{self.ip_adress}_json/stcipd-config.json'):
                with open(f'{self.ip_adress}_json/stcipd-config.json', 'r') as file:
                    lines = file.readlines()
                    lines = ''.join(lines)
                    message = lines
                self.session_log.append(message)
            # В прошивке 6.94.8 json расположен по другому пути и с другим названием
            elif os.path.exists(f'{self.ip_adress}_json/stcip-config.json'):
                with open(f'{self.ip_adress}_json/stcip-config.json', 'r') as file:
                    lines = file.readlines()
                    lines = ''.join(lines)
                    message = lines
                self.session_log.append(message)
        # Добавляем в self.session_log финальное сообщение
        message = f' Время сессии: {str(round(time.time() - start_time_ssh))} секунд\nКонец'
        self.session_log.append(f'\n\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} {message}')
        # Пишем в лог configuration.path_to_file_log_ssh_filter_snmp весь лог из self.session_log
        with open(configuration.path_to_file_log_ssh_filter_snmp, 'a') as file:
            for message in self.session_log:
                file.write(message)


class SwarcoFilterSnmp(ConnectionSSH):
    """ Класс предлагает возможность установки различных фильтров IPTABLES, а также
        запуск/перезапуск протокола STCIP с помощью rc-command через shell для дк Swarco
    """

    def __init__(self, flag_make_session=True, args='-', ip_adress_host='-',
                 net_adress_filtered_host='-', option_filter_snmp='-', controller_type='-'):

        self.session_log = []
        if isinstance(args, list):
            self.ip_adress_host, self.net_adress_filtered_host, self.controller_type, self.option_filter_snmp = args

        elif ip_adress_host != '-':
            self.ip_adress_host = ip_adress_host
            self.net_adress_filtered_host = net_adress_filtered_host
            self.option_filter_snmp = option_filter_snmp
            self.controller_type = controller_type

        if flag_make_session:
            self.make_ssh_filter_snmp_swarco()

    @staticmethod
    def send_commands_to_shell_swarco(ssh=None, option_filter_snmp=None, net_adress_filtered_host=None):

        short_sleep = 0.4
        long_sleep = 3
        recieve_bytes = 6000

        if net_adress_filtered_host == 'anywhere':
            net_adress_filtered_host = ''
        else:
            net_adress_filtered_host = f'-s {net_adress_filtered_host}'

        if (option_filter_snmp == 'Заблокировать управление по SNMP' or
                option_filter_snmp == 'Заблокировать управление по SNMP до перезагрузки'):
            commands_to_shell = ['uname -a \n', 'rm -r /etc/iptables/ \n', 'iptables -L \n', 'iptables -F \n',
                                 f'iptables -A INPUT -p udp --dport 161 {net_adress_filtered_host} -j DROP \n',
                                 f'iptables -A FORWARD -p udp --dport 161 {net_adress_filtered_host} -j DROP \n',
                                 'iptables -L \n',
                                 f'chmod 750 {configuration.path_to_60_stcip_on_server} \n', 'exit \n']
        elif option_filter_snmp == 'Разблокировать управление по SNMP':
            commands_to_shell = ['uname -a \n', 'rm -r /etc/iptables/ \n', 'iptables -L \n', 'iptables -F \n',
                                 'iptables -L \n',
                                 f'chmod 750 {configuration.path_to_60_stcip_on_server} \n', 'exit \n']
        elif option_filter_snmp == 'Start_STCIP(Swarco)':
            commands_to_shell = ['uname -a \n', 'rc-command start 60_stcip \n', 'exit \n']
        elif option_filter_snmp == 'Stop_STCIP(Swarco)':
            commands_to_shell = ['uname -a \n', 'rc-command stop 60_stcip \n', 'exit \n']
        elif option_filter_snmp == 'Restart_STCIP(Swarco)':
            commands_to_shell = ['uname -a \n', 'rc-command restart 60_stcip \n', 'exit \n']
        else:
            return '-'

        for command in commands_to_shell:
            ssh.send(command)
            if command != 'rc-command restart 60_stcip \n':
                time.sleep(short_sleep)
            else:
                time.sleep(long_sleep)
        message = ssh.recv(recieve_bytes).decode(encoding='utf-8')

        message = message.partition('~')[2]
        return message

    def make_ssh_filter_snmp_swarco(self):

        try:
            user_host_name = socket.gethostname()
        except:
            user_host_name = platform.node()

        if user_host_name is None:
            user_host_name = 'The name is not defined'

        message = f'\n{"*" * 75}\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")}' \
                  f'\nИмя пользователя: {user_host_name}\nТип контроллера: {self.controller_type}\n' \
                  f'Адресс контроллера: {self.ip_adress_host}\n' \
                  f'Опция: {self.option_filter_snmp}\nАдресс фильтра: {self.net_adress_filtered_host}\n'
        self.session_log.append(message)

        start_time_ssh = time.time()
        client, message = self.create_ssh_session(ip_adress=self.ip_adress_host, access_level='ssh swarco r')

        if client is None:
            self.session_log.append(message)
        else:
            with client.invoke_shell() as ssh:
                self.session_log.append(message)
                options_for_send_command_to_shell = ('Заблокировать управление по SNMP',
                                                     'Заблокировать управление по SNMP до перезагрузки',
                                                     'Разблокировать управление по SNMP', 'Start_STCIP(Swarco)',
                                                     'Stop_STCIP(Swarco)', 'Restart_STCIP(Swarco)')
                if self.option_filter_snmp in options_for_send_command_to_shell[:3]:
                    result, message = self.put_60_stcip_to_server(ssh=ssh, option_filter_snmp=self.option_filter_snmp)
                    if result:
                        message = self.send_commands_to_shell_swarco(ssh=ssh,
                                                                     option_filter_snmp=self.option_filter_snmp,
                                                                     net_adress_filtered_host=self.net_adress_filtered_host
                                                                     )
                        self.session_log.append(f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")}:\n{message}\n')
                    else:
                        self.session_log.append(f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")}:\n{message}\n')

                elif self.option_filter_snmp in options_for_send_command_to_shell[3:]:
                    message = self.send_commands_to_shell_swarco(ssh=ssh, option_filter_snmp=self.option_filter_snmp,
                                                                 net_adress_filtered_host=self.net_adress_filtered_host
                                                                 )
                    self.session_log.append(f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")}:\n{message}\n')

        # Запись в лог
        message = f' Время сессии: {str(round(time.time() - start_time_ssh))} секунд\nКонец'
        self.session_log.append(f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} {message}')
        with open(configuration.path_to_file_log_ssh_filter_snmp, 'a') as file:
            for message in self.session_log:
                file.write(message)

    def put_60_stcip_to_server(self, ssh=None, option_filter_snmp=None):

        if ssh is None or option_filter_snmp is None:
            return False
        temp_path = configuration.temp_path
        short_sleep = 0.4

        if option_filter_snmp == 'Заблокировать управление по SNMP':
            path_to_60_stcip_xx = configuration.path_to_60_stcip_modify
        elif option_filter_snmp == 'Заблокировать управление по SNMP до перезагрузки':
            path_to_60_stcip_xx = configuration.path_to_60_stcip_ishodniy
        elif option_filter_snmp == 'Разблокировать управление по SNMP':
            path_to_60_stcip_xx = configuration.path_to_60_stcip_ishodniy
        else:
            return

        if os.path.exists(f'{temp_path}60_stcip_from_server'):
            os.remove(f'{temp_path}60_stcip_from_server')
        # Изготавливаем 60stcip для загрузки на контроллер
        sdp_func_lib.make_60stcip(file_to_replace_windows_line_ending=path_to_60_stcip_xx)

        scp = SCPClient(ssh.get_transport())
        for attempt in range(3):
            flag_put, flag_get, flag_rename, flag_compare_files = False, False, False, False
            if attempt == 2:
                message = '< Произошел сбой при загрузке файла с сервера >\nКонец\n'
                return False, message
            try:
                # Загружаем 60stcip на котроллер
                scp.put(configuration.path_to_60_stcip,
                        recursive=True, remote_path='/home/swarco/stcip/etc/init.d/')
                flag_put = True
            except:
                continue

            time.sleep(short_sleep)

            # Скачиваем с дк загруженный ранее 60stcip(для последующей проверки)
            scp.get('/home/swarco/stcip/etc/init.d/60_stcip', temp_path)
            time.sleep(short_sleep)

            # Проверяем скачался ли 60stcip
            if not os.path.exists(f'{temp_path}60_stcip'):
                continue
            else:
                flag_get = True
            # Переименовываем  скачанный 60stcip на 60_stcip_from_server
            try:
                os.rename(f'{temp_path}60_stcip', f'{temp_path}60_stcip_from_server')
                flag_rename = True
                time.sleep(short_sleep)
            except:
                continue
            # Сравниваем 2 файла: etc/swarco/60_stcip с temp/60_stcip_from_server.
            # Если они равны, считаем загрузу успешной
            if filecmp.cmp(configuration.path_to_60_stcip, f'{temp_path}60_stcip_from_server'):
                flag_compare_files = True
            else:
                continue

            if flag_put and flag_get and flag_rename and flag_compare_files:
                message = f'< Конфигурация iptables успешно изменена >\n'
                return True, message


class SwarcoWorkStationManagement(ConnectionSSH):
    """ Класс предлагает возможность установки различных параметров(inp,softinp, M-reg, outp)
        через shell для дк Swarco
    """

    def __init__(self, flag_make_session=True, args='-', ip_adress='-', inp102='-', inp_102_val='-', type_command='-',
                 num_digitInp_softInp_Mreg_Out='-', val_digitInp_softInp_Mreg_Out='-'):

        self.session_log = []

        if isinstance(args, list):
            self.ip_adress, self.inp102, self.inp_102_val, self.type_command, \
                self.num_digitInp_softInp_Mreg_Out, self.val_digitInp_softInp_Mreg_Out = args
            self.num_digitInp_softInp_Mreg_Out = self.num_digitInp_softInp_Mreg_Out.split('(')[0]
        elif ip_adress != '-':
            self.ip_adress = ip_adress
            self.inp102 = inp102
            self.inp_102_val = inp_102_val
            self.type_command = type_command
            self.num_digitInp_softInp_Mreg_Out = num_digitInp_softInp_Mreg_Out.split('(')[0]
            self.val_digitInp_softInp_Mreg_Out = val_digitInp_softInp_Mreg_Out
        else:
            return
            # Запись в лог и return

        if flag_make_session:
            self.make_ssh_inp_outp_Mreg()

    def make_ssh_inp_outp_Mreg(self):
        """" Функция открывает ssh соединение и отправлят в shell сообщения.
             args -> list с параметрами вида: [ip_adress, inp102, inp_102_val, type_command,
             num_digitInp_softInp_Mreg_Out,val_digitInp_softInp_Mreg_Out]
             inp102 -> если == INPUT 102(РУ) сохраняем команду в list ssh_commands со значением = inp_102_val
             доступные type_command:
                                     Физический вход
                                     Софт вход
                                     M-регистр
                                     Физический выход
             num_digitInp_softInp_Mreg_Out -> номер входа/выхода/M-регистра
             val_digitInp_softInp_Mreg_Out -> значение входа/выхода/M-регистра
             Если type_command из доступных, то сохраняем команду в list ssh_commands с номером входа/выхода/M-регистра
             num_digitInp_softInp_Mreg_Out и значением = val_digitInp_softInp_Mreg_Out
             Если list ssh_commands не пустой - циклом for отправляем команды в shell
        """

        ip_adress, inp102, inp_102_val, type_command, num_digitInp_softInp_Mreg_Out, \
            val_digitInp_softInp_Mreg_Out = self.ip_adress, self.inp102, self.inp_102_val, self.type_command, \
            self.num_digitInp_softInp_Mreg_Out, self.val_digitInp_softInp_Mreg_Out

        # Лог
        message = f'\n{"*" * 75}\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")}' \
                  f'\nАдресс контроллера: {ip_adress}\n' \
                  f'Вход 102(РУ): {inp_102_val}\n' \
                  f'{type_command} номер: {num_digitInp_softInp_Mreg_Out}, ' \
                  f'Значение: {val_digitInp_softInp_Mreg_Out}\n'
        self.session_log.append(message)

        ssh_commands = []
        # Проверяем inp102 значение. Если не '-' -> добавляем в ssh_commands
        if inp102 != '-' and inp_102_val != '-':
            ssh_commands.append(f'inp102={inp_102_val}\n', )
            ssh_commands.append('inp102 ?\n')
        # Проверяем Тип команды и номер входа/выхода/М-регистра. Если не '-' -> добавляем в ssh_commands
        if type_command != '-' and num_digitInp_softInp_Mreg_Out != '-':
            if type_command == 'Физический вход':
                ssh_commands.append(f'inp{num_digitInp_softInp_Mreg_Out}={val_digitInp_softInp_Mreg_Out}\n')
                ssh_commands.append(f'inp{num_digitInp_softInp_Mreg_Out} ?\n')
            elif type_command == 'Софт вход':
                ssh_commands.append(f'ws3 {num_digitInp_softInp_Mreg_Out} {val_digitInp_softInp_Mreg_Out}\n')
                ssh_commands.append(f'softstat{num_digitInp_softInp_Mreg_Out} ?\n')
            elif type_command == 'M-регистр':
                ssh_commands.append(f'ws4 {num_digitInp_softInp_Mreg_Out} {val_digitInp_softInp_Mreg_Out}\n')
                ssh_commands.append(f'cbmem{num_digitInp_softInp_Mreg_Out} ?\n')
            elif type_command == 'Физический выход':
                ssh_commands.append(f'outp{num_digitInp_softInp_Mreg_Out}={val_digitInp_softInp_Mreg_Out}\n')
                ssh_commands.append(f'outp{num_digitInp_softInp_Mreg_Out} ?\n')

        # Если список команд не пустой - начнаем ssh сессию
        if ssh_commands:
            ssh_commands.append('exit\n')
            start_time_ssh = time.time()
            short_sleep = 0.4
            bytes_recv = 6000

            try:
                login, password = configuration.auth('ssh swarco l2')
            except TypeError:
                return
            except:
                sys.exit()

            client, message = self.create_ssh_session(ip_adress=ip_adress, access_level='ssh swarco i', )

            if client is None:
                self.session_log.append(message)
            else:
                ssh_commands = ['lang UK\n', f'{login}\n', f'{password}\n'] + ssh_commands

                with client.invoke_shell() as ssh:
                    for command in ssh_commands:
                        ssh.send(command)
                        time.sleep(short_sleep)

                    msg_from_shell = ssh.recv(bytes_recv).decode(encoding="latin-1")
                    message = f'\n{msg_from_shell}\n'
                    self.session_log.append(message)
            session_time = f'\nSession time: {str(round(time.time() - start_time_ssh))} second\nEnd'
            self.session_log.append(session_time)

            # Записываем лог сессии
            with open(configuration.path_to_file_log_ssh_set_inp_outp_Mreg, 'a') as file:
                file.write(self.session_log[0])
            try:
                with open(configuration.path_to_file_log_ssh_set_inp_outp_Mreg, 'a', encoding="latin-1") as file:
                    for message in self.session_log[1:]:
                        file.write(message)
            except UnicodeEncodeError as err:
                with open(configuration.path_to_file_log_ssh_set_inp_outp_Mreg, 'a') as file:
                    for message in self.session_log[1:]:
                        file.write(message)


class PeekFilterSnmp(ConnectionSSH):
    """ Класс предлагает возможность установки различных фильтров IPTABLES через shell для дк Peek """

    def __init__(self, flag_make_session=True, args='-', ip_adress_host='-',
                 net_adress_filtered_host='-', option_filter_snmp='-', controller_type='-'):

        self.session_log = []
        if isinstance(args, list):
            self.ip_adress_host, self.net_adress_filtered_host, self.controller_type, self.option_filter_snmp = args

        elif ip_adress_host != '-':
            self.ip_adress_host = ip_adress_host
            self.net_adress_filtered_host = net_adress_filtered_host
            self.option_filter_snmp = option_filter_snmp
            self.controller_type = controller_type

        if flag_make_session:
            self.make_ssh_filter_snmp_peek()

    @staticmethod
    def send_commands_to_shell_peek(ssh=None, option_filter_snmp=None, net_adress_filtered_host=None):

        short_sleep = 0.6
        recieve_bytes = 6000

        if net_adress_filtered_host == 'anywhere':
            net_adress_filtered_host = ''
        else:
            net_adress_filtered_host = f'-s {net_adress_filtered_host}'

        if (option_filter_snmp == 'Заблокировать управление по SNMP' or
                option_filter_snmp == 'Заблокировать управление по SNMP до перезагрузки'):
            commands_to_shell = ['uname -a \n', 'iptables -L \n', 'iptables -F \n',
                                 f'iptables -A INPUT -p udp --dport 161 {net_adress_filtered_host} -j DROP \n',
                                 f'iptables -A FORWARD -p udp --dport 161 {net_adress_filtered_host} -j DROP \n',
                                 'iptables -L \n',
                                 f'chmod 755 {configuration.path_to_S79UG405init_on_server} \n', 'exit \n']
        elif option_filter_snmp == 'Разблокировать управление по SNMP':
            commands_to_shell = ['uname -a \n', 'iptables -L \n', 'iptables -F \n', 'iptables -L \n',
                                 f'chmod 755 {configuration.path_to_S79UG405init_on_server} \n' 'exit \n']
        else:
            return '-'

        for command in commands_to_shell:
            ssh.send(command)
            time.sleep(short_sleep)
        message = ssh.recv(recieve_bytes).decode(encoding='utf-8')
        message = message.partition('uname -a')[2]
        return message

    def put_S79UG405init_to_server(self, ip_adress_host=None, option_filter_snmp=None):

        temp_path = configuration.temp_path

        if option_filter_snmp == 'Заблокировать управление по SNMP':
            write_iptables_to_S79UG405init = True
        elif option_filter_snmp == 'Заблокировать управление по SNMP до перезагрузки':
            write_iptables_to_S79UG405init = False
        elif option_filter_snmp == 'Разблокировать управление по SNMP':
            write_iptables_to_S79UG405init = False
        else:
            return

        if os.path.exists(f'{temp_path}S79UG405init_from_server'):
            os.remove(f'{temp_path}S79UG405init_from_server')

        try:
            login, password = configuration.auth('ftp peek p')
        except TypeError:
            return
        except:
            sys.exit()

        # Создание каталога etc/peek/"ip хоста"_S79UG405init/from_server
        if not os.path.exists(f'{configuration.path_to_etc_peek}{ip_adress_host}_S79UG405init/'):
            os.mkdir(f'{configuration.path_to_etc_peek}{ip_adress_host}_S79UG405init/')
            os.mkdir(f'{configuration.path_to_etc_peek}{ip_adress_host}_S79UG405init/from_server')

        try:
            with FTP(ip_adress_host, timeout=5) as ftp_session:
                comm_msg = '\n< Начинаю загрузку файла конфигурации на сервер >:'
                msg_ftp_session_getwelcome = ftp_session.getwelcome()
                msg_ftp_session_login = ftp_session.login(login, password)
                ftp_session.cwd('rc.d')

                # загружаем с дк S79UG405init в etc/peek/"ip хоста"_S79UG405init/from_server
                with open(f'{configuration.path_to_etc_peek}{ip_adress_host}_S79UG405init/from_server/S79UG405init',
                          'wb') as get_file:
                    msg_ftp_session_get = ftp_session.retrbinary(f'RETR S79UG405init', get_file.write)

                # Если произошла ошибка при загрузке S79UG405init с контроллера
                if msg_ftp_session_get != '226 Transfer complete.':
                    message = f' {comm_msg}' \
                              f'\n{msg_ftp_session_getwelcome}\n{msg_ftp_session_login}\n{msg_ftp_session_get}' \
                              f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} < Ошибка передачи файла >\nКонец'
                    # sdp_func_lib.logger(path_to_file_log=configuration.path_to_file_log_ssh_filter_snmp,
                    #                     flag='new_standart', message=message)
                    result = False
                    self.session_log.append(message)

                # Изготавливаем S79UG405init для загрузки на контроллер
                sdp_func_lib.make_S79UG405init(self.net_adress_filtered_host,
                                               write_iptables_to_S79UG405init=write_iptables_to_S79UG405init,
                                               path=f'{configuration.path_to_etc_peek}{ip_adress_host}_S79UG405init')
                # Загружаем изготовленный S79UG405init на дк
                with open(f'{configuration.path_to_etc_peek}{ip_adress_host}_S79UG405init/S79UG405init', 'rb') as file_to_put:
                    msg_ftp_session_put = ftp_session.storbinary(
                        f'STOR {configuration.path_to_etc_peek}{ip_adress_host}_S79UG405init/S79UG405init', file_to_put)
                    if msg_ftp_session_put == '226 Transfer complete.':
                        msg_reult = '< Файл новой конфигурации успешно загружен на сервер >\n'

                # загружаем еще раз с дк S79UG405init в /temp для того, чтобы сравнить с тем файлом, что мы изготовили.
                # Если они равны, то значит загрузка произведена успешено
                with open(configuration.path_to_tmp_temp_S79UG405init, 'wb') as file_to_get:
                    ftp_session.retrbinary(f'RETR S79UG405init', file_to_get.write)

                if (filecmp.cmp(f'{configuration.path_to_etc_peek}{ip_adress_host}_S79UG405init/S79UG405init',
                                configuration.path_to_tmp_temp_S79UG405init) and
                        msg_ftp_session_put == '226 Transfer complete.'):
                    message = f' {comm_msg}\n{msg_ftp_session_login}' \
                              f'\n{msg_ftp_session_login}\n{msg_ftp_session_put}' \
                              f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} {msg_reult}'

                    # sdp_func_lib.logger(path_to_file_log=configuration.path_to_file_log_ssh_filter_snmp,
                    #                     flag='new_standart', message=message)
                    result = True
                else:
                    message = f' {comm_msg}\n{msg_ftp_session_getwelcome}' \
                              f'\n{msg_ftp_session_login}\n{msg_ftp_session_get}\n{msg_ftp_session_put}' \
                              f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} < Ошибка передачи файла >\nКонец'
                    # sdp_func_lib.logger(path_to_file_log=configuration.path_to_file_log_ssh_filter_snmp,
                    #                     flag='new_standart', message=message)
                    result = False

                self.session_log.append(message)

                try:
                    os.remove(configuration.path_to_tmp_temp_S79UG405init)
                except FileNotFoundError:
                    pass
                ftp_session.close()
                return result
        except TimeoutError:
            message = f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} < Ошибка подключения. Хост недоступен >\nКонец'

            # sdp_func_lib.logger(path_to_file_log=configuration.path_to_file_log_ssh_filter_snmp,
            #                     flag='new_standart', message=message)
            self.session_log.append(message)
            return False

    def make_ssh_filter_snmp_peek(self):

        self.start_time_ssh = time.time()

        try:
            user_host_name = socket.gethostname()
        except:
            user_host_name = platform.node()

        if user_host_name is None:
            user_host_name = 'The name is not defined'

        # Запись в лог
        message = f'\n{"*" * 75}\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")}' \
                  f'\nИмя пользователя: {user_host_name}\nТип контроллера: {self.controller_type}\n' \
                  f'Адресс контроллера: {self.ip_adress_host}\n' \
                  f'Опция: {self.option_filter_snmp}\nАдресс фильтра: {self.net_adress_filtered_host}\n'
        self.session_log.append(message)

        res_put_S79UG405init_to_server = self.put_S79UG405init_to_server(ip_adress_host=self.ip_adress_host,
                                                                         option_filter_snmp=self.option_filter_snmp)

        if res_put_S79UG405init_to_server:
            pass
        else:
            self.write_log_to_file()
            return

        client, message = self.create_ssh_session(ip_adress=self.ip_adress_host, access_level='ssh peek', )

        if client is None:
            self.write_log_to_file()
            return

        with client.invoke_shell() as ssh:
            self.session_log.append(message)
            message = self.send_commands_to_shell_peek(ssh=ssh, option_filter_snmp=self.option_filter_snmp,
                                                       net_adress_filtered_host=self.net_adress_filtered_host,
                                                       )
            self.session_log.append(message)

        self.write_log_to_file()

    def write_log_to_file(self):
        message = f' Время сессии: {str(round(time.time() - self.start_time_ssh))} секунд\nКонец'
        self.session_log.append(f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} {message}')
        with open(configuration.path_to_file_log_ssh_filter_snmp, 'a') as file:
            for message in self.session_log:
                file.write(message)


class CommandsToShell(ConnectionSSH):
    def __init__(self, ip_adress=None, controller_type=None, commands=None, access_level=None,
                 flag_commands_to_shell=False, flag_commands_swarco_ws=False,
                 flag_reset_inp104_111=False, write_log=False):

        self.ip_adress = ip_adress
        self.controller_type = controller_type
        self.commands = commands
        self.access_level = access_level
        self.flag_write_to_log = write_log
        self.flag_reset_inp102_111 = flag_reset_inp104_111

        self.session_log = []


        if flag_commands_to_shell:
            self.common_commands_to_shell()
        elif flag_commands_swarco_ws:
            self.commands_to_shell_swarco_WS()


    def common_commands_to_shell(self):

        if self.ip_adress is None or self.controller_type is None or self.commands is None:
            return

        ip_adress, controller_type, commands, = self.ip_adress, self.controller_type, self.commands,

        flag_reboot = False
        short_sleep = 0.4
        long_sleep = 5
        recieve_bytes = 6000

        if commands[0] == 'reboot \n':
            flag_reboot = True

        if len(commands) == 1 and commands[0] == 'reboot \n':
            if controller_type == configuration.type_controller_swarco:
                self.access_level = 'ssh swarco a'
            elif controller_type == configuration.type_controller_peek:
                self.access_level = 'ssh peek'

        access_level = self.access_level

        if controller_type == configuration.type_controller_swarco:
            client, message = self.create_ssh_session(ip_adress=ip_adress, access_level=access_level)
        elif controller_type == configuration.type_controller_peek:
            client, message = self.create_ssh_session(ip_adress=ip_adress, access_level=access_level)
        else:
            return

        try:
            with client.invoke_shell() as ssh:
                for command in commands:
                    ssh.send(command)
                    if flag_reboot:
                        time.sleep(long_sleep)
                    else:
                        time.sleep(short_sleep)
        except:
            pass


    def commands_to_shell_swarco_WS(self):

        start_time = time.time()

        if not self.flag_reset_inp102_111 and self.commands is None:
            return
        elif self.flag_reset_inp102_111 and self.commands is None:
            self.commands = []

        if self.ip_adress is None or self.controller_type is None:
            return
        ip_adress, controller_type, commands, = self.ip_adress, self.controller_type, self.commands

        if self.flag_write_to_log:
            message = f'\n{"*" * 75}\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")}' \
                      f'{"-" * 15} Зелёная улица {"-" * 15}' \
                      f'\nАдресс контроллера: {ip_adress}\n'
            self.session_log.append(message)

        short_sleep = 0.4
        long_sleep = 5
        recieve_bytes = 6000

        access_level = 'ssh swarco i'
        client, message = self.create_ssh_session(ip_adress=ip_adress, access_level=access_level)

        login, password = configuration.auth('ssh swarco l2')
        if self.flag_reset_inp102_111:
            commands = ['lang UK', f'{login}', f'{password}'] + [f'inp{inp}=0' for inp in range(104, 112)] + commands
        else:
            commands = ['lang UK', f'{login}', f'{password}'] + commands

        try:
            with client.invoke_shell() as ssh:
                for command in commands:
                    ssh.send(f'{command}\n')
                    time.sleep(short_sleep)
                msg_from_shell = ssh.recv(recieve_bytes).decode(encoding="latin-1")
            if self.flag_write_to_log:
                self.session_log.append(msg_from_shell)
                session_time = f'\nSession time: {str(round(time.time() - start_time))} second\nEnd'
                self.session_log.append(session_time)
            # print('self.session_log:')
            # print(self.session_log)
        except:
            pass

        if self.flag_write_to_log:
            with open(configuration.path_to_file_greenroad_log, 'a') as file:
                file.write(self.session_log[0])
            try:
                with open(configuration.path_to_file_greenroad_log, 'a', encoding="latin-1") as file:
                    for message in self.session_log[1:]:
                        file.write(message)
            except UnicodeEncodeError as err:
                with open(configuration.path_to_file_greenroad_log, 'a') as file:
                    for message in self.session_log[1:]:
                        file.write(message)


    def commands_to_shell_swarco_new_greenroad_WS(self):

        start_time = time.time()

        if self.ip_adress is None or self.controller_type is None or self.commands is None:
            return
        ip_adress, controller_type, commands, = self.ip_adress, self.controller_type, self.commands

        if self.flag_write_to_log:
            message = f'\n{"*" * 75}\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")}' \
                      f'{"-" * 15} Зелёная улица {"-" * 15}' \
                      f'\nАдресс контроллера: {ip_adress}\n'
            self.session_log.append(message)

        short_sleep = 0.4
        recieve_bytes = 6000

        access_level = 'ssh swarco i'
        client, message = self.create_ssh_session(ip_adress=ip_adress, access_level=access_level)

        login, password = configuration.auth('ssh swarco l2')
        commands = ['lang UK', f'{login}', f'{password}', 'inp104=0', 'inp105=0', 'inp106=0', 'inp107=0',
                    'inp108=0'] + commands
        try:
            with client.invoke_shell() as ssh:
                for command in commands:
                    ssh.send(f'{command}\n')
                    time.sleep(short_sleep)
                msg_from_shell = ssh.recv(recieve_bytes).decode(encoding="latin-1")
            if self.flag_write_to_log:
                self.session_log.append(msg_from_shell)
                session_time = f'\nSession time: {str(round(time.time() - start_time))} second\nEnd'
                self.session_log.append(session_time)
            # print('self.session_log:')
            # print(self.session_log)
        except:
            pass

        if self.flag_write_to_log:
            with open(configuration.path_to_file_greenroad_log, 'a') as file:
                file.write(self.session_log[0])
            try:
                with open(configuration.path_to_file_greenroad_log, 'a', encoding="latin-1") as file:
                    for message in self.session_log[1:]:
                        file.write(message)
            except UnicodeEncodeError as err:
                with open(configuration.path_to_file_greenroad_log, 'a') as file:
                    for message in self.session_log[1:]:
                        file.write(message)


class CommandsToShellSwarco(ConnectionSSH):
    def __init__(self, ip_adress=None, write_log=False):

        self.ip_adress = ip_adress
        self.flag_write_to_log = write_log
        self.session_log = []

    def commands_to_workstation(self, commands, flag_reset_inp102_111=False):

        start_time = time.time()

        if self.flag_write_to_log:
            message = f'\n{"*" * 75}\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")}' \
                      f'{"-" * 15} Зелёная улица {"-" * 15}' \
                      f'\nАдресс контроллера: {self.ip_adress}\n'
            self.session_log.append(message)

        short_sleep = 0.4
        long_sleep = 5
        recieve_bytes = 6000

        access_level = 'ssh swarco i'
        client, message = self.create_ssh_session(ip_adress=self.ip_adress, access_level=access_level)

        login, password = configuration.auth('ssh swarco l2')
        if flag_reset_inp102_111:
            commands = ['lang UK', f'{login}', f'{password}'] + [f'inp{inp}=0' for inp in range(104, 112)] + commands
        else:
            commands = ['lang UK', f'{login}', f'{password}'] + commands

        try:
            with client.invoke_shell() as ssh:
                for command in commands:
                    ssh.send(f'{command}\n')
                    time.sleep(short_sleep)
                msg_from_shell = ssh.recv(recieve_bytes).decode(encoding="latin-1")
            if self.flag_write_to_log:
                self.session_log.append(msg_from_shell)
                session_time = f'\nSession time: {str(round(time.time() - start_time))} second\nEnd'
                self.session_log.append(session_time)
            # print('self.session_log:')
            # print(self.session_log)
        except:
            pass

        if self.flag_write_to_log:
            with open(configuration.path_to_file_greenroad_log, 'a') as file:
                file.write(self.session_log[0])
            try:
                with open(configuration.path_to_file_greenroad_log, 'a', encoding="latin-1") as file:
                    for message in self.session_log[1:]:
                        file.write(message)
            except UnicodeEncodeError as err:
                with open(configuration.path_to_file_greenroad_log, 'a') as file:
                    for message in self.session_log[1:]:
                        file.write(message)

    def commands_to_shell(self):
        pass