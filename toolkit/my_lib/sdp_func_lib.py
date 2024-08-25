import socket
import subprocess
import itertools
import datetime

import time
from datetime import datetime


def time_benchmark(func):
    def wrapper(option=None):
        start_time = time.time()
        func(option)
        print(f'Время выполенения функции: {time.time() - start_time}')

    return wrapper


def find_max_num_napravl(stages: list) -> int:
    max_napr = 0
    for num_stage in range(len(stages)):
        try:
            tmp_max_napr = int(max(stages[num_stage], key=lambda napr: int(napr)))
            # print(tmp_max_napr)
            if max_napr < tmp_max_napr:
                max_napr = tmp_max_napr
        except ValueError:
            pass
    return max_napr


def get_data_from_list(path_to_file):
    try:
        with open(path_to_file, 'r', encoding='UTF-8') as file:
            data_list = []
            for line in file:
                data_list.append(line.strip().split(':'))
    except UnicodeError:
        with open(path_to_file, 'r', encoding='windows-1251') as file:
            data_list = []
            for line in file:
                data_list.append(line.strip().split(':'))
    return data_list


def make_path_to_save_config(path_old: str):
    if '/' in path_old:
        part1_dir = '/'.join(path_old.split('/')[:-1])
        part2_name = '/'.join(path_old.split('/')[-1:])
        # print(f'{part1_dir}/new_{part2_name}')
        return f'{part1_dir}/new_{part2_name}'

    elif '\\' in path_old:
        path_old = remove_quotes(path_old)
        part1_dir = '\\'.join(path_old.split('\\')[:-1])
        part2_name = '\\'.join(path_old.split('\\')[-1:])
        # print(f'{part1_dir}/new_{part2_name}')
        return f'{part1_dir}/new_{part2_name}'


def remove_quotes(user_file):
    """Функция принимает на вход строку, которую ввел пользователь, содержащую путь к каталогу/файлу и
       возвращает строку без кавычек"""
    user_file = user_file.replace('"', '').replace("'", '')
    return user_file


def reverse_slashes(path):
    path = path.replace('\\', '/')
    return path


def import_data_from_file_for_calc_conflict(filename: str) -> list:
    if filename:
        with open(filename, 'r') as file:
            data_from_file = file.readlines()
            return data_from_file


def sort_stages(stages: list):
    """Функция сортирует списки фаза-направление. на вход получает список вложенных списков.
        Вложенный список с индексом 0 -> 1 фаза, с индексом 1 -> 2 фаза и т.д.
        Значения в списке - направления, участвующие в фазе
        Возвращает кортеж: отсортированный список списков фаза-направление, количество направлений
    """

    if stages is None or len(stages) > 255:
        return

    kolichestvo_naptavleniy = 0
    for i in range(len(stages)):
        try:
            if stages[i][0].replace(' ', '') != '':
                stages[i] = list(map(int, stages[i]))
                max_num_napr_v_faze = max(stages[i])
                if kolichestvo_naptavleniy < max_num_napr_v_faze:
                    kolichestvo_naptavleniy = max_num_napr_v_faze
                stages[i] = sorted(list(set(stages[i])))
            else:
                stages[i] = []
        except ValueError as err:
            return err
    return stages, kolichestvo_naptavleniy


def make_number_coflicts_group_for_swarco_F992(conflict_matrix_F997, controller_type):
    """ Функция принимает на вход матрицу конфликтов вида F997.
        Рассчитывает и возвращает вложенный список направлений, с которыми есть конфликт у каждой их групп
        Вложенный список с индеком 0 -> группы, с которыми есть конфликт у 1 направления,
        индекс 1 -> группы, с которыми есть конфликт у 2 направления и т.д.
    """

    if controller_type == 'swarco':
        conflict_groups_F992 = []
        # print('conflict_matrix_F997')
        # print(conflict_matrix_F997)
        for i in range(len(conflict_matrix_F997)):
            tmp = []
            num_group = 1

            for j in conflict_matrix_F997[i]:
                if j == '03.0;':
                    tmp.append(f'{num_group};')
                num_group += 1
            conflict_groups_F992.append(tmp)
        return conflict_groups_F992
    elif controller_type == 'peek':
        conflict_groups_Peek = []
        # print('conflict_matrix_F997')
        # print(conflict_matrix_F997)
        sum_conflicts_for_peek = 0  # Количество конфликтов для Пика

        for i in range(len(conflict_matrix_F997)):
            tmp2 = []
            num_group = 1
            for j in conflict_matrix_F997[i]:
                if j == '03.0;':
                    tmp2.append(num_group)
                num_group += 1
            conflict_groups_Peek.append(tmp2)
            sum_conflicts_for_peek = sum_conflicts_for_peek + len(tmp2)
        # print('make_number_coflicts_group_for_swarco_F992')
        # print(conflict_groups_Peek)
        # print(f'sum_conflicts_for_peek: {sum_conflicts_for_peek}')
        # make_dat_file_for_peek(conflict_groups_F992, sum_conflicts_for_peek)
        return conflict_groups_Peek, sum_conflicts_for_peek

    # conflict_groups_F992 = []
    # conflict_groups_Peek = []
    #
    # print('conflict_matrix_F997')
    # print(conflict_matrix_F997)
    # sum_conflicts_for_peek = 0  # Количество конфликтов для Пика
    #
    # sum_confl_final = 0
    #
    # for i in range(len(conflict_matrix_F997)):
    #     tmp = []
    #     tmp2 = []
    #     num_group = 1
    #     sum_conflicts_for_peek2 = 0
    #
    #     for j in conflict_matrix_F997[i]:
    #         if j == '03.0;':
    #             tmp.append(f'{num_group};')
    #             tmp2.append(num_group)
    #             sum_conflicts_for_peek2 += 1
    #         num_group += 1
    #     conflict_groups_F992.append(tmp)
    #     conflict_groups_Peek.append(tmp2)
    #     sum_confl_final = sum_confl_final + sum_conflicts_for_peek2
    #     sum_conflicts_for_peek = sum_conflicts_for_peek + len(tmp2)
    # print('make_number_coflicts_group_for_swarco_F992')
    # print(conflict_groups_F992)
    # print(conflict_groups_Peek)
    # print(f'sum_confl_final: {sum_confl_final}')
    # print(f'sum_conflicts_for_peek: {sum_conflicts_for_peek}')
    #
    # make_dat_file_for_peek(conflict_groups_F992, sum_conflicts_for_peek)
    #
    # return conflict_groups_F992
    # for i in range(len(conflict_groups_F992)):
    #     print(*conflict_groups_F992[i])


# def make_number_coflicts_group_for_swarco_F992(conflict_matrix_F997) -> list:
#     """ Функция принимает на вход матрицу конфликтов вида F997.
#         Рассчитывает и возвращает вложенный список направлений, с которыми есть конфликт у каждой их групп
#         Вложенный список с индеком 0 -> группы, с которыми есть конфликт у 1 направления,
#         индекс 1 -> группы, с которыми есть конфликт у 2 направления и т.д.
#     """
#     conflict_groups_F992 = []
#     conflict_groups_Peek = []
#
#     print('conflict_matrix_F997')
#     print(conflict_matrix_F997)
#     sum_conflicts_for_peek = 0  # Количество конфликтов для Пика
#
#     sum_confl_final = 0
#
#     for i in range(len(conflict_matrix_F997)):
#         tmp = []
#         tmp2 = []
#         num_group = 1
#         sum_conflicts_for_peek2 = 0
#
#         for j in conflict_matrix_F997[i]:
#             if j == '03.0;':
#                 tmp.append(f'{num_group};')
#                 tmp2.append(num_group)
#                 sum_conflicts_for_peek2 += 1
#             num_group += 1
#         conflict_groups_F992.append(tmp)
#         conflict_groups_Peek.append(tmp2)
#         sum_confl_final = sum_confl_final + sum_conflicts_for_peek2
#         sum_conflicts_for_peek = sum_conflicts_for_peek + len(tmp2)
#     print('make_number_coflicts_group_for_swarco_F992')
#     print(conflict_groups_F992)
#     print(conflict_groups_Peek)
#     print(f'sum_confl_final: {sum_confl_final}')
#     print(f'sum_conflicts_for_peek: {sum_conflicts_for_peek}')
#
#     make_dat_file_for_peek(conflict_groups_F992, sum_conflicts_for_peek)
#
#     return conflict_groups_F992
#     # for i in range(len(conflict_groups_F992)):
#     #     print(*conflict_groups_F992[i])


# def make_conflicts_and_binary_val(stages=None, path_and_name_for_txt_conflicts=None, flag_conflicts_swarco=False,
#                                   flag_save_conflicts_to_dat_peek=False, flag_save_conflicts_to_PTC2=False,
#                                   path_to_original_PTC2=None, path_to_new_PTC2=None, confl_swarco='03.0;',):
#
#
#     """ Функция формирует матрицу конфликтов на алгоритме поиска конфликтных направлений
#         Матрица для функции F997 swarco: 0 индекс -> 1 направление, 1 индекс -> 2 направление и т.д.
#         Матрица для вывода на экран(oputput)/записи в файл: 0 индекс -> шапка матрицы
#         1 индекс -> 1 направление, 2 индекс -> 2 направление и т.д.
#         Вазвращает кортеж списков: (матрица сварко(list), матрица output(list), бинарное значение для F009(list)
#         matrix_swarco_F997 - > матрица конфликтов для F997
#         matrix_output -> матрица конфликтов для записи в txt/вывода на экран
#         binary_val_swarco_for_write_PTC2 -> бинарные значения фаз для записи в PTC2
#         binary_val_swarco_F009 -> бинарные значения фаз для записи txt
#         supervisor_matrix_swarco_F997 -> матрица конфликтов для F997, ссозданная на основе алгоритма, отличающегося
#         от того, по которому формируется matrix_swarco_F997. После создания обеих матриц идёт проверка, равны
#         ли они друг другу. Если не равны -> выходим из функции и пишем в лог
#
#     """
#     print(f'ya v make_conflicts_and_binary_val')
#     print(stages)
#     stages_and_napr = sort_stages(stages)
#     print(stages_and_napr)
#     sorted_stages, kolichestvo_napr = stages_and_napr
#
#     if sorted_stages is None or kolichestvo_napr is None:
#         return
#     if path_and_name_for_txt_conflicts is None:
#         path_and_name_for_txt_conflicts = os.getcwd()
#
#
#
#     matrix_swarco_F997 = []
#     binary_val_swarco_for_write_PTC2 = []
#     binary_val_swarco_F009 = []
#     supervisor_matrix_swarco_F997 = []
#     # Шапка вида | *| |01| |02| |03| |04| |05| |06| |07| |08| |09| |10|
#     matrix_output = [['| *|' if i == 0 else f'|0{i}|' if i < 10 else f'|{i}|' for i in range(kolichestvo_napr + 1)]]
#
#     for i in range(1, kolichestvo_napr + 1):
#         tmp_matrix_output = ['X;' if x == i - 1 else confl_swarco for x in range(kolichestvo_napr)]
#         tmp_matrix_swarco_F997 = [f'|0{i}|' if x == 0 and i < 10 else f'|{i}|' if x == 0 and i > 9 else
#                                   '| K|' for x in range(kolichestvo_napr + 1)]
#         binary_val = 0
#
#         tmp_for_supervisor = []
#         tmp_matrix_swarco_F997_supervosor = ['X;' if x == i - 1 else confl_swarco for x in range(kolichestvo_napr)]
#
#         for j in range(len(sorted_stages)):
#             if i in sorted_stages[j]:
#                 for napr in sorted_stages[j]:
#                     tmp_matrix_output[napr - 1] = '  . ;'
#                     tmp_matrix_output[i - 1] = 'X;'
#
#                     tmp_matrix_swarco_F997[napr] = '| O|'
#                     tmp_matrix_swarco_F997[i] = '| *|'
#                     #Для проверки(supervisor_matrix_swarco_F997)
#                     tmp_for_supervisor = tmp_for_supervisor + sorted_stages[j]
#
#                 if flag_conflicts_swarco:
#                     if j != 7:
#                         binary_val = binary_val + 2 ** (j + 1)
#                     else:
#                         binary_val = binary_val + 2 ** 0
#             # Если фаза пустая(без направлений)
#             elif not sorted_stages[j]:
#                 tmp_matrix_swarco_F997[i] = '| *|'
#
#
#         if flag_conflicts_swarco:
#             if binary_val < 10:
#                 binary_val_swarco_for_write_PTC2.append([f';00{binary_val};;1;'])
#             elif binary_val > 9 and binary_val < 100:
#                 binary_val_swarco_for_write_PTC2.append([f';0{binary_val};;1;'])
#             elif binary_val > 99 and binary_val < 256:
#                 binary_val_swarco_for_write_PTC2.append([f';{binary_val};;1;'])
#             binary_val_swarco_F009.append([f'{binary_val};'])
#
#
#         matrix_swarco_F997.append(tmp_matrix_output)
#         matrix_output.append(tmp_matrix_swarco_F997)
#
#         # Для проверки(supervisor_matrix_swarco_F997)
#         tmp_for_supervisor = sorted(list(set(tmp_for_supervisor)))
#         for ii in tmp_for_supervisor:
#             tmp_matrix_swarco_F997_supervosor[ii - 1] = '  . ;'
#             tmp_matrix_swarco_F997_supervosor[i - 1] = 'X;'
#         supervisor_matrix_swarco_F997.append(tmp_matrix_swarco_F997_supervosor)
#
#     if supervisor_matrix_swarco_F997 != matrix_swarco_F997:
#         return
#
#     if flag_save_conflicts_to_PTC2:
#         conflict_groups_F992 = make_number_coflicts_group_for_swarco_F992(matrix_swarco_F997)
#         write_conflicts_to_file(path_and_name_for_txt_conflicts=path_and_name_for_txt_conflicts,
#                                 sorted_stages=sorted_stages, matrix_swarco_F997=matrix_swarco_F997,
#                                 binary_val_swarco_F009=binary_val_swarco_F009,
#                                 binary_val_swarco_for_write_PTC2=binary_val_swarco_for_write_PTC2,
#                                 kolichestvo_napravleniy=kolichestvo_napr,
#                                 matrix_output=matrix_output, conflict_groups_F992=conflict_groups_F992,
#                                 flag_save_conflicts_to_PTC2=True, path_to_original_PTC2=path_to_original_PTC2,
#                                 path_to_new_PTC2=path_to_new_PTC2)
#     elif flag_save_conflicts_to_dat_peek:
#         conflict_groups_F992 = make_number_coflicts_group_for_swarco_F992(matrix_swarco_F997)
#         write_conflicts_to_file(path_and_name_for_txt_conflicts=path_and_name_for_txt_conflicts,
#                                 sorted_stages=sorted_stages, matrix_swarco_F997=matrix_swarco_F997,
#                                 binary_val_swarco_F009=binary_val_swarco_F009,
#                                 binary_val_swarco_for_write_PTC2=binary_val_swarco_for_write_PTC2,
#                                 kolichestvo_napravleniy=kolichestvo_napr,
#                                 matrix_output=matrix_output, conflict_groups_F992=conflict_groups_F992,
#                                 flag_save_conflicts_to_PTC2=False, path_to_original_PTC2=path_to_original_PTC2,
#                                 path_to_new_PTC2=path_to_new_PTC2)
#         make_dat_file_for_peek(conflict_groups_F992)
#
#     elif flag_conflicts_swarco:
#         conflict_groups_F992 = make_number_coflicts_group_for_swarco_F992(matrix_swarco_F997)
#         write_conflicts_to_file(path_and_name_for_txt_conflicts=path_and_name_for_txt_conflicts,
#                                 sorted_stages=sorted_stages, matrix_swarco_F997=matrix_swarco_F997,
#                                 binary_val_swarco_F009=binary_val_swarco_F009, kolichestvo_napravleniy=kolichestvo_napr,
#                                 matrix_output=matrix_output, conflict_groups_F992=conflict_groups_F992,
#                                 flag_conflicts_swarco=flag_conflicts_swarco
#                                 )
#     else:
#         write_conflicts_to_file(path_and_name_for_txt_conflicts=path_and_name_for_txt_conflicts,
#                                 sorted_stages=sorted_stages,
#                                 kolichestvo_napravleniy=kolichestvo_napr,
#                                 matrix_output=matrix_output,
#                                 )
#
#
#     # if flag_conflicts_swarco:
#     #     return matrix_swarco_F997, matrix_output,
#     # conflicts_F992 = make_number_coflicts_group_for_swarco_F992(matrix_swarco_F997)


def make_conflicts_and_binary_val(sorted_stages: list, kolichestvo_napr: int, confl_swarco='03.0;'):
    matrix_swarco_F997 = []
    binary_val_swarco_for_write_PTC2 = []
    binary_val_swarco_F009 = []
    supervisor_matrix_swarco_F997 = []
    # Шапка вида | *| |01| |02| |03| |04| |05| |06| |07| |08| |09| |10|
    matrix_output = [['| *|' if i == 0 else f'|0{i}|' if i < 10 else f'|{i}|' for i in range(kolichestvo_napr + 1)]]

    for i in range(1, kolichestvo_napr + 1):
        tmp_matrix_output = ['X;' if x == i - 1 else confl_swarco for x in range(kolichestvo_napr)]
        tmp_matrix_swarco_F997 = [f'|0{i}|' if x == 0 and i < 10 else f'|{i}|' if x == 0 and i > 9 else
        '| K|' for x in range(kolichestvo_napr + 1)]
        binary_val = 0

        tmp_for_supervisor = []
        tmp_matrix_swarco_F997_supervosor = ['X;' if x == i - 1 else confl_swarco for x in range(kolichestvo_napr)]

        for j in range(len(sorted_stages)):
            if i in sorted_stages[j]:
                for napr in sorted_stages[j]:
                    tmp_matrix_output[napr - 1] = '  . ;'
                    tmp_matrix_output[i - 1] = 'X;'

                    tmp_matrix_swarco_F997[napr] = '| O|'
                    tmp_matrix_swarco_F997[i] = '| *|'
                    # Для проверки(supervisor_matrix_swarco_F997)
                    tmp_for_supervisor = tmp_for_supervisor + sorted_stages[j]

                if j != 7:
                    binary_val = binary_val + 2 ** (j + 1)
                else:
                    binary_val = binary_val + 2 ** 0
            # Если фаза пустая(без направлений)
            elif i not in sorted_stages[j]:
                tmp_matrix_swarco_F997[i] = '| *|'

        if binary_val < 10:
            binary_val_swarco_for_write_PTC2.append([f';00{binary_val};;1;'])
        elif binary_val > 9 and binary_val < 100:
            binary_val_swarco_for_write_PTC2.append([f';0{binary_val};;1;'])
        elif binary_val > 99 and binary_val < 256:
            binary_val_swarco_for_write_PTC2.append([f';{binary_val};;1;'])
        binary_val_swarco_F009.append([f'{binary_val};'])

        matrix_swarco_F997.append(tmp_matrix_output)
        matrix_output.append(tmp_matrix_swarco_F997)

        # Для проверки(supervisor_matrix_swarco_F997)
        tmp_for_supervisor = sorted(list(set(tmp_for_supervisor)))
        for ii in tmp_for_supervisor:
            tmp_matrix_swarco_F997_supervosor[ii - 1] = '  . ;'
            tmp_matrix_swarco_F997_supervosor[i - 1] = 'X;'
        supervisor_matrix_swarco_F997.append(tmp_matrix_swarco_F997_supervosor)

    if supervisor_matrix_swarco_F997 != matrix_swarco_F997:
        return
    else:
        return matrix_output, matrix_swarco_F997, binary_val_swarco_for_write_PTC2, binary_val_swarco_F009


def calculate_conflicts(stages=None, name_for_txt_conflicts=None, path_to_config_file=None,
                        controller_type=None, add_conflicts_and_binval_calcConflicts=False,
                        make_config=False):
    """ Функция формирует матрицу конфликтов на алгоритме поиска конфликтных направлений
        Матрица для функции F997 swarco: 0 индекс -> 1 направление, 1 индекс -> 2 направление и т.д.
        Матрица для вывода на экран(oputput)/записи в файл: 0 индекс -> шапка матрицы
        1 индекс -> 1 направление, 2 индекс -> 2 направление и т.д.
        Вазвращает кортеж списков: (матрица сварко(list), матрица output(list), бинарное значение для F009(list)
        matrix_swarco_F997 - > матрица конфликтов для F997
        matrix_output -> матрица конфликтов для записи в txt/вывода на экран
        binary_val_swarco_for_write_PTC2 -> бинарные значения фаз для записи в PTC2
        binary_val_swarco_F009 -> бинарные значения фаз для записи txt
        supervisor_matrix_swarco_F997 -> матрица конфликтов для F997, ссозданная на основе алгоритма, отличающегося
        от того, по которому формируется matrix_swarco_F997. После создания обеих матриц идёт проверка, равны
        ли они друг другу. Если не равны -> выходим из функции и пишем в лог

    """
    # print(f'ya v make_conflicts_and_binary_val')
    # print(stages)
    stages_and_napr = sort_stages(stages)
    # print(stages_and_napr)
    sorted_stages, kolichestvo_napr = stages_and_napr

    if sorted_stages is None or kolichestvo_napr is None:
        return
    if name_for_txt_conflicts is None:
        name_for_txt_conflicts = 'Calculate conflicts.txt'

    if controller_type is not None and make_config:
        if controller_type == 'swarco' and kolichestvo_napr > 48:
            return 'swarco more than 48 directions have been introduced'
        elif controller_type == 'swarco' and len(sorted_stages) > 8:
            return 'swarco more than 8 stages have been introduced'
        elif controller_type == 'peek' and kolichestvo_napr > 64:
            return 'peek more than 64 directions have been introduced'
        elif controller_type == 'peek' and len(sorted_stages) > 32:
            return 'peek more than 32 stages have been introduced'

    matrix_output, matrix_swarco_F997, binary_val_swarco_for_write_PTC2, \
        binary_val_swarco_F009 = make_conflicts_and_binary_val(sorted_stages, kolichestvo_napr)

    conflict_groups_F992 = make_number_coflicts_group_for_swarco_F992(matrix_swarco_F997, controller_type)

    if add_conflicts_and_binval_calcConflicts or make_config and controller_type == 'swarco':

        write_conflicts_to_txt_file(path_and_name_for_txt_conflicts=name_for_txt_conflicts,
                                    kolichestvo_napravleniy=kolichestvo_napr,
                                    sorted_stages=sorted_stages, matrix_output=matrix_output,
                                    conflicts_and_binVal_swarco=True,
                                    matrix_swarco_F997=matrix_swarco_F997,
                                    binary_val_swarco_F009=binary_val_swarco_F009,
                                    conflict_groups_F992=conflict_groups_F992)
    else:
        write_conflicts_to_txt_file(path_and_name_for_txt_conflicts=name_for_txt_conflicts,
                                    sorted_stages=sorted_stages,
                                    kolichestvo_napravleniy=kolichestvo_napr,
                                    matrix_output=matrix_output)

    if make_config:
        if controller_type == 'swarco':
            result_write_conflicts = make_PTC2_file(matrix_swarco_F997=matrix_swarco_F997,
                                                    binary_val_swarco_for_write_PTC2=binary_val_swarco_for_write_PTC2,
                                                    path_to_original_PTC2=path_to_config_file)
            return
        elif controller_type == 'peek':

            conflict_groups_F992, sum_conflicts = make_number_coflicts_group_for_swarco_F992(
                matrix_swarco_F997, controller_type)
            result_write_conflicts = make_dat_file_for_peek(
                conflict_groups_F992, sum_conflicts, sorted_stages, path_to_config_file)

    return sorted_stages, kolichestvo_napr, matrix_output, matrix_swarco_F997, conflict_groups_F992,\
        binary_val_swarco_for_write_PTC2, binary_val_swarco_F009

    # if flag_save_conflicts_to_PTC2:
    #     conflict_groups_F992 = make_number_coflicts_group_for_swarco_F992(matrix_swarco_F997)
    #     write_conflicts_to_file(path_and_name_for_txt_conflicts=name_for_txt_conflicts,
    #                             sorted_stages=sorted_stages, matrix_swarco_F997=matrix_swarco_F997,
    #                             binary_val_swarco_F009=binary_val_swarco_F009,
    #                             binary_val_swarco_for_write_PTC2=binary_val_swarco_for_write_PTC2,
    #                             kolichestvo_napravleniy=kolichestvo_napr,
    #                             matrix_output=matrix_output, conflict_groups_F992=conflict_groups_F992,
    #                             flag_save_conflicts_to_PTC2=True, path_to_original_PTC2=path_to_original_PTC2,
    #                             path_to_new_PTC2=path_to_config_file)
    # elif flag_save_conflicts_to_dat_peek:
    #     conflict_groups_F992 = make_number_coflicts_group_for_swarco_F992(matrix_swarco_F997)
    #     write_conflicts_to_file(path_and_name_for_txt_conflicts=name_for_txt_conflicts,
    #                             sorted_stages=sorted_stages, matrix_swarco_F997=matrix_swarco_F997,
    #                             binary_val_swarco_F009=binary_val_swarco_F009,
    #                             binary_val_swarco_for_write_PTC2=binary_val_swarco_for_write_PTC2,
    #                             kolichestvo_napravleniy=kolichestvo_napr,
    #                             matrix_output=matrix_output, conflict_groups_F992=conflict_groups_F992,
    #                             flag_save_conflicts_to_PTC2=False, path_to_original_PTC2=path_to_original_PTC2,
    #                             path_to_new_PTC2=path_to_config_file)
    #     make_dat_file_for_peek(conflict_groups_F992)
    #
    # elif conflicts_and_binVal_swarco_for_txt:
    #     conflict_groups_F992 = make_number_coflicts_group_for_swarco_F992(matrix_swarco_F997)
    #     write_conflicts_to_file(path_and_name_for_txt_conflicts=name_for_txt_conflicts,
    #                             sorted_stages=sorted_stages, matrix_swarco_F997=matrix_swarco_F997,
    #                             binary_val_swarco_F009=binary_val_swarco_F009, kolichestvo_napravleniy=kolichestvo_napr,
    #                             matrix_output=matrix_output, conflict_groups_F992=conflict_groups_F992,
    #                             flag_conflicts_swarco=conflicts_and_binVal_swarco_for_txt
    #                             )
    # else:
    #     write_conflicts_to_file(path_and_name_for_txt_conflicts=name_for_txt_conflicts,
    #                             sorted_stages=sorted_stages,
    #                             kolichestvo_napravleniy=kolichestvo_napr,
    #                             matrix_output=matrix_output,
    #                             )

    # if flag_conflicts_swarco:
    #     return matrix_swarco_F997, matrix_output,
    # conflicts_F992 = make_number_coflicts_group_for_swarco_F992(matrix_swarco_F997)


# def write_conflicts_to_file(path_and_name_for_txt_conflicts=None, sorted_stages=None, matrix_swarco_F997=None,
#                             binary_val_swarco_F009=None, binary_val_swarco_for_write_PTC2=None,
#                             kolichestvo_napravleniy=None,  matrix_output=None,
#                             conflict_groups_F992=None,flag_conflicts_swarco=None, flag_save_conflicts_to_PTC2=None,
#                             path_to_original_PTC2 = None, path_to_new_PTC2 = None):
#     """Функция производит запись вычесленных ранее ""Матрица конфликтов "интергрин" F997",
#        "Физические конфликты - номера конфликтных групп F992", "Сигнальные группы в фазах F009"(бинарные значения)
#        в файл по указанному пользевателем каталогу"""
#     # Запись значений в файл
#
#     with open(path_and_name_for_txt_conflicts, 'w') as file:
#         # Запишем в файл общую информацию: Фазы-Направления
#         num_stage = 1
#         for stage in sorted_stages:
#             if stage:
#                 file.write(f"Фаза {num_stage}: ")
#                 check_last_item = 1
#             else:
#                 file.write(f"Фаза {num_stage}:\n")
#                 num_stage += 1
#                 continue
#             for num_napravleniya in stage:
#                 if check_last_item == len(stage):
#                     file.write(f'{num_napravleniya}\n')
#                 else:
#                     file.write(f'{num_napravleniya}, ')
#                     check_last_item += 1
#             num_stage += 1
#         file.write(f'Количество направлений: {kolichestvo_napravleniy}\n\n')
#
#         # Общая "Матрица конфликтов"
#         for stroka_napravleine in range(kolichestvo_napravleniy + 1):
#             file.write(f'{" ".join(matrix_output[stroka_napravleine])}\n')
#         file.write('\n')
#
#         if flag_save_conflicts_to_PTC2 is None and flag_conflicts_swarco is None:
#             return
#         # Запишем в файл "Матрица конфликтов "интергрин" F997"
#         file.write('Матрица конфликтов "интергрин" F997:\n')
#         for num_napravleniya in matrix_swarco_F997:
#             for stroka_napravlenie in num_napravleniya:
#                 file.write(stroka_napravlenie)
#             file.write('\n')
#         file.write('\n')
#
#         # Запишем в файл "Физические конфликты - номера конфликтных групп F992"
#         file.write('Физические конфликты - номера конфликтных групп F992:\n')
#         for num_napravleniya in conflict_groups_F992:
#             for stroka_napravlenie in num_napravleniya:
#                 file.write(stroka_napravlenie)
#             file.write('\n')
#         file.write('\n')
#
#         # Запишем в файл "Сигнальные группы в фазах F009"(,бинарные значения)
#         file.write('Сигнальные группы в фазах F009: \n')
#         for num_napravleniya in binary_val_swarco_F009:
#             for val in num_napravleniya:
#                 file.write(val)
#
#
#     if flag_save_conflicts_to_PTC2:
#         make_PTC2_file(matrix_swarco_F997=matrix_swarco_F997,
#                        binary_val_swarco_for_write_PTC2=binary_val_swarco_for_write_PTC2,
#                        path_to_original_PTC2=path_to_original_PTC2,
#                        path_to_new_PTC2=path_to_new_PTC2)


def write_conflicts_to_txt_file(path_and_name_for_txt_conflicts=None, sorted_stages=None, matrix_swarco_F997=None,
                                binary_val_swarco_F009=None, kolichestvo_napravleniy=None, matrix_output=None,
                                conflict_groups_F992=None, conflicts_and_binVal_swarco=False):
    """Функция производит запись вычесленных ранее ""Матрица конфликтов "интергрин" F997",
       "Физические конфликты - номера конфликтных групп F992", "Сигнальные группы в фазах F009"(бинарные значения)
       в файл по указанному пользевателем каталогу"""
    # Запись значений в файл

    with open(path_and_name_for_txt_conflicts, 'w') as file:
        # Запишем в файл общую информацию: Фазы-Направления
        num_stage = 1
        for stage in sorted_stages:
            if stage:
                file.write(f"Фаза {num_stage}: ")
                check_last_item = 1
            else:
                file.write(f"Фаза {num_stage}:\n")
                num_stage += 1
                continue
            for num_napravleniya in stage:
                if check_last_item == len(stage):
                    file.write(f'{num_napravleniya}\n')
                else:
                    file.write(f'{num_napravleniya}, ')
                    check_last_item += 1
            num_stage += 1
        file.write(f'Количество направлений: {kolichestvo_napravleniy}\n\n')

        # Общая "Матрица конфликтов"
        for stroka_napravleine in range(kolichestvo_napravleniy + 1):
            file.write(f'{" ".join(matrix_output[stroka_napravleine])}\n')
        file.write('\n')

        if not conflicts_and_binVal_swarco:
            return True
        # Запишем в файл "Матрица конфликтов "интергрин" F997"
        file.write('Матрица конфликтов "интергрин" F997:\n')
        for num_napravleniya in matrix_swarco_F997:
            for stroka_napravlenie in num_napravleniya:
                file.write(stroka_napravlenie)
            file.write('\n')
        file.write('\n')

        # Запишем в файл "Физические конфликты - номера конфликтных групп F992"
        file.write('Физические конфликты - номера конфликтных групп F992:\n')
        for num_napravleniya in conflict_groups_F992:
            for stroka_napravlenie in num_napravleniya:
                file.write(stroka_napravlenie)
            file.write('\n')
        file.write('\n')

        # Запишем в файл "Сигнальные группы в фазах F009"(,бинарные значения)
        file.write('Сигнальные группы в фазах F009: \n')
        for num_napravleniya in binary_val_swarco_F009:
            for val in num_napravleniya:
                file.write(val)
        return True


# def make_PTC2_file(path_to_original_PTC2=None, path_to_new_PTC2=None, matrix_swarco_F997=None,
#                    binary_val_swarco_for_write_PTC2=None):
#     print(f'ya v make_PTC2_file')
#
#     with open(path_to_original_PTC2) as file, open(path_to_new_PTC2, 'w') as new_file:
#         flag1 = False
#         flag2 = False
#         flag3 = False
#         for line in file:
#             if flag1:
#                 if 'NeXt' not in line:
#                     new_file.write('')
#                 else:
#                     flag1 = False
#             elif flag2:
#                 if 'NeXt' not in line:
#                     new_file.write('')
#                 else:
#                     flag2 = False
#             elif flag3:
#                 if 'NeXt' not in line:
#                     new_file.write('')
#                 else:
#                     flag3 = False
#
#             if 'NewSheet693  : Work.997' in line:
#                 flag1 = True
#                 new_file.write(line)
#                 for group_line in matrix_swarco_F997:
#                     new_file.write(''.join(group_line))
#                     new_file.write('\n')
#             elif 'NewSheet693  : Work.992' in line:
#                 flag2 = True
#                 new_file.write(line)
#                 for group_line in matrix_swarco_F997:
#                     new_file.write(''.join(group_line))
#                     new_file.write('\n')
#             elif 'NewSheet693  : Work.009' in line:
#                 flag3 = True
#                 new_file.write(line)
#                 for group_line in binary_val_swarco_for_write_PTC2:
#                     new_file.write(''.join(group_line))
#                     new_file.write('\n')
#             elif not flag1 and not flag2 and not flag3:
#                 new_file.write(line)


def make_PTC2_file(path_to_original_PTC2=None, matrix_swarco_F997=None, binary_val_swarco_for_write_PTC2=None):
    path_to_new_PTC2 = make_path_to_save_config(path_to_original_PTC2)

    with open(path_to_original_PTC2) as file, open(path_to_new_PTC2, 'w') as new_file:

        flag1 = flag2 = flag3 = flag4 = False

        for line in file:
            if flag1:
                if 'NeXt' not in line:
                    new_file.write('')
                else:
                    flag1 = False
            elif flag2:
                if 'NeXt' not in line:
                    new_file.write('')
                else:
                    flag2 = False
            elif flag3:
                if 'NeXt' not in line:
                    new_file.write('')
                else:
                    flag3 = False
            elif flag4:
                if 'NeXt' not in line:
                    new_file.write('')
                else:
                    flag4 = False

            if 'NewSheet693  : Work.997' in line:
                flag1 = True
                new_file.write(line)
                for group_line in matrix_swarco_F997:
                    new_file.write(''.join(group_line))
                    new_file.write('\n')
            elif 'NewSheet693  : Work.992' in line:
                flag2 = True
                new_file.write(line)
                for group_line in matrix_swarco_F997:
                    new_file.write(''.join(group_line))
                    new_file.write('\n')
            elif 'NewSheet693  : Work.009' in line:
                flag3 = True
                new_file.write(line)
                for group_line in binary_val_swarco_for_write_PTC2:
                    new_file.write(''.join(group_line))
                    new_file.write('\n')
            elif 'NewSheet693  : Work.006' in line:
                flag4 = True
                new_file.write(line)
            elif not flag1 and not flag2 and not flag3 and not flag4:
                new_file.write(line)
    return True


def make_dat_file_for_peek(conflicts: list, sum_conflicts: int, sorted_stages: list, path_to_original_DAT: str):
    sum_stages = len(sorted_stages)
    new_file_dat = make_path_to_save_config(path_to_original_DAT)

    table_conflicts = f':TABLE "XSGSG",{str(sum_conflicts)},4,3,4,4,3\n'
    table_SA_STG = f':TABLE "YSRM_SA_STG",{str(sum_stages)},2,4,10\n'
    table_UK_STAGE = f':TABLE "YSRM_UK_STAGE",{str(sum_stages)},4,4,4,1,10\n'

    with open(path_to_original_DAT, 'r', encoding='utf-8') as file1, open(new_file_dat, 'w', encoding='utf-8') as file2:
        flag1 = flag2 = flag3 = False
        count = 0
        for line in file1:
            if flag1 and 'TABLE "YKLOK"' not in line:
                pass
            elif flag1 and 'TABLE "YKLOK"' in line:
                flag1 = False
                count += 1
                file2.write(':END\n')
                file2.write(line)
            elif ':TABLE "XSGSG"' in line:
                file2.write(table_conflicts)
                for num_group_from in range(len(conflicts)):
                    for num_group_to in conflicts[num_group_from]:
                        file2.write(f':RECORD\n'
                                    f'"Type",2\n'
                                    f'"Id1",{str(num_group_from + 1)}\n'
                                    f'"Id2",{str(num_group_to)}\n'
                                    f'"Time",30\n'
                                    f':END\n')
                flag1 = True


            elif flag2 and ':TABLE "YSRM_STEP"' not in line:
                pass
            elif flag2 and ':TABLE "YSRM_STEP"' in line:
                flag2 = False
                count += 1
                file2.write(':END\n')
                file2.write(line)
            elif ':TABLE "YSRM_SA_STG"' in line:
                file2.write(table_SA_STG)
                for num_stage in range(len(sorted_stages)):
                    stage = ','.join(list(map(str, sorted_stages[num_stage])))
                    file2.write(f':RECORD\n'
                                f'"Id",{str(num_stage + 1)}\n'
                                f'"SGdef","{stage}"\n'
                                f':END\n')
                flag2 = True

            elif flag3 and '"YSRM_UK_STAGE_TRANS"' not in line:
                pass
            elif flag3 and '"YSRM_UK_STAGE_TRANS"' in line:
                flag3 = False
                count += 1
                file2.write(':END\n')
                file2.write(line)
            elif ':TABLE "YSRM_UK_STAGE"' in line:
                file2.write(table_UK_STAGE)
                for num_stage in range(len(sorted_stages)):
                    stage = ','.join(list(map(str, sorted_stages[num_stage])))
                    file2.write(f':RECORD\n'
                                f'"ProcessId",1\n'
                                f'"StageId",{str(num_stage + 1)}\n'
                                f'"StartUpStage",{str(True) if num_stage == 0 else str(False)}\n'
                                f'"SignalGroups",",{stage},"\n'
                                f':END\n')
                flag3 = True

            else:
                file2.write(line)
    return True


def check_charchter(chars):
    new_list_chars = []

    for i in range(len(chars)):
        stroka = ''
        for char in chars[i]:
            if char.isdigit() or char == ',':
                stroka = stroka + char
        if stroka != '':
            new_list_chars.append(stroka)
        print(new_list_chars)
    return new_list_chars


def convert_scn(SCN):
    """ Функция получает на вход строку, которую необходимо конвертировать в SCN
        для управления и мониторинга по протоколу UG405.
        Например: convert_scn(CO1111)
    """
    len_scn = str(len(SCN)) + '.'
    convert_to_ASCII = [str(ord(c)) for c in SCN]
    scn = f'.1.{len_scn}{".".join(convert_to_ASCII)}'
    return scn


def check_host_tcp(ip_adress: str, port=80, timeout=2):
    """
        Функция проверят наличие связи через socket с хостом. При наличии свзяи возвращает True, при отсутствии
        связи пишет в лог ошибку и возвращает False
    """
    try:
        socket.setdefaulttimeout(timeout)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip_adress, port))
    except OSError as error:
        return False
    else:
        return True


# def make_S79UG405init(ip_adress_for_filter_snmp='anywhere', write_iptables_to_S79UG405init=True):
#
#     if ip_adress_for_filter_snmp == 'anywhere':
#         iptables_input = f'    iptables -A INPUT -p udp --dport 161 -j DROP \n'
#         iptables_forward = f'    iptables -A FORWARD -p udp --dport 161 -j DROP \n'
#     else:
#         iptables_input = f'    iptables -A INPUT -p udp --dport 161 -s {ip_adress_for_filter_snmp} -j DROP \n'
#         iptables_forward = f'    iptables -A FORWARD -p udp --dport 161 -s {ip_adress_for_filter_snmp} -j DROP \n'
#
#     if write_iptables_to_S79UG405init:
#         with open(configuration.path_to_S79UG405init_ishodniy, 'r') as file_get_data, \
#                 open(configuration.path_to_S79UG405init, 'w') as file_write_data:
#             for line in file_get_data:
#                 if configuration.desired_line_in_path_to_S79UG405init_ishodniy in line:
#                     file_write_data.write(line)
#                     file_write_data.write(f'{iptables_input}{iptables_forward}')
#                 else:
#                     file_write_data.write(line)
#     else:
#         with open(configuration.path_to_S79UG405init_ishodniy, 'r') as file_get_data, \
#                 open(configuration.path_to_S79UG405init, 'w') as file_write_data:
#             content = file_get_data.read()
#             file_write_data.write(content)
#
#     replace_windows_line_ending_to_unix_line_ending(configuration.path_to_S79UG405init)


def replace_windows_line_ending_to_unix_line_ending(path_to_file):
    """ Функция заменяет переводы строк CRLF(Windows) на  LF(Unix) в файле по пути: path_to_file """

    WINDOWS_LINE_ENDING = b'\r\n'
    UNIX_LINE_ENDING = b'\n'

    with open(path_to_file, 'rb') as file:
        content = file.read()
    content = content.replace(WINDOWS_LINE_ENDING, UNIX_LINE_ENDING)

    with open(path_to_file, 'wb') as file:
        file.write(content)


def logger(path_to_file_log=None, message='-', flag='-', ip_adress='-', session_time=None):
    """ Функция, делающая запись в файл лог сессии ssh
        flile - название файла, в котрорый пишется лог
        message - сообщение для лога
        flag - флаг, который помогает понять необходимо делать перенос строки при записи
    """
    if path_to_file_log is None:
        return

    if flag == 'zagolovok':
        with open(path_to_file_log, 'a') as file_log:
            file_log.write(f'\n{"*" * 75}\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")}{message}\n')
    elif flag == 'ssh_set_inp_outp_Mreg':
        with open(path_to_file_log, 'a', encoding='latin-1') as file_log:
            file_log.write(f'\n{message}\n'
                           f'{datetime.today().strftime("%Y-%m-%d %H:%M:%S")}\n')
    elif flag == 'new_standart':
        with open(path_to_file_log, 'a') as file_log:
            file_log.write(f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} {message}')
    elif flag == 'standart':
        with open(path_to_file_log, 'a') as file_log:
            file_log.write(f'{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} < {message} >\n')
    elif flag == 'msg_from_ssh':
        with open(path_to_file_log, 'a') as file_log:
            file_log.write(f'{datetime.today().strftime("%Y-%m-%d %H:%M:%S")}:\n{message}\n')
    elif flag == 'put_log_to_ftp_laba_out':
        with open(path_to_file_log, 'a') as file_log:
            file_log.write(f'{datetime.datetime.now()} '
                           f'< Загрузка лога на ноут_лаба 192.168.45.163: {message} >\n')
    elif flag == 'stcip_json':
        with open(path_to_file_log, 'a') as file_log:
            file_log.write(f'\n\n{message}\n')


def sorting_data_for_greenroad_web_peek(unsorted_list):
    sorted_data_for_intersection = []
    for item in unsorted_list:
        sorted_data_for_intersection.append(item.split('='))

    print(f'sorted_data_for_intersection: {sorted_data_for_intersection}')
    return sorted_data_for_intersection


# def sorting_data_for_greenroad_web_peek(unsorted_list):
#     sorted_data_for_intersection = []
#     for num, item in enumerate(unsorted_list, 1):
#         if num < 4:
#             sorted_data_for_intersection.append(item)
#         else:
#             tmp = item.split('=')
#             sorted_data_for_intersection.append(tmp)
#     print(f'sorted_data_for_intersection: {sorted_data_for_intersection}')
#     return sorted_data_for_intersection


def sorting_data_for_greenroad_swarco_ssh(unsorted_list):
    sorted_data_for_intersection = []
    for num, item in enumerate(unsorted_list, 1):
        if num < 6:
            sorted_data_for_intersection.append(item)
        else:
            tmp = item.split('=')
            print(tmp)
            sorted_data_for_intersection.append(tmp)
    return sorted_data_for_intersection


def time_repr(seconds: int):
    minutes = seconds // 60
    seconds = seconds % 60
    return str(minutes), str(seconds)


def write_to_log(path_to_log, message):
    with open(path_to_log, 'a') as file:
        file.write(f'\n{datetime.today().strftime("%Y-%m-%d %H:%M:%S")} {message}')


def get_index_of_host(string: str) -> int:
    """ Функция получает на вход строку с названием виджета, котором последний/последние символы - его номер(индекс)
        и возвращает индекс(отрез)
    """

    index_has_two_symbols = string[-2:]
    if index_has_two_symbols.isdigit():
        return int(index_has_two_symbols) - 1
    else:
        return int(string[-1]) - 1


def make_va_and_ft_transitions(dat_file):
    with open(dat_file, 'r') as file:
        va = []
        ft = []
        cnt = 0
        flag_table_trans_stage = flag_va = flag_ft = flag_write_record = False

        for line in file:

            if ':TABLE "YSRM_VPLAN_PARM"' in line:
                break

            if ':TABLE "YSRM_UK_STAGE_TRANS"' in line:
                flag_table_trans_stage = True
                continue
            if not flag_table_trans_stage:
                continue

            if flag_table_trans_stage and ':RECORD' in line:
                cnt += 1
                string = line
            elif flag_table_trans_stage and '"TransId"' in line:
                # Номер transition "TransId",
                trans_id = line.strip().split(',')[1]
                string += line
            elif flag_table_trans_stage and '"ModeOfOpp",5' in line:
                flag_va = True
                string += line
            elif flag_table_trans_stage and '"ModeOfOpp",6' in line:
                flag_ft = True
                string += line
            elif flag_table_trans_stage and ':END' in line:
                if flag_va:
                    string += line
                    va.append(string)
                    flag_va = False
                    string = ''
                elif flag_ft:
                    string += line
                    ft.append(string)
                    flag_ft = False
                    string = ''
                else:
                    continue
            else:

                string += line

    return va, ft


def make_utc_and_man_transitions(num_stages):
    utc_transitions = []
    man_transitions = []
    num_transition = 1

    for j in range(1, num_stages + 1):
        for i in range(1, num_stages + 1):
            if j == i:
                continue
            if i != j:
                utc_trans = (
                    f':RECORD\n'
                    f'"ProcessId",1\n'
                    f'"TransId",{num_transition}\n'
                    f'"ModeOfOpp",1\n'
                    f'"FromStage",{j}\n'
                    f'"ToStage",{i}\n'
                    f'"DemandCondition","utc_STG({j},{i})"\n'
                    f'"ExtensionCondition",""\n'
                    f'"InhibitionCondition","utc_i_STG({j},{i})"\n'
                    f':END\n'
                )

                man_tr = (f':RECORD\n'
                          f'"ProcessId",1\n'
                          f'"TransId",{num_transition}\n'
                          f'"ModeOfOpp",3\n'
                          f'"FromStage",{j}\n'
                          f'"ToStage",{i}\n'
                          f'"DemandCondition","man_STG({j},{i})"\n'
                          f'"ExtensionCondition",""\n'
                          f'"InhibitionCondition",""\n'
                          f':END\n'
                          )

                utc_transitions.append(utc_trans)
                man_transitions.append(man_tr)

                # print(f'{j} >> {i}')
            num_transition += 1
    return utc_transitions, man_transitions


def make_dat_file_with_utc_and_man_transitions(path_to_dat_file, num_stages):
    path_to_new_dat = make_path_to_save_config(path_to_dat_file)

    all_va_transitions, all_ft_transitions = make_va_and_ft_transitions(path_to_dat_file)
    all_utc_transitions, all_man_transitions = make_utc_and_man_transitions(num_stages)

    num_transitions = (len(all_utc_transitions) + len(all_man_transitions) + len(all_va_transitions) +
                       len(all_ft_transitions))

    with open(path_to_dat_file, 'r') as file_from, open(path_to_new_dat, 'w') as file_to:
        flag = False
        for line in file_from:
            if not flag and ':TABLE "YSRM_UK_STAGE_TRANS"' not in line:
                file_to.write(line)

            if ':TABLE "YSRM_UK_STAGE_TRANS"' in line:
                flag = True
                file_to.write(f':TABLE "YSRM_UK_STAGE_TRANS",{num_transitions},8,4,4,4,4,4,10,10,10\n')

                for utc_tr, man_tr, va_tr, ft_tr in itertools.zip_longest(
                        all_utc_transitions, all_man_transitions, all_va_transitions, all_ft_transitions):
                    if utc_tr is not None:
                        file_to.write(utc_tr)
                    if man_tr is not None:
                        file_to.write(man_tr)
                    if va_tr is not None:
                        file_to.write(va_tr)
                    if ft_tr is not None:
                        file_to.write(ft_tr)
                continue

            if flag == True:
                pass

            if ':TABLE "YSRM_VPLAN_PARM"' in line:
                file_to.write(':END\n')
                file_to.write(line)
                flag = False


def range_for_label_new_greenroad(span=4):
    cnt = 0
    range_to_change_label = []
    while cnt < 60:
        range_to_change_label += list(range(cnt, cnt + span))
        cnt += span * 2
    return range_to_change_label


def check_query(query, desired_text):

    valid_data = query.get(desired_text)

    if desired_text in query and valid_data is not None and valid_data.strip():
        return True
    return False

# key = b'some_key'
#
# def encrypt(filename, key):
#     f = Fernet(key)
#     with open(filename, 'rb') as file:
#         file_data = file.read()
#         encrypted_data = f.encrypt(file_data)
#     with open(filename, 'wb') as file:
#         file.write(encrypted_data)


