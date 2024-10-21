from enum import Enum
from toolkit.sdp_lib import controller_management
from engineering_tools import settings

import logging

logger = logging.getLogger(__name__)
from toolkit.sdp_lib import controller_management

# print(controller_management.BaseUG405.convert_scn('CO381'))

a = controller_management.PotokP.convert_val_to_num_stage_set_req('1')
