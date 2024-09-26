from engineering_tools.settings import SHARED_DESKTOP


def get_val_SHARED_DESKTOP(request):
    print(f'')
    print(f'SHARED_DESKTOP: {SHARED_DESKTOP}')
    return {'SHARED_DESKTOP': SHARED_DESKTOP}
