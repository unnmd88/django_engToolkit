import json
import os
import subprocess
import sys
from datetime import datetime as dt
import time
from enum import Enum
import asyncio
import inspect
from io import StringIO, BytesIO

from pathlib import Path

from django.core.files import File
from django.http import HttpResponse, HttpResponseNotFound, Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import QueryDict
from django.urls import reverse
from django.template.loader import render_to_string
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics

from engineering_tools.settings import MEDIA_ROOT, MEDIA_URL, BASE_DIR
from toolkit.forms_app import CreateConflictForm, ControllerManagementData
from toolkit.models import TrafficLightObjects, SaveConfigFiles, SaveConflictsTXT, ControllerManagement
from toolkit.sdp_lib import conflicts, controller_management
from toolkit.serializers import ControllerHostsSerializer, TrafficLightsSerializer

protocols = ('Поток_UG405', 'Поток_STCIP', 'Swarco_STCIP', 'Peek_UG405')


class ControllersViewSet(ModelViewSet):
    queryset = ControllerManagement.objects.all()
    serializer_class = ControllerHostsSerializer


class TrafficLightsAPIVeiw(generics.ListAPIView):
    queryset = TrafficLightObjects.objects.all()
    serializer_class = TrafficLightsSerializer




def reverse_slashes(path):
    path = path.replace('\\', '/')
    return path


def make_id(filename: str) -> int:
    """
        Возвращает id для модели UploadFiles2:
        swarco: 1
        peek: 2
        остальные файлы: 3
        :param filename: имя файла из коллекции request.FILEES:
        :return id_for_db -> номер группы(принадлежности)
        """
    if filename[-4:] == 'PTC2':
        id_for_db = 1
    elif filename[-3:] == 'DAT':
        id_for_db = 2
    else:
        id_for_db = 3
    return id_for_db


class AvailableCommandsControllerManagement(Enum):

    MAN = 'MAN'
    SNMP = 'SNMP'
    TERMINAL = 'ТЕРМИНАЛЬНАЯ КОМАНДА'
    INPUTS_PEEK = 'ВВОДЫ'
    UP_PEEK = 'ПАРАМЕТРЫ ПРОГРАММЫ'


class AvailableControllers(Enum):
    """ Доступные типы контроллера """
    SWARCO = 'SWARCO'
    POTOK_P = 'ПОТОК (P)'
    POTOK_S = 'ПОТОК (S)'
    PEEK = 'PEEK'


class ProcessedRequestBase:
    @staticmethod
    def reverse_slashes(path):
        path = path.replace('\\', '/')
        return path


class ProcessedRequestConflicts(ProcessedRequestBase):
    upload_name_id = 'upload_config_file'
    name_textarea = 'table_stages'
    controller_type = 'controller_type'

    @staticmethod
    def make_group_name(filename: str) -> str:
        """
        Возвращает id для модели UploadFiles2:
        swarco: swarco
        peek: peek
        остальные файлы: undefind
        :param filename: имя файла из коллекции request.FILEES:
        :return id_for_db -> имя группы(принадлежности)
        """
        if filename[-4:] == 'PTC2':
            id_for_db = 'swarco'
        elif filename[-3:] == 'DAT':
            id_for_db = 'peek'
        else:
            id_for_db = 'undefind'
        return id_for_db

    @staticmethod
    def correct_path(path):
        return ProcessedRequestBase.reverse_slashes(path).split('media/')[1]

    def __init__(self, request):
        self.request = request
        self.post_req_dict = request.POST.dict()
        self.files_dict = request.FILES.dict()
        self.controller_type = \
            self.post_req_dict.get(self.controller_type).lower() if self.controller_type in self.post_req_dict else None
        self.val_txt_conflicts = True if 'create_txt' in self.post_req_dict else False
        self.val_add_conflicts_and_binval_calcConflicts = True if 'binval_swarco' in self.post_req_dict else False
        self.val_make_config = True if 'make_config' in self.post_req_dict else False
        self.stages = self.post_req_dict.get(self.name_textarea)

        print('-' * 25)

        if request.FILES:
            if 'make_config' in self.post_req_dict:
                self.val_make_config = True
            if self.upload_name_id in self.files_dict:
                self.file_from_request = self.files_dict.get(self.upload_name_id)
                print(f'self.file_from_requestT: {self.file_from_request}')
                print(f'self.file_from_requestT: {type(self.file_from_request)}')
                print('--&&---')

                self.filename_from_request = self.file_from_request.name
                print(f'request.FILES.get(upload_name_id): {request.FILES.get(self.upload_name_id)}')
                print(f'request.FILES.get(upload_name_id): {type(request.FILES.get(self.upload_name_id))}')

                print(f'request.FILES2: {request.FILES}')
                print(f'self..file_from_request: {self.file_from_request}')
                print(f'self..filename_from_request: {self.filename_from_request}')
            self.group_name = self.make_group_name(filename=self.filename_from_request)
        else:
            self.val_make_config = False
            self.file_from_request = False
            self.filename_from_request = False

        # if self.val_txt_conflicts:
        #     self.make_txt_conflicts()
        #     self.path_to_txt_conflicts = SaveConflictsTXT.objects.last().file.path
        # else:
        #     self.path_to_txt_conflicts = None


class SaveConfigurationDB:
    def __init__(self, data):
        self.data = data

    def make_data_string(self):
        string = ''
        for host, data in self.data.items():
            if host.isdigit():
                string += '{' + f'{host}:{data}' + '}'
        return string


class GetConfigurationDB:
    def __init__(self, data):
        self.data = data

    def make_data(self):
        splited = self.data.split(',')
        print(splited)


menu_header = [
    {'title': 'Главная страница', 'url_name': 'home'},
    {'title': 'О сайте', 'url_name': 'about'},
    {'title': 'Возможности', 'url_name': 'options'},
    {'title': 'Обратная связь', 'url_name': 'contact'},
    {'title': 'Вход', 'url_name': 'login'},
]

menu_common = [
    {'id': 1, 'title': 'Управление по SNMP', 'url_name': 'manage_snmp'},
    {'id': 3, 'title': 'Расчет цикла и сдвигов', 'url_name': 'calc_cyc'},
    {'id': 4, 'title': 'Расчет конфликтов', 'url_name': 'calc_conflicts'},
]

data_db2 = ['Управление по SNMP', 'Фильтр SNMP',
            'Расчет цикла и сдвигов', 'Расчет конфликтов'
            ]

controllers_menu = [
    {'id': 1, 'title': 'Swarco', 'url_name': 'swarco'},
    {'id': 3, 'title': 'Peek', 'url_name': 'peek'},
    {'id': 4, 'title': 'Поток', 'url_name': 'potok'},
]

path_tmp = 'toolkit/tmp/'
path_uploads = 'toolkit/uploads/'


def get_snmp_ajax(request, num_host):
    print(f'request.GET: {request.GET}')
    print(f'request: {request}')
    get_dict = request.GET.dict()
    print(f'get_dict: {get_dict}')

    if request.GET:
        objects_methods = []
        get_data_manager = controller_management.GetDataControllerManagement()
        for num_host, data_request in get_dict.items():
            data_request = data_request.split(';')
            if len(data_request) != 3:
                continue
            ip_adress, controller_type, scn = data_request
            controller_type_request = get_type_object_get_request(controller_type.upper())
            obj = controller_management.Controller(ip_adress, controller_type_request, scn, num_host)
            objects_methods.append(obj.get_current_mode)
        raw_data_from_controllers = asyncio.run(get_data_manager.main(objects_methods, option='get'))
        processed_data = get_data_manager.data_processing(raw_data_from_controllers)
    else:
        print('nnnnnooo')
        return HttpResponse(json.dumps('Error: Failed to get data'), content_type='text/html')

    return HttpResponse(json.dumps(processed_data, ensure_ascii=False), content_type='text/html')


def set_snmp_ajax(request, num_host):
    print(f'set_snmp_ajax')
    result = None
    if request.POST:

        set_stage = ('ФАЗА MAN', 'ФАЗА SNMP')
        set_flash = ('ЖМ MAN', 'ЖМ SNMP')
        set_dark = ('ОС MAN', 'ОС SNMP')

        set_dict = request.POST.dict()
        print(f'set_dict: {set_dict}')
        for num_host, data_request in set_dict.items():
            data_request = data_request.split(';')
            if len(data_request) != 5:
                continue
            ip_adress, type_of_controller, scn, command, value = data_request
            command, type_of_controller = command.upper(), type_of_controller.upper()
            type_of_controller_management = get_type_object_set_request(type_of_controller, command)
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

        res = {num_host: result}

    else:
        res = {num_host: 'error_set_request'}

    print(f'set_snmp_ajax перед return')

    return HttpResponse(json.dumps(res, ensure_ascii=False), content_type='text/html')


def get_configuration_controller_management(request):
    if request.POST:
        set_dict = request.POST.dict()
        print(f'set_dict {set_dict}')
        name = set_dict.get('name_configuration')

        w = ControllerManagement.objects.get(name=name)

        print(w.data)
        print(f'type(w.data) = {type(w.data)}')

        # data = {
        #     'data': [{1: w.data}, {2: 'fdf;10.23.'}],
        #
        # }
        data = {
            'data': w.data,
            'num_visible_hosts': w.num_visible_hosts,
        }
    else:
        data = {'data': False}

    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type='text/html')


def save_configuration_snmp(request):
    if request.POST:

        print('save_snmp_curr_configuration')
        post_dict = request.POST.dict()
        print(f'request.POST.dict(): {post_dict}')

        name = post_dict.pop('name')
        num_visible_hosts = post_dict.pop('num_visible_hosts')
        configuration = ControllerManagement(name=name, data=post_dict,
                                             num_visible_hosts=num_visible_hosts,
                                             category=1)
        try:
            configuration.save()
            result = True
        except Exception as err:
            print('error ' + str(err))
            result = False
    else:
        result = False

    data = {'result': result}
    return HttpResponse(json.dumps(data, ensure_ascii=False), content_type='text/html')


def my_python_function(request):  # Ваш код Python здесь
    response_data = {'message': 'Функция Python вызвана успешно!'}
    print(response_data)
    return JsonResponse(response_data)


def index(request):
    print('ind')

    data = {'title': 'Главная страница',
            'menu_header': menu_header,
            'menu2': data_db2,
            'menu_common': menu_common,
            'controllers_menu': controllers_menu,
            }
    return render(request, 'toolkit/index.html', context=data)


def about(request):
    return render(request, 'toolkit/about.html', {'title': 'О сайте', 'menu_header': menu_header})


def manage_snmp(request):
    first_row_settings = {'label_settings': 'Настройки ДК', 'ip': 'IP-адресс', 'scn': 'SCN', 'protocol': 'Протокол'}
    second_row_get = {'controller_data': 'Информация с ДК', 'label_get_data': 'Получать данные с ДК',
                      'label_data': 'Данные с ДК'}
    third_row_set = {'set_btn': 'Отправить'}
    form = ControllerManagementData()

    # print(BASE_DIR / 'data/db.sqlite3')

    host_data = {
        'first_row_settings': first_row_settings,
        'second_row_get': second_row_get,
        'third_row_set': third_row_set,
        'num_hosts': [i for i in range(1, 31)],
        'data_form': form,
        'title': 'Управление контроллером'
    }

    return render(request, 'toolkit/manage_snmp.html', context=host_data)


def contact(request):
    return HttpResponse('Обратная связь')


def login(request):
    return HttpResponse('Авторизация')


def options(request):
    return HttpResponse('Возможности')


def show_tab(request, post_id):
    print('1')
    controller = get_object_or_404(TrafficLightObjects, pk=post_id)

    data = {
        'num_CO': controller.ip_adress,
        'menu': menu_header,
        'controller': controller,
        'cat_selected': 1,
    }

    return render(request, 'toolkit/about_controller.html', context=data)

    # return HttpResponse(f'Отображение вкладки с id = {post_id}')


def calc_cyc(request):
    data = {'title': 'Расчёт циклов и сдвигов', 'menu_header': menu_header}
    return render(request, 'toolkit/calc_cyc.html', context=data)


# def tabs(request, tabs_id):
#     return HttpResponse(f'<h1> Странца приложения tabs </h1><p>id: {tabs_id}</p>')
#
#
# def tabs_by_slug(request, tabs_slug):
#     print(request.GET)
#     return HttpResponse(f'<h1> Странца приложения tabs </h1><p>slug: {tabs_slug}</p>')
#
# def main_page(request):
#     return HttpResponse('Главная страница')
#
#
# def archive(request, year):
#     if year > 2024:
#         uri = reverse('tabs_slug', args=('test', ))
#         return HttpResponseRedirect('/')

def upload_file(file):
    with open(f'{path_tmp}{file.name}', 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)


def page_not_found(request, exception):
    return HttpResponseNotFound("<h1> Страница не найдена </h1>")


def data_for_calc_conflicts(request):
    title = 'Расчёт конфликтов'

    if request.GET:
        data = {'render_conflicts_data': False, 'menu_header': menu_header, 'title': title}
        return render(request, 'toolkit/calc_conflicts.html', context=data)

    elif request.POST:
        req_data = ProcessedRequestConflicts(request)
        if req_data.val_make_config:
            SaveConfigFiles.objects.create(file=req_data.file_from_request, controller_type=req_data.group_name,
                                           source='uploaded', )
            path_to_config_file = SaveConfigFiles.objects.last().file.path
        else:
            path_to_config_file = None

    else:
        # DEBUG
        data = {'render_conflicts_data': False, 'menu_header': menu_header, 'title': title}
        return render(request, 'toolkit/calc_conflicts.html', context=data)

    print(f'BASE_DIR {BASE_DIR}')
    print(f'MEDIA_ROOT {MEDIA_ROOT}')
    print(f'MEDIA_URL {MEDIA_URL}')

    path_txt_conflict = f'{MEDIA_ROOT}/conflicts/txt/сalculated_conflicts {dt.now().strftime("%d %b %Y %H_%M_%S")}.txt'

    obj = conflicts.Conflicts()
    res, msg, *rest = obj.calculate_conflicts(
        input_stages=req_data.stages,
        controller_type=req_data.controller_type,
        make_txt_conflicts=req_data.val_txt_conflicts,
        add_conflicts_and_binval_calcConflicts=req_data.val_add_conflicts_and_binval_calcConflicts,
        make_config=req_data.val_make_config,
        prefix_for_new_config_file='new_',
        path_to_txt_conflicts=path_txt_conflict,
        path_to_config_file=path_to_config_file)

    print(f'res: {res}: msg {msg}')
    print(f'obj.result_make_config.: {obj.result_make_config}')
    print(f'obj.result_num_kolichestvo_napr: {obj.result_num_kolichestvo_napr}')
    print(f'sorted_stages: {obj.sorted_stages}')
    print(f'kolichestvo_napr: {obj.kolichestvo_napr}')
    print(f'matrix_output: {obj.matrix_output}')
    print(f'matrix_swarco_F997: {obj.matrix_swarco_F997}')
    print(f'conflict_groups_F992: {obj.conflict_groups_F992}')
    print(f'binary_val_swarco_for_write_PTC2: {obj.binary_val_swarco_for_write_PTC2}')
    print(f'binary_val_swarco_F009: {obj.binary_val_swarco_F009}')

    if obj.result_make_config and obj.result_make_config[0] and len(obj.result_make_config) >= 3:
        f = SaveConfigFiles(source='created', file=obj.result_make_config[2],
                            controller_type=req_data.group_name)
        f.file.name = ProcessedRequestConflicts.correct_path(f.file.path)
        f.save()
        create_link_config = True
    else:
        create_link_config = False

    if obj.result_make_txt and obj.result_make_txt[0] and len(obj.result_make_txt) >= 3:
        f = SaveConflictsTXT(source='created', file=obj.result_make_txt[2])
        f.file.name = ProcessedRequestConflicts.correct_path(f.file.path)
        f.save()
        create_link_txt_conflicts = True
    else:
        create_link_txt_conflicts = False

    data = {
        'menu_header': menu_header,
        'title': title,
        'render_conflicts_data': res,
        'add_conflicts_and_binval_calcConflicts': req_data.val_add_conflicts_and_binval_calcConflicts,
        'values': ('| K|', '| O|'),
        'matrix': obj.matrix_output,
        'sorted_stages': obj.sorted_stages,
        'kolichestvo_napr': obj.kolichestvo_napr,
        'matrix_swarco_F997': obj.matrix_swarco_F997,
        'conflict_groups_F992': obj.conflict_groups_F992,
        'binary_val_swarco_F009': obj.binary_val_swarco_F009,
        'create_link_txt_conflicts': create_link_txt_conflicts,
        'create_link_config': create_link_config,
        'txt_conflict_file': SaveConflictsTXT.objects.last() if SaveConflictsTXT.objects.last() else False,
        'config_file': SaveConfigFiles.objects.last() if SaveConfigFiles.objects.last() else False,
    }

    return render(request, 'toolkit/calc_conflicts.html', context=data)


def controller_swarco(request):
    data = {'title': 'Swarco', 'menu_header': menu_header}

    content = render_to_string('toolkit/swarco.html', data, request)

    return HttpResponse(content, )

    return render(request, 'toolkit/swarco.html', context=data, content_type='application/force-download')


def controller_peek(request):
    data = {'title': 'Peek', 'menu_header': menu_header}
    return render(request, 'toolkit/peek.html', context=data)


def controller_potok(request):
    data = {'title': 'Поток', 'menu_header': menu_header}
    return render(request, 'toolkit/potok.html', context=data)


def get_type_object_set_request(controller_type, command):
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



def get_type_object_get_request(controller_type: str):

    if controller_type == AvailableControllers.POTOK_P.value:
        return controller_management.AvailableProtocolsManagement.POTOK_UG405.value
    elif controller_type == AvailableControllers.POTOK_S.value:
        return controller_management.AvailableProtocolsManagement.POTOK_STCIP.value
    elif controller_type == AvailableControllers.SWARCO.value:
        return controller_management.AvailableProtocolsManagement.SWARCO_STCIP.value
    elif controller_type == AvailableControllers.PEEK.value:
        return controller_management.AvailableProtocolsManagement.PEEK_UG405.value
