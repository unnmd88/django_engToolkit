import json
import logging
import sys
import ast
import time
from datetime import datetime as dt
from enum import Enum
import asyncio
import inspect
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from engineering_tools.settings import MEDIA_ROOT, MEDIA_URL, BASE_DIR, SHARED_DESKTOP
from toolkit.forms_app import CreateConflictForm, ControllerManagementData
from toolkit.models import TrafficLightObjects, SaveConfigFiles, SaveConflictsTXT, ControllerManagement
from toolkit.sdp_lib import conflicts
from toolkit.serializers import ControllerHostsSerializer, TrafficLightsSerializer
from . import services

class ControllersViewSet(APIView):

    def get(self, request):
        queryset = ControllerManagement.objects.all()

        name_configuration = self.request.query_params.get('name_configuration')
        if name_configuration is not None:
            queryset = queryset.filter(name=self.request.query_params.get('name_configuration')).values()[0]
            try:
                queryset['data'] = ast.literal_eval(queryset.get('data'))
                return Response(queryset)
            except Exception as err:
                print(f'err: {err}')
                return Response({'Fault': 'Ошибка получения конфигураии'})
        return Response({'Error': 'Имя конфигурации не определено'})

    # serializer_class = ControllerHostsSerializer
    # print(f'serializer_class: {serializer_class}' )
    # def get_queryset(self):
    #
    #     queryset = ControllerManagement.objects.all()
    #     name_configuration = self.request.query_params.get('name_configuration')
    #     if name_configuration is not None:
    #         queryset = queryset.filter(name=self.request.query_params.get('name_configuration'))
    #     print(f'queryset: {queryset}')
    #     print(f'serializer_class: {self.serializer_class}')
    #     return queryset


class SearchControllerViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        # allowed_options = ('number', 'description')
        number_search = 'number'
        description_search = 'description'
        print(f'self.request.query_params: {self.request.query_params}')

        if number_search in self.request.query_params and self.request.query_params.get(number_search).isdigit():
            queryset = TrafficLightObjects.objects.filter(number=int(self.request.query_params.get(number_search)))
            print(f'queryset from if SearchControllerViewSet: {queryset.values()}')
            if queryset:
                queryset = queryset.values()[0]
            else:
                queryset = {'error': 'Объект не найден', 'result': False}
        elif description_search in self.request.query_params:
            queryset = TrafficLightObjects.objects.filter(
                description=self.request.query_params.get(description_search).lower())
            print(f'queryset from elif SearchControllerViewSet: {queryset.values()}')
            if queryset:
                queryset = queryset.values()[0]
            else:
                queryset = {'error': 'Объект не найден', 'result': False}
        else:
            queryset = {'error': 'Неверный тип запроса', 'result': False}
        return Response(queryset)


class TrafficLightsAPIVeiw(generics.ListAPIView):
    queryset = TrafficLightObjects.objects.all()
    serializer_class = TrafficLightsSerializer


# class GetControllerData(View)


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

logger = logging.getLogger(__name__)


def test_logger(request):
    logger.debug('TEst1')
    print(logger)
    return JsonResponse({'Res': 'success'})


class GetDataFromControllerAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    # def get(self, request):
    #
    #
    #
    #     manager = GetDataFromController(request)
    #     objects_methods = manager.create_objects_methods()
    #     if objects_methods:
    #         processed_data = manager.get_data_from_controllers(objects_methods)
    #     else:
    #         processed_data = {'software fault': 'Программный сбой'}
    #
    #     return Response(processed_data)
    def post(self, request):

        # print(f'req_data = {request.data}')
        # print(f'req_data2 = {request.data.get("data")}')
        start_time = time.time()
        manager = services.GetDataFromController(request.data.get('data', {}))
        err_hosts, res_req = asyncio.run(manager.main())
        responce = {}
        for errInd, varBinds, obj in res_req:
            data_host = obj.create_json(errInd, varBinds, first_kwarg='вот он первий попытка))) kwarg')
            logger.debug(data_host)
            responce |= data_host

        logger.debug(f'Время выполнения запроса: {time.time() - start_time}')
        return Response(responce)


class SetRequestToControllerAPIView(APIView):

    def post(self, request):
        print(f'post-post')
        manager = services.SetRequestToController(request)
        num_host, result, msg = manager.set_command_request()

        context = {
            'num_host': int(num_host) if num_host.isdigit() else num_host,
            'result': result,
            'message': msg
        }

        return Response(context)


class GetNamesConfigurationControllerManagementAPIView(APIView):

    def get(self, request):
        first_option = 'Выбор конфигурации'
        names = {k: v if k > 0 else first_option
                 for k, v in enumerate([el[0] for el in ControllerManagement.objects.values_list('name')])}
        # print(f'nameees2 --> {names}')
        return Response(names)


def get_configuration_controller_management_axios(request):
    # print(f'get_configuration_controller_management_ax')


    if request.GET:
        get_dict = request.GET.dict()
        print(f'get_dict {get_dict}')
        name = get_dict.get('name_configuration')

        w = ControllerManagement.objects.get(name=name)

        print(w.data)
        print(f'type(w.data) = {type(w.data)}')

        # data = {
        #     'data': [{1: w.data}, {2: 'fdf;10.23.'}],
        #
        # }
        data = {
            'data': json.loads(w.data),
            'num_visible_hosts': json.loads(w.num_visible_hosts),
            'result': True
        }
    else:
        data = {'result': False}

    return JsonResponse(data)


def save_configuration_controller_management_axios(request):
    data_request = json.loads(request.body.decode("utf-8")).get('data')
    # print(f'data_request SV_AXIOS: {data_request} ')

    name = data_request.pop('name')
    num_visible_hosts = data_request.pop('num_visible_hosts')
    configuration = ControllerManagement(name=name, data=json.dumps(data_request, ensure_ascii=False),
                                         num_visible_hosts=num_visible_hosts,
                                         category=1)

    try:
        configuration.save()
        result = True
    except Exception as err:
        print('error ' + str(err))
        result = False

    # qset = ControllerManagement.objects.filter(name=name)
    # res = json.loads(qset[0].data) if len(qset) == 1 else 'null'
    # res['num_visible_hostsSSs'] = qset[0].num_visible_hosts
    #
    # print(f'res__: {res}')
    # print(f'res__ typy: {type(res)}')

    # if request.POST:
    #
    #     print('save_snmp_curr_configuration')
    #     post_dict = request.POST.dict()
    #     print(f'request.POST.dict(): {post_dict}')
    #
    #     name = post_dict.pop('name')
    #     num_visible_hosts = post_dict.pop('num_visible_hosts')
    #     configuration = ControllerManagement(name=name, data=post_dict,
    #                                          num_visible_hosts=num_visible_hosts,
    #                                          category=1)
    #     try:
    #         configuration.save()
    #         result = True
    #     except Exception as err:
    #         print('error ' + str(err))
    #         result = False
    # else:
    #     result = False
    # res = {'result': res}

    return JsonResponse({'result': result})




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


# def manage_snmp(request):
#     first_row_settings = {'label_settings': 'Настройки ДК', 'ip': 'IP-адресс', 'scn': 'SCN', 'protocol': 'Протокол'}
#     second_row_get = {'controller_data': 'Информация с ДК', 'label_get_data': 'Получать данные с ДК',
#                       'label_data': 'Данные с ДК'}
#     third_row_set = {'set_btn': 'Отправить'}
#     form = ControllerManagementData()
#
#     # print(BASE_DIR / 'data/db.sqlite3')
#
#     host_data = {
#         'first_row_settings': first_row_settings,
#         'second_row_get': second_row_get,
#         'third_row_set': third_row_set,
#         'num_hosts': [i for i in range(1, 31)],
#         'data_form': form,
#         'title': 'Управление контроллером',
#         'flag SHARED_DESKTOP': SHARED_DESKTOP
#     }
#
#     return render(request, 'toolkit/manage_snmp.html', context=host_data)


def manage_snmp(request):
    first_row_settings = {'label_settings': 'Настройки ДК', 'ip': 'IP-адресс', 'scn': 'SCN', 'protocol': 'Протокол'}
    second_row_get = {'controller_data': 'Информация с ДК', 'label_get_data': 'Получать данные с ДК',
                      'label_data': 'Данные с ДК'}
    third_row_set = {'set_btn': 'Отправить'}
    form = ControllerManagementData()
    lst = [el.name for el in ControllerManagement.objects.all()]

    # print(BASE_DIR / 'data/db.sqlite3')

    host_data = {
        'first_row_settings': first_row_settings,
        'second_row_get': second_row_get,
        'third_row_set': third_row_set,
        'num_hosts': [i for i in range(1, 31)],
        'data_form': form,
        'lst': lst,
        'title': 'Управление контроллером',
        'flag SHARED_DESKTOP': SHARED_DESKTOP
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

# def get_type_object_set_request(controller_type, command):
#     SNMP = 'SNMP'
#     MAN = 'MAN'
#     INPUTS = 'ВВОДЫ'
#
#     command = command.upper()
#
#     if controller_type == AvailableControllers.POTOK_P.value:
#         if SNMP in command:
#             return controller_management.AvailableProtocolsManagement.POTOK_UG405.value
#     elif controller_type == AvailableControllers.POTOK_S.value:
#         if SNMP in command:
#             return controller_management.AvailableProtocolsManagement.POTOK_STCIP.value
#     elif controller_type == AvailableControllers.SWARCO.value:
#         if SNMP in command:
#             return controller_management.AvailableProtocolsManagement.SWARCO_STCIP.value
#         elif MAN in command:
#             return controller_management.AvailableProtocolsManagement.SWARCO_SSH.value
#     elif controller_type == AvailableControllers.PEEK.value:
#         if SNMP in command:
#             return controller_management.AvailableProtocolsManagement.PEEK_UG405.value
#         elif MAN in command or INPUTS in command:
#             return controller_management.AvailableProtocolsManagement.PEEK_WEB.value
#
#
# def get_type_object_get_request(controller_type: str):
#     if controller_type == AvailableControllers.POTOK_P.value:
#         return controller_management.AvailableProtocolsManagement.POTOK_UG405.value
#     elif controller_type == AvailableControllers.POTOK_S.value:
#         return controller_management.AvailableProtocolsManagement.POTOK_STCIP.value
#     elif controller_type == AvailableControllers.SWARCO.value:
#         return controller_management.AvailableProtocolsManagement.SWARCO_STCIP.value
#     elif controller_type == AvailableControllers.PEEK.value:
#         return controller_management.AvailableProtocolsManagement.PEEK_UG405.value
