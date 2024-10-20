from enum import Enum

from toolkit.sdp_lib import controller_management

# print(controller_management.BaseUG405.convert_scn('CO381'))

class Test(Enum):
    A = 1
    B = 2

print(Test(1).value)
