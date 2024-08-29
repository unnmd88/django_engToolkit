
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