from enum import Enum


class SystemStatus(Enum):
    NOT_AVAILABLE = -1
    FREE = 0
    MANUAL = 1
    CONTRACT_MODE = 2
    SCHEDULE = 3
    AUTO = 4


def working_status_check(name):
    current_list = ['待機', '運行']
    return name in current_list
