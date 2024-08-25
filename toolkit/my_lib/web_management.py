import time
import datetime
import keyboard

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException

import sdp_func_lib
import configuration


class PeekWeb:
    MAN_INPUTS = {'MPP_MAN', 'MPP_FL', 'MPP_OFF', 'MPP_PH1', 'MPP_PH2', 'MPP_PH3',
                  'MPP_PH4', 'MPP_PH5', 'MPP_PH6', 'MPP_PH7', 'MPP_PH8'}

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


    def __init__(self, ip_adress):
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
    def _make_inputs_and_user_parameters(inputs=None, user_parameters=None, ):
        flag_to_reset_curr_act_inputs = False
        if inputs:
            inputs = (i.split('=') for i in inputs)
            inputs = {i[0]: i[1] for i in inputs}
            flag_to_reset_curr_act_inputs = True if 'MPP_MAN' and 'MPP_PH' in inputs else False
        if user_parameters:
            user_parameters = (i.split('=') for i in user_parameters)
            user_parameters = {i[0]: i[1] for i in user_parameters}
        return inputs, flag_to_reset_curr_act_inputs, user_parameters

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
        print(main_page)
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
        print('start click_to_inp_and_actuator')
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
        time.sleep(self.short_pause)
        print('final; click_to_inp_and_actuator')

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
        element_input = self.driver.find_element(By.XPATH,  buttons.get('OK'))
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

    def session_manager(self, increase_the_timeout=False, set_stage_MAN=False,
                        inputs=None, user_parameters=None,):
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

        if increase_the_timeout:
            self.short_pause += 1
            self.middle_pause += 2
            self.long_pause += 2


        inputs, flag_set_stage_by_MAN_or_reset_mMAN, user_parameters = \
            PeekWeb._make_inputs_and_user_parameters(inputs, user_parameters)
        print(f'inputs = {inputs}, user_parameters = {user_parameters},')

        ##############################################################

        # Боевой вариант
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=options)
        driver.get('http://' + self.ip_adress)

        # Тест вариант
        self.driver = webdriver.Chrome()
        self.driver.get('http://localhost/')
        time.sleep(self.short_pause)
        self.driver.get('http://localhost' + '/hvi?file=dummy.hvi&uic=3333')
        time.sleep(self.short_pause)
        self.driver.get('http://localhost/')
        time.sleep(self.middle_pause)

        span_inputs, span_user_parameters = self._detect_span_inputs_and_user_parameterts()
        time.sleep(self.middle_pause)

        if inputs:
            self.driver.refresh()
            time.sleep(self.short_pause)
            self._goto_content_frame(span_inputs)
            table_INPUTS = self.driver.find_element(By.TAG_NAME, 'table')
            table_INPUT_elements = table_INPUTS.find_elements(By.TAG_NAME, 'tr')

            print(inputs)
            print('----!!!!--------')
            cnt, len_inputs = 0, len(inputs)
            for row in [el.text.split() for el in table_INPUT_elements]:
                if len(row) == 5:
                    num, name, state, time_state, actuator_val = row
                else:
                    continue
                print(f'num: {num}, name: {name},state: {state},time_state: {time_state},actuator_val: {actuator_val}')
                if name not in inputs and set_stage_MAN and name in self.MAN_INPUTS:
                    if state == '1' and actuator_val != 'ВЫКЛ':
                        self._set_INPUTS(num, 'ВЫКЛ')
                    elif state == '0' and actuator_val != 'ВКЛ':
                        self._set_INPUTS(num, 'ВФ')
                elif name in inputs:
                    val_actuator_to_set = inputs.get(name)
                    val_actuator_to_curr = 'ВФ' if actuator_val == '-' else actuator_val
                    if val_actuator_to_set != val_actuator_to_curr:
                        self._set_INPUTS(num, inputs.get(name))
                        cnt += 1
                if cnt >= len_inputs:
                    print(f'if cnt >= len_inputs:')
                    break
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

class PotokWeb:
    def __init__(self, ip_adress, flag=None):
        self.ip_adress = ip_adress

        if flag == 'reboot':
            self.restart_controller_potok_webdriver()

    def restart_controller_potok_webdriver(self):

        if not sdp_func_lib.check_host_tcp(self.ip_adress):
            return

        driver = webdriver.Chrome()

        try:
            # Открыть браузер Chrome
            driver.get(f'https://{self.ip_adress}')

            button_dopolnitelnie = '/html/body/div/div[2]/button[3]'
            link_go_to_site = '//*[@id="proceed-link"]'
            login = '//*[@id="login"]'
            password = '//*[@id="password"]'
            button_login = '/html/body/div[2]/div/div/form/button'
            # button_restart_programm = '/html/body/div[3]/div/div/form/div[11]/div/button'
            # radio_button_fix = '/html/body/div[3]/div/div/form/div[12]/div/label[1]'
            # radio_button_adaptiva = '/html/body/div[3]/div/div/form/div[12]/div/label[2]'
            # button_change_mode = '/html/body/div[3]/div/div/form/div[13]/div/button'

            time.sleep(1)
            # Клик в "Дополнительно"(небезопасый сайт)
            element_input = driver.find_element(By.XPATH, button_dopolnitelnie)
            element_input.click()
            time.sleep(1)
            # Клик в перейти на сайт
            element_input = driver.find_element(By.XPATH, link_go_to_site)
            element_input.click()
            time.sleep(1)
            # Ввод логина и пароля
            element_input = driver.find_element(By.XPATH, login)
            element_input.send_keys('admin')
            element_input = driver.find_element(By.XPATH, password)
            element_input.send_keys('zBCTRuV7')
            # Клик на кнопку Войти
            element_input = driver.find_element(By.XPATH, button_login)
            element_input.click()
            time.sleep(1)

            driver.get(f'https://{self.ip_adress}/system_reboot')
        except:
            pass

        #     # Клик на кнопку Перезапуск программы
        #     if action == "Перезапуск программы":
        #         element_input = driver.find_element(By.XPATH, button_restart_programm)
        #         element_input.click()
        #         keyboard.send("enter")
        #     # Клик на radiobutton Фиксированный:
        #     elif action == "Фикс":
        #         element_input = driver.find_element(By.XPATH, radio_button_fix)
        #         element_input.click()
        #         time.sleep(1)
        #         element_input = driver.find_element(By.XPATH, button_change_mode)
        #         element_input.click()
        #     # Клик на radiobutton Адаптивный:
        #     elif action == "Адаптива":
        #         element_input = driver.find_element(By.XPATH, radio_button_adaptiva)
        #         element_input.click()
        #         time.sleep(1)
        #         element_input = driver.find_element(By.XPATH, button_change_mode)
        #         element_input.click()
        #     # Перезапуск ОС контроллера:
        #     elif action == "Перезапуск ОС":
        #         driver.get('https://' + ip_adress + '/system_reboot')
        #
        #
        #     time.sleep(4)
        #
        # except Exception as ex:
        #     pass
        # finally:
        #     # driver.close()
        #     driver.quit()


def restart_programm_potok_webdriver(ip_adress: str, action: str):
    if not sdp_func_lib.check_host_tcp(ip_adress):
        return

    driver = webdriver.Chrome()

    try:
        # Открыть браузер Chrome
        driver.get('https://' + ip_adress)

        button_dopolnitelnie = '/html/body/div/div[2]/button[3]'
        link_go_to_site = '//*[@id="proceed-link"]'
        login = '//*[@id="login"]'
        password = '//*[@id="password"]'
        button_login = '/html/body/div[2]/div/div/form/button'
        button_restart_programm = '/html/body/div[3]/div/div/form/div[11]/div/button'
        radio_button_fix = '/html/body/div[3]/div/div/form/div[12]/div/label[1]'
        radio_button_adaptiva = '/html/body/div[3]/div/div/form/div[12]/div/label[2]'
        button_change_mode = '/html/body/div[3]/div/div/form/div[13]/div/button'

        time.sleep(1)
        # Клик в "Дополнительно"(небезопасый сайт)
        element_input = driver.find_element(By.XPATH, button_dopolnitelnie)
        element_input.click()
        time.sleep(1)
        # Клик в перейти на сайт
        element_input = driver.find_element(By.XPATH, link_go_to_site)
        element_input.click()
        time.sleep(1)
        # Ввод логина и пароля
        element_input = driver.find_element(By.XPATH, login)
        element_input.send_keys('admin')
        element_input = driver.find_element(By.XPATH, password)
        element_input.send_keys('zBCTRuV7')
        # Клик на кнопку Войти
        element_input = driver.find_element(By.XPATH, button_login)
        element_input.click()
        time.sleep(1)

        # Клик на кнопку Перезапуск программы
        if action == "Перезапуск программы":
            element_input = driver.find_element(By.XPATH, button_restart_programm)
            element_input.click()
            keyboard.send("enter")
        # Клик на radiobutton Фиксированный:
        elif action == "Фикс":
            element_input = driver.find_element(By.XPATH, radio_button_fix)
            element_input.click()
            time.sleep(1)
            element_input = driver.find_element(By.XPATH, button_change_mode)
            element_input.click()
        # Клик на radiobutton Адаптивный:
        elif action == "Адаптива":
            element_input = driver.find_element(By.XPATH, radio_button_adaptiva)
            element_input.click()
            time.sleep(1)
            element_input = driver.find_element(By.XPATH, button_change_mode)
            element_input.click()
        # Перезапуск ОС контроллера:
        elif action == "Перезапуск ОС":
            driver.get('https://' + ip_adress + '/system_reboot')

        time.sleep(4)

    except Exception as ex:
        pass
    finally:
        # driver.close()
        driver.quit()


def restart_controller_potok_webdriver(ip_adress: str):
    if not sdp_func_lib.check_host_tcp(ip_adress):
        return

    driver = webdriver.Chrome()

    try:
        # Открыть браузер Chrome
        driver.get(f'https://{ip_adress}')

        button_dopolnitelnie = '/html/body/div/div[2]/button[3]'
        link_go_to_site = '//*[@id="proceed-link"]'
        login = '//*[@id="login"]'
        password = '//*[@id="password"]'
        button_login = '/html/body/div[2]/div/div/form/button'
        # button_restart_programm = '/html/body/div[3]/div/div/form/div[11]/div/button'
        # radio_button_fix = '/html/body/div[3]/div/div/form/div[12]/div/label[1]'
        # radio_button_adaptiva = '/html/body/div[3]/div/div/form/div[12]/div/label[2]'
        # button_change_mode = '/html/body/div[3]/div/div/form/div[13]/div/button'

        time.sleep(1)
        # Клик в "Дополнительно"(небезопасый сайт)
        element_input = driver.find_element(By.XPATH, button_dopolnitelnie)
        element_input.click()
        time.sleep(1)
        # Клик в перейти на сайт
        element_input = driver.find_element(By.XPATH, link_go_to_site)
        element_input.click()
        time.sleep(1)
        # Ввод логина и пароля
        element_input = driver.find_element(By.XPATH, login)
        element_input.send_keys('admin')
        element_input = driver.find_element(By.XPATH, password)
        element_input.send_keys('zBCTRuV7')
        # Клик на кнопку Войти
        element_input = driver.find_element(By.XPATH, button_login)
        element_input.click()
        time.sleep(1)

        driver.get(f'https://{ip_adress}/system_reboot')
    except:
        pass

    #     # Клик на кнопку Перезапуск программы
    #     if action == "Перезапуск программы":
    #         element_input = driver.find_element(By.XPATH, button_restart_programm)
    #         element_input.click()
    #         keyboard.send("enter")
    #     # Клик на radiobutton Фиксированный:
    #     elif action == "Фикс":
    #         element_input = driver.find_element(By.XPATH, radio_button_fix)
    #         element_input.click()
    #         time.sleep(1)
    #         element_input = driver.find_element(By.XPATH, button_change_mode)
    #         element_input.click()
    #     # Клик на radiobutton Адаптивный:
    #     elif action == "Адаптива":
    #         element_input = driver.find_element(By.XPATH, radio_button_adaptiva)
    #         element_input.click()
    #         time.sleep(1)
    #         element_input = driver.find_element(By.XPATH, button_change_mode)
    #         element_input.click()
    #     # Перезапуск ОС контроллера:
    #     elif action == "Перезапуск ОС":
    #         driver.get('https://' + ip_adress + '/system_reboot')
    #
    #
    #     time.sleep(4)
    #
    # except Exception as ex:
    #     pass
    # finally:
    #     # driver.close()
    #     driver.quit()


#
if __name__ == '__main__':
    obj = PeekWeb('ячсчя')
    # obj.session_manager(inputs=[f'MPP_MAN=ВЫКЛ' if inp == 0 else f'MPP_PH{inp}=ВФ' for inp in range(9)])
    obj.session_manager(inputs=(f'MPP_MAN=ВЫКЛ', 'MPP_PH4=ВФ', 'CP_AUTO=ВКЛ'), user_parameters=('TEST1=40', 'TEST3=4711',))
    # host = PeekWeb('dsd')
    # host.session_refactor(resetting_the_desired_values={'ВЫКЛ': ('ВКЛ',)}, MPP_MAN='ВФ')
