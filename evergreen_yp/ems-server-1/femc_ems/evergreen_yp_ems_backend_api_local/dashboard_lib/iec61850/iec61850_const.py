from enum import Enum, IntEnum


class IEC61850ConfigConst(Enum):
    FIELD_ID = 'field_id'
    RESOURCE_ID = 'resource_id'
    PARENT_ID = 'parent_id'
    EQUIPMENT_ID = 'equipment_id'
    SUB_EQUIPMENT_ID_LIST = 'sub_equipment_id_list'
    HOST = 'host'
    PORT = 'port'
    LIB_PATH = 'lib_path'
    TIMEOUT = 'timeout'


class FC(IntEnum):
    ST = 0    # 狀態 (Status)
    MX = 1    # 測值 (Measurements)
    SP = 2    # 設定值 (Setpoint)
    SV = 3    # 替代值 (SubstitutionVal)
    CF = 4    # 設定/參數 (Configuration)
    DC = 5    # metadata/描述 (Description)
    SG = 6    # Setting Group
    SE = 7    # Setting Group Editable
    CO = 12   # 控制 (Control)


class DataType(Enum):
    Bool = "bool"               # 布林值 true/false
    Int = "int"                 # 有號整數
    Uint = "uint"               # 無號整數
    Float = "float"             # 單精度浮點
    Double = "double"           # 雙精度浮點
    String = "string"           # 文字字串 (VisString / UTF8String)
    Octet = "octet"             # octet-string (bytes)
    BitString = "bitstring"     # bit-string (常用於 Quality)
    Timestamp = "timestamp"     # 8-byte timestamp (MMS binary time)
    Dbpos = "dbpos"


class ControlModel(IntEnum):
    STATUS_ONLY = 0         # 只讀狀態，不允許控制
    DIRECT_NORMAL = 1       # 直接操作
    SBO_NORMAL = 2          # Select-Before-Operate
    DIRECT_ENHANCED = 3     # Direct enhanced
    SBO_ENHANCED = 4        # SBO enhanced
    READ_ONLY = 5           # 僅允許讀，不允許控制


class FolderAndFileConst(Enum):
    LOG_DIR = 'logs'
    CONFIG_FILE = 'config.ini'
    BASE_PATH = 'base_path'
