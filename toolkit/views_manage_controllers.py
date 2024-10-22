

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


class GetNamesConfigurationControllerManagementAPIView(APIView):

    def get(self, request):
        first_option = 'Выбор конфигурации'
        names = {k: v if k > 0 else first_option
                 for k, v in enumerate([el[0] for el in ControllerManagement.objects.values_list('name')])}
        # print(f'nameees2 --> {names}')
        return Response(names)


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