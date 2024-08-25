
def make_json_to_front(host, protocol=None):

    status_mode = {
        '8': 'Адаптивный',
        '10': 'Ручное управление',
        '11': 'Удалённое управление',
        '12': 'Фиксированный',
        '00': 'Ошибка электрической цепи',
        '--': 'Нет данных',
    }

    vals = (None, 'None')

    mode = status_mode.get(host.get_mode())
    print(f'mode from base: {mode}')
    curr_stage = host.get_stage()
    curr_plan = host.get_plan()

    """ New ver """
    if curr_stage in vals and curr_plan in vals:
        json_data = 'Фаза= План= Режим=Аварийный'
        return json_data
    if curr_stage in vals or curr_plan in vals:
        json_data = f'Фаза={curr_stage} План={curr_plan} Режим=Нет данных'
    else:
        print(f'host.ip_adress: {host.ip_adress}' )
        json_data = f'Фаза={curr_stage} План={curr_plan} Режим={mode}'
    return json_data

    """ Old ver """
    if curr_stage in vals and curr_plan in vals:
        json_data = {
            'Фаза': '--',
            'План': '--',
            'Режим': 'Аварийный',
        }
        return json_data
    if curr_stage in vals or curr_plan in vals:
        json_data = {
            'Фаза': curr_stage,
            'План': curr_plan,
            'Режим': 'Нет данных',
        }
    else:
        print(f'host.ip_adress: {host.ip_adress}' )
        json_data = {
            'Фаза': curr_stage,
            'План': curr_plan,
            'Режим': mode,
        }
    return json_data


