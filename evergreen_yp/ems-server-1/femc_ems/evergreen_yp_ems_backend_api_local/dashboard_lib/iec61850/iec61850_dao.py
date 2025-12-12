import os
import sys
import ctypes
import time
from ctypes import (
    c_void_p,
    c_char_p,
    c_int,
    c_float,
    c_bool,
    c_int32,
    c_uint64,
    POINTER,
    byref,
)
from typing import Dict, Optional, List

from dashboard_lib.constant import ConfigConstant
from dashboard_lib.iec61850.iec61850_const import FC, DataType
from logging_utils import Logger


MmsValue = c_void_p
IedConnection = c_void_p
IedClientError = c_int
FunctionalConstraint = c_int
ControlObjectClient = c_void_p


class IEC61850Dao:
    """
    libiec61850 ctypes DAO：
    - 讀取 Int/Float/Bool/DBPOS
    - 控制 (DIRECT / SBO / ENHANCED)
    """
    MMS_BIT_STRING_VAL = 3
    MMS_ARRAY_VAL = 15

    @staticmethod
    def _decode_error(err: int) -> str:
        mapping = {
            0: "IED_ERROR_OK",
            1: "IED_ERROR_NOT_CONNECTED",
            2: "IED_ERROR_ALREADY_CONNECTED",
            3: "IED_ERROR_CONNECTION_LOST",
            4: "IED_ERROR_SERVICE_NOT_SUPPORTED",
            5: "IED_ERROR_CONNECTION_REJECTED",
            10: "IED_ERROR_USER_PROVIDED_INVALID_ARGUMENT",
            11: "IED_ERROR_ENABLE_REPORT_FAILED_DATASET_MISMATCH",
            12: "IED_ERROR_OBJECT_REFERENCE_INVALID",
            13: "IED_ERROR_UNEXPECTED_VALUE_RECEIVED",
            20: "IED_ERROR_TIMEOUT",
            21: "IED_ERROR_ACCESS_DENIED",
            22: "IED_ERROR_OBJECT_DOES_NOT_EXIST",
            23: "IED_ERROR_OBJECT_EXISTS",
            24: "IED_ERROR_OBJECT_ACCESS_UNSUPPORTED",
            25: "IED_ERROR_TYPE_INCONSISTENT",
            26: "IED_ERROR_TEMPORARILY_UNAVAILABLE",
            27: "IED_ERROR_OBJECT_UNDEFINED",
            28: "IED_ERROR_INVALID_ADDRESS",
            29: "IED_ERROR_HARDWARE_FAULT",
            30: "IED_ERROR_TYPE_UNSUPPORTED",
            31: "IED_ERROR_OBJECT_ATTRIBUTE_INCONSISTENT",
            32: "IED_ERROR_OBJECT_VALUE_INVALID",
            33: "IED_ERROR_OBJECT_INVALIDATED",
            34: "IED_ERROR_MALFORMED_MESSAGE",
            35: "IED_ERROR_OBJECT_CONSTRAINT_CONFLICT",
        }
        return mapping.get(err, f"UNKNOWN_ERROR_{err}")

    @staticmethod
    def _parse_fc(fc_val) -> FC:
        if isinstance(fc_val, FC):
            return fc_val
        if isinstance(fc_val, int):
            return FC(fc_val)
        if isinstance(fc_val, str):
            return FC[fc_val]
        # 預設 ST
        return FC.ST

    def __init__(self, config, **kwargs):
        setting_config = config[ConfigConstant.APP.value]
        log_path = setting_config[ConfigConstant.LOG_PATH.value]

        logging_level = config.get('logging_level') or kwargs.get('logging_level') or 'INFO'
        host = config.get('uri') or kwargs.get('uri')
        port = config.get('port') or kwargs.get('port')
        timeout = config.get('timeout') or kwargs.get('timeout') or 10

        self.logger = Logger().create('Evergreen API', level=logging_level, log_path=log_path)

        self.config = config
        self.host = host
        self.port = int(port)

        if not self.host or not self.port:
            err_msg = "IEC61850 參數設置錯誤 (HOST / PORT)，請確認設定檔"
            self.logger.error(err_msg)
            raise Exception(err_msg)
        self.port = int(self.port)
        self.timeout: int = int(timeout)

        self._lib = self._load_library()
        self._conn: Optional[IedConnection] = None

        # 建立連線
        self._conn = None

    # -------------------------------------------------------------------------
    # 動態載入 libiec61850
    # -------------------------------------------------------------------------
    def _load_library(self):
        """
        根據平台載入 libiec61850
        - Windows: .../bin/windows/iec61850.dll
        - Linux:   .../bin/linux/libiec61850.so
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))

        if sys.platform.startswith("win"):
            lib_path = os.path.join(base_dir, "", "bin", "windows", "iec61850.dll")
        else:
            lib_path = os.path.join(base_dir, "", "bin", "linux", "libiec61850.so")

        lib_path = os.path.normpath(lib_path)
        self.logger.debug(f"載入 IEC61850 library: {lib_path}")

        try:
            lib = ctypes.CDLL(lib_path)
        except OSError as e:
            self.logger.error(f"無法載入 IEC61850 library: {lib_path}, error={e}")
            raise

        # ---- IedConnection 相關 C 函式 ----
        lib.IedConnection_create.restype = IedConnection
        lib.IedConnection_create.argtypes = []

        lib.IedConnection_connect.restype = None
        lib.IedConnection_connect.argtypes = [
            IedConnection,
            POINTER(IedClientError),
            c_char_p,
            c_int,
        ]

        lib.IedConnection_close.restype = None
        lib.IedConnection_close.argtypes = [IedConnection]

        lib.IedConnection_destroy.restype = None
        lib.IedConnection_destroy.argtypes = [IedConnection]

        if hasattr(lib, "IedConnection_setConnectTimeout"):
            lib.IedConnection_setConnectTimeout.restype = None
            lib.IedConnection_setConnectTimeout.argtypes = [IedConnection, c_int]

        # ---- read / write Int32 ----
        lib.IedConnection_readInt32Value.restype = c_int32
        lib.IedConnection_readInt32Value.argtypes = [
            IedConnection,
            POINTER(IedClientError),
            c_char_p,
            FunctionalConstraint,
        ]

        lib.IedConnection_writeInt32Value.restype = None
        lib.IedConnection_writeInt32Value.argtypes = [
            IedConnection,
            POINTER(IedClientError),
            c_char_p,
            FunctionalConstraint,
            c_int32,
        ]

        # ---- float ----
        if hasattr(lib, "IedConnection_readFloatValue"):
            lib.IedConnection_readFloatValue.restype = c_float
            lib.IedConnection_readFloatValue.argtypes = [
                IedConnection,
                POINTER(IedClientError),
                c_char_p,
                FunctionalConstraint,
            ]

        if hasattr(lib, "IedConnection_writeFloatValue"):
            lib.IedConnection_writeFloatValue.restype = None
            lib.IedConnection_writeFloatValue.argtypes = [
                IedConnection,
                POINTER(IedClientError),
                c_char_p,
                FunctionalConstraint,
                c_float,
            ]

        # ---- bool ----
        if hasattr(lib, "IedConnection_readBooleanValue"):
            lib.IedConnection_readBooleanValue.restype = c_bool
            lib.IedConnection_readBooleanValue.argtypes = [
                IedConnection,
                POINTER(IedClientError),
                c_char_p,
                FunctionalConstraint,
            ]

        if hasattr(lib, "IedConnection_writeBooleanValue"):
            lib.IedConnection_writeBooleanValue.restype = None
            lib.IedConnection_writeBooleanValue.argtypes = [
                IedConnection,
                POINTER(IedClientError),
                c_char_p,
                FunctionalConstraint,
                c_bool,
            ]

        # ---- DBPOS / 通用 MmsValue 相關 ----
        if hasattr(lib, "IedConnection_readObject"):
            lib.IedConnection_readObject.restype = MmsValue
            lib.IedConnection_readObject.argtypes = [
                IedConnection,
                POINTER(IedClientError),
                c_char_p,
                FunctionalConstraint,
            ]

        if hasattr(lib, "MmsValue_getType"):
            lib.MmsValue_getType.restype = c_int
            lib.MmsValue_getType.argtypes = [MmsValue]

        if hasattr(lib, "MmsValue_getBitStringSize"):
            lib.MmsValue_getBitStringSize.restype = c_int
            lib.MmsValue_getBitStringSize.argtypes = [MmsValue]

        if hasattr(lib, "MmsValue_getBitStringAsInteger"):
            lib.MmsValue_getBitStringAsInteger.restype = c_uint64
            lib.MmsValue_getBitStringAsInteger.argtypes = [MmsValue]

        if hasattr(lib, "MmsValue_getArraySize"):
            lib.MmsValue_getArraySize.restype = c_int
            lib.MmsValue_getArraySize.argtypes = [MmsValue]

        if hasattr(lib, "MmsValue_getElement"):
            lib.MmsValue_getElement.restype = MmsValue
            lib.MmsValue_getElement.argtypes = [MmsValue, c_int]

        if hasattr(lib, "MmsValue_clone"):
            lib.MmsValue_clone.restype = MmsValue
            lib.MmsValue_clone.argtypes = [MmsValue]

        if hasattr(lib, "MmsValue_delete"):
            lib.MmsValue_delete.restype = None
            lib.MmsValue_delete.argtypes = [MmsValue]

        # Boolean MmsValue
        if hasattr(lib, "MmsValue_newBoolean"):
            lib.MmsValue_newBoolean.restype = MmsValue
            lib.MmsValue_newBoolean.argtypes = [c_bool]

        # ---- Enhanced security / 結構相關 ----
        if hasattr(lib, "MmsValue_createEmptyStructure"):
            lib.MmsValue_createEmptyStructure.restype = MmsValue
            lib.MmsValue_createEmptyStructure.argtypes = [c_int]

        if hasattr(lib, "MmsValue_setElement"):
            lib.MmsValue_setElement.restype = None
            lib.MmsValue_setElement.argtypes = [MmsValue, c_int, MmsValue]

        if hasattr(lib, "MmsValue_newInteger"):
            lib.MmsValue_newInteger.restype = MmsValue
            lib.MmsValue_newInteger.argtypes = [c_int]

        if hasattr(lib, "MmsValue_newIntegerFromInt32"):
            lib.MmsValue_newIntegerFromInt32.restype = MmsValue
            lib.MmsValue_newIntegerFromInt32.argtypes = [c_int]
            lib.MmsValue_newInteger = lib.MmsValue_newIntegerFromInt32

        if hasattr(lib, "MmsValue_newUtcTime"):
            lib.MmsValue_newUtcTime.restype = MmsValue
            lib.MmsValue_newUtcTime.argtypes = [c_uint64]

        # ---- ControlObjectClient 相關 ----
        if hasattr(lib, "ControlObjectClient_create"):
            lib.ControlObjectClient_create.restype = ControlObjectClient
            lib.ControlObjectClient_create.argtypes = [c_char_p, IedConnection]

            lib.ControlObjectClient_destroy.restype = None
            lib.ControlObjectClient_destroy.argtypes = [ControlObjectClient]

            lib.ControlObjectClient_getControlModel.restype = c_int
            lib.ControlObjectClient_getControlModel.argtypes = [ControlObjectClient]

            lib.ControlObjectClient_select.restype = c_bool
            lib.ControlObjectClient_select.argtypes = [ControlObjectClient]

            lib.ControlObjectClient_operate.restype = c_bool
            lib.ControlObjectClient_operate.argtypes = [
                ControlObjectClient,
                MmsValue,
                c_uint64,
            ]

            lib.ControlObjectClient_getLastError.restype = IedClientError
            lib.ControlObjectClient_getLastError.argtypes = [ControlObjectClient]

        if hasattr(lib, "ControlObjectClient_selectWithValue"):
            lib.ControlObjectClient_selectWithValue.restype = c_bool
            lib.ControlObjectClient_selectWithValue.argtypes = [
                ControlObjectClient,
                MmsValue,
            ]

        if hasattr(lib, "ControlObjectClient_operateWithValue"):
            lib.ControlObjectClient_operateWithValue.restype = c_bool
            lib.ControlObjectClient_operateWithValue.argtypes = [
                ControlObjectClient,
                MmsValue,
                c_uint64,
            ]

        return lib

    # -------------------------------------------------------------------------
    # 連線 & Template 初始化
    # -------------------------------------------------------------------------
    def __connect(self) -> IedConnection:
        self.logger.debug("建立 IEC61850 IedConnection")
        conn = self._lib.IedConnection_create()
        if not conn:
            err_msg = "IedConnection_create 失敗"
            self.logger.error(err_msg)
            raise Exception(err_msg)

        # timeout 如 lib 有提供就設一下
        if hasattr(self._lib, "IedConnection_setConnectTimeout"):
            try:
                self._lib.IedConnection_setConnectTimeout(conn, self.timeout * 1000)
            except Exception:
                pass

        self.logger.debug(f"連線到 IED {self.host}:{self.port}")
        err = IedClientError(0)

        self._lib.IedConnection_connect(
            conn,
            byref(err),
            self.host.encode("utf-8"),
            self.port,
        )

        if err.value != 0:
            err_name = self._decode_error(err.value)
            err_msg = f"IedConnection_connect 失敗, error={err.value} ({err_name})"
            self.logger.error(err_msg)
            self._lib.IedConnection_destroy(conn)
            raise Exception(err_msg)

        self.logger.debug("IEC61850 連線成功")
        return conn

    def _check_client(self):
        if not self._conn:
            self._conn = self.__connect()
            if not self._conn:
                raise Exception("IEC61850 connection 尚未連線或已關閉")

    # -------------------------------------------------------------------------
    # Enhanced security 結構 building
    # -------------------------------------------------------------------------
    def _build_enhanced_security_val(self, bool_value: bool) -> MmsValue:
        # 追蹤所有已分配的指標，用於安全釋放
        allocated_mms_values = []

        required_funcs = [
            "MmsValue_createEmptyStructure",
            "MmsValue_setElement",
            "MmsValue_newInteger",
            "MmsValue_newUtcTime",
            "MmsValue_newBoolean",
        ]
        for fn in required_funcs:
            if not hasattr(self._lib, fn):
                raise Exception(f"Enhanced security not supported, missing {fn} in libiec61850")

        try:
            # 建立頂層 Structure (6 個欄位)
            st = self._lib.MmsValue_createEmptyStructure(6)
            if not st:
                raise Exception("Failed to create top-level MMS Structure.")
            allocated_mms_values.append(st)  # 追蹤頂層指標

            # 0: origin (可以給一個兩元素空 structure)
            origin = self._lib.MmsValue_createEmptyStructure(2)
            if not origin: raise Exception("Failed to create Origin Structure.")
            allocated_mms_values.append(origin)
            self._lib.MmsValue_setElement(st, 0, origin)

            # 1: ctlNum（控制序號，先寫死 1）
            ctl_num = self._lib.MmsValue_newInteger(1)
            if not ctl_num: raise Exception("Failed to create ctlNum.")
            allocated_mms_values.append(ctl_num)
            self._lib.MmsValue_setElement(st, 1, ctl_num)

            # 2: earlierCtlVal
            earlier = self._lib.MmsValue_newBoolean(False)
            if not earlier: raise Exception("Failed to create earlierCtlVal.")
            allocated_mms_values.append(earlier)
            self._lib.MmsValue_setElement(st, 2, earlier)

            # 3: timeOfEntry
            now_sec = int(time.time())
            toe = self._lib.MmsValue_newUtcTime(c_uint64(now_sec))
            if not toe: raise Exception("Failed to create timeOfEntry.")
            allocated_mms_values.append(toe)
            self._lib.MmsValue_setElement(st, 3, toe)

            # 4: check (optional, 先給 0)
            check = self._lib.MmsValue_newInteger(0)
            if not check: raise Exception("Failed to create check.")
            allocated_mms_values.append(check)
            self._lib.MmsValue_setElement(st, 4, check)

            # 5: ctlVal（真正的控制值）
            ctl_val = self._lib.MmsValue_newBoolean(bool_value)
            if not ctl_val: raise Exception("Failed to create ctlVal.")
            allocated_mms_values.append(ctl_val)
            self._lib.MmsValue_setElement(st, 5, ctl_val)

            allocated_mms_values.remove(st)
            return st

        except Exception as e:
            # 如果在任何步驟中發生錯誤，釋放所有已分配的子指標
            self.logger.error(f"Error building enhanced control structure: {e}. Attempting cleanup.")
            for val_ptr in allocated_mms_values:
                if val_ptr and int(val_ptr) != 0:
                    try:
                        self._lib.MmsValue_delete(val_ptr)
                    except Exception as clean_e:
                        self.logger.warning(f"Cleanup failed for pointer {int(val_ptr)}: {clean_e}")
            raise Exception(f"Failed to build enhanced control structure: {e}")

    # -------------------------------------------------------------------------
    # Read/Write
    # -------------------------------------------------------------------------
    def read_attribute(self, path: str, dtype: DataType, fc: FC = FC.ST):
        self._check_client()

        err = IedClientError(0)
        p = path.encode("ascii")
        fc_val = FunctionalConstraint(int(fc))

        if dtype == DataType.Int:
            val = self._lib.IedConnection_readInt32Value(
                self._conn, byref(err), p, fc_val
            )

        elif dtype == DataType.Float:
            if not hasattr(self._lib, "IedConnection_readFloatValue"):
                raise Exception("Float read not supported by this libiec61850 build")
            val = self._lib.IedConnection_readFloatValue(
                self._conn, byref(err), p, fc_val
            )

        elif dtype == DataType.Bool:
            if not hasattr(self._lib, "IedConnection_readBooleanValue"):
                raise Exception("Bool read not supported by this libiec61850 build")
            val = self._lib.IedConnection_readBooleanValue(
                self._conn, byref(err), p, fc_val
            )

        elif dtype == DataType.Dbpos:
            # 1. 先試 Int32 快速路徑
            err = IedClientError(0)
            int_val = self._lib.IedConnection_readInt32Value(
                self._conn, byref(err), p, fc_val
            )
            if err.value == 0:
                return int(int_val) & 0b11  # DBPOS = 2 bits → 0~3

            # 2. 再用 readObject + BitString 解析
            needed = [
                "IedConnection_readObject",
                "MmsValue_getType",
                "MmsValue_getBitStringSize",
                "MmsValue_getBitStringAsInteger",
            ]
            for fn in needed:
                if not hasattr(self._lib, fn):
                    raise Exception(
                        "DBPOS readObject or necessary helpers not supported by this libiec61850 build"
                    )

            if not hasattr(self._lib, "MmsValue_delete"):
                raise Exception("MmsValue_delete missing in library")

            err = IedClientError(0)
            mms_val = self._lib.IedConnection_readObject(
                self._conn, byref(err), p, fc_val
            )

            if (mms_val is None) or (int(mms_val) == 0) or (err.value != 0):
                raise Exception(
                    f"Read DBPOS object failed: err={err.value}, {self._decode_error(err.value)} (Pointer NULL or Read Failed)"
                )

            # clone 防止某些版本 mms_val 生命週期問題
            if hasattr(self._lib, "MmsValue_clone"):
                mms_val_copy = self._lib.MmsValue_clone(mms_val)
                self._lib.MmsValue_delete(mms_val)
                mms_val = mms_val_copy

            try:
                mms_type = self._lib.MmsValue_getType(mms_val)

                # Array 包一層 BitString
                if mms_type == self.MMS_ARRAY_VAL:
                    if not hasattr(self._lib, "MmsValue_getElement"):
                        raise Exception("MmsValue_getElement not available to parse Array DBPOS")

                    array_size = self._lib.MmsValue_getArraySize(mms_val)
                    if array_size < 1:
                        raise Exception(f"MMS Array for DBPOS is empty or size too small: {array_size}")

                    element_mms_val = self._lib.MmsValue_getElement(mms_val, c_int(0))
                    if (element_mms_val is None) or (int(element_mms_val) == 0):
                        raise Exception("MmsValue_getElement failed to return element 0 (Pointer NULL).")

                    element_type = self._lib.MmsValue_getType(element_mms_val)
                    if element_type == self.MMS_BIT_STRING_VAL:
                        mms_val_to_parse = element_mms_val
                    else:
                        raise Exception(
                            f"Array element type error: expected {self.MMS_BIT_STRING_VAL}, got {element_type}"
                        )

                elif mms_type == self.MMS_BIT_STRING_VAL:
                    mms_val_to_parse = mms_val

                else:
                    raise Exception(f"DBPOS readObject returned wrong type: {mms_type}")

                size = self._lib.MmsValue_getBitStringSize(mms_val_to_parse)
                if size < 2:
                    raise Exception(f"DBPOS BitString size too small: {size}")

                raw = self._lib.MmsValue_getBitStringAsInteger(mms_val_to_parse)
                val = int(raw) & 0b11
                return val

            finally:
                if mms_val:
                    self._lib.MmsValue_delete(mms_val)

        else:
            raise Exception("Unsupported read type")

        if err.value != 0:
            raise Exception(f"Read failed: {self._decode_error(err.value)}")

        return val

    def write_attribute(self, path: str, dtype: DataType, value, fc: FC = FC.CO):
        self._check_client()

        err = IedClientError(0)
        p = path.encode("ascii")
        fc_val = FunctionalConstraint(int(fc))

        if dtype == DataType.Int:
            self._lib.IedConnection_writeInt32Value(
                self._conn, byref(err), p, fc_val, c_int32(value)
            )

        elif dtype == DataType.Float:
            if not hasattr(self._lib, "IedConnection_writeFloatValue"):
                raise Exception("Float write not supported by this libiec61850 build")
            self._lib.IedConnection_writeFloatValue(
                self._conn, byref(err), p, fc_val, c_float(value)
            )

        elif dtype == DataType.Bool:
            if not hasattr(self._lib, "IedConnection_writeBooleanValue"):
                raise Exception("Bool write not supported by this libiec61850 build")
            self._lib.IedConnection_writeBooleanValue(
                self._conn, byref(err), p, fc_val, c_bool(value)
            )

        else:
            raise Exception("Unsupported write type")

        if err.value != 0:
            raise Exception(f"Write failed: {self._decode_error(err.value)}")

    def read_by_template(self, template: List) -> Dict[str, object]:
        results: Dict[str, object] = {}

        for pt in (template or []):
            name = pt["name"]
            path = pt["path"]
            type_str = pt.get("type", "int")

            type_map = {
                "int": DataType.Int,
                "float": DataType.Float,
                "bool": DataType.Bool,
                "dbpos": DataType.Dbpos,
            }
            dtype = type_map.get(type_str.lower(), DataType.Int)
            fc = self._parse_fc(pt.get("fc", "ST"))

            try:
                value = self.read_attribute(path, dtype, fc)
                results[name] = value
            except Exception as e:
                results[name] = {"ok": False, "error": str(e)}

        return results

    # -------------------------------------------------------------------------
    # CONTROL
    # -------------------------------------------------------------------------
    # -------------------------------------------------------------------------
    # CONTROL（ctlModel 1/2/3/4，支援 SBO-Enhanced）
    # -------------------------------------------------------------------------
    def execute_control(self, path: str, value: any, timeout_ms: int = 3000):
        """
        path: 可傳 DO / DO.Oper / DO.Oper.ctlVal / DO.ctlVal，例如:
          "REF615HLD0/GGIO1.SPCSO1"
          "REF615HLD0/GGIO1.SPCSO1.ctlVal"
          "REF615H/CTRL.CBCSWI1.PosOpn"
          "REF615H/CTRL.CBCSWI1.PosOpn.Oper"
          "REF615H/CTRL.CBCSWI1.PosOpn.Oper.ctlVal"
        value: True/False 或 0/1

        - ctlModel = 1: direct-with-normal-security
        - ctlModel = 2: sbo-with-normal-security
        - ctlModel = 3: direct-with-enhanced-security (但通常仍吃 boolean)
        - ctlModel = 4: sbo-with-enhanced-security（吃整個 structure）
        """
        self._check_client()

        if not hasattr(self._lib, "ControlObjectClient_create"):
            raise Exception("This libiec61850 build has no ControlObjectClient API")

        # ---- 還原 base path：丟給 ControlObjectClient_create 用 ----
        base = path
        if base.endswith(".Oper.ctlVal"):
            base = base[:-len(".Oper.ctlVal")]
        elif base.endswith(".Oper"):
            base = base[:-len(".Oper")]
        elif base.endswith(".ctlVal"):
            base = base[:-len(".ctlVal")]

        base_bytes = base.encode("utf-8")
        ctrl = self._lib.ControlObjectClient_create(base_bytes, self._conn)

        # fallback：control object 建立失敗，就直接寫 ctlVal（模擬或一些簡化 server）
        if not ctrl:
            self.logger.warning(
                f"ControlObjectClient_create failed for {base}, fallback to direct write {base}.ctlVal"
            )
            try:
                self.write_attribute(f"{base}.ctlVal", DataType.Bool, bool(value), FC.CO)
                return
            except Exception as e:
                raise Exception(f"fallback ctlVal write failed: {e}")

        mms_val = None      # 一般 Boolean 用 (ctlModel 1/2/3)
        enhanced_val = None  # SBO Enhanced 用 (ctlModel 4)

        try:
            # 讀取 control model
            ctl_model = int(self._lib.ControlObjectClient_getControlModel(ctrl))
            self.logger.debug(f"[CONTROL] ctlModel = {ctl_model} for {base}")

            # 0 = status-only (不能控制)
            if ctl_model == 0:
                raise Exception(f"Control model=0 (status-only), DO 不允許控制: {base}")

            # 準備通用的 boolean MMS 值（給 1/2/3，用不到 4）
            if ctl_model in (1, 2, 3):
                if not hasattr(self._lib, "MmsValue_newBoolean"):
                    raise Exception(
                        "MmsValue_newBoolean not available in this libiec61850 build"
                    )
                mms_val = self._lib.MmsValue_newBoolean(c_bool(bool(value)))
                if not mms_val:
                    raise Exception("Failed to allocate MmsValue_newBoolean (returned NULL).")

            # 準備 Enhanced security 結構（給 ctlModel = 4）
            if ctl_model == 4:
                if not hasattr(self._lib, "ControlObjectClient_selectWithValue"):
                    raise Exception("SBO enhanced not supported in this libiec61850 build")
                enhanced_val = self._build_enhanced_security_val(bool(value))
                if not enhanced_val:
                    raise Exception("Failed to allocate enhanced_val structure (returned NULL).")

            # ============ MODE 1: DIRECT NORMAL ============
            if ctl_model == 1:
                ok = self._lib.ControlObjectClient_operate(ctrl, mms_val, c_uint64(0))
                if not ok:
                    err = int(self._lib.ControlObjectClient_getLastError(ctrl))
                    raise Exception(
                        f"DIRECT operate failed ({self._decode_error(err)}, code={err})"
                    )

            # ============ MODE 2: SBO NORMAL ============
            elif ctl_model == 2:
                ok = self._lib.ControlObjectClient_select(ctrl)
                if not ok:
                    err = int(self._lib.ControlObjectClient_getLastError(ctrl))
                    raise Exception(
                        f"SBO select failed ({self._decode_error(err)}, code={err})"
                    )

                ok = self._lib.ControlObjectClient_operate(ctrl, mms_val, c_uint64(0))
                if not ok:
                    err = int(self._lib.ControlObjectClient_getLastError(ctrl))
                    raise Exception(
                        f"SBO operate failed ({self._decode_error(err)}, code={err})"
                    )

            # ============ MODE 3: DIRECT ENHANCED ============
            elif ctl_model == 3:
                # 多數實作仍然吃 boolean，但會在 server 端套用 enhanced 機制
                ok = self._lib.ControlObjectClient_operate(ctrl, mms_val, c_uint64(0))
                if not ok:
                    err = int(self._lib.ControlObjectClient_getLastError(ctrl))
                    raise Exception(
                        f"Direct-Enhanced operate failed ({self._decode_error(err)}, code={err})"
                    )

            # ============ MODE 4: SBO ENHANCED ============
            elif ctl_model == 4:
                # # ======================== MODE 4: 模擬器版本 ========================
                # if not hasattr(self._lib, "ControlObjectClient_selectWithValue"):
                #     raise Exception("SBO enhanced not supported in this libiec61850 build")
                #
                # mms_val = self._lib.MmsValue_newBoolean(c_bool(bool(value)))
                # ok = self._lib.ControlObjectClient_selectWithValue(ctrl, mms_val)
                # if not ok:
                #     err = int(self._lib.ControlObjectClient_getLastError(ctrl))
                #     raise Exception(
                #         f"SBO-Enhanced selectWithValue failed: {self._decode_error(err)}"
                #     )
                #
                # ok = self._lib.ControlObjectClient_operate(ctrl, mms_val, c_uint64(0))
                # if not ok:
                #     err = int(self._lib.ControlObjectClient_getLastError(ctrl))
                #     raise Exception(
                #         f"SBO-Enhanced operate failed: {self._decode_error(err)}"
                #     )
                #
                # # ======================== MODE 4: 實際使用版本 ========================
                # # 先 selectWithValue（帶整個 enhanced 結構）
                # ok = self._lib.ControlObjectClient_selectWithValue(ctrl, enhanced_val)
                # if not ok:
                #     err = int(self._lib.ControlObjectClient_getLastError(ctrl))
                #     raise Exception(
                #         f"SBO-Enhanced selectWithValue failed "
                #         f"({self._decode_error(err)}, code={err})"
                #     )

                # 再 operate（優先用 operateWithValue，有些版本只有 operate）
                if hasattr(self._lib, "ControlObjectClient_operateWithValue"):
                    ok = self._lib.ControlObjectClient_operateWithValue(
                        ctrl, enhanced_val, c_uint64(0)
                    )
                else:
                    ok = self._lib.ControlObjectClient_operate(
                        ctrl, enhanced_val, c_uint64(0)
                    )

                if not ok:
                    err = int(self._lib.ControlObjectClient_getLastError(ctrl))
                    raise Exception(
                        f"SBO-Enhanced operate failed "
                        f"({self._decode_error(err)}, code={err})"
                    )

            else:
                raise Exception(f"Unsupported ctlModel={ctl_model} for {base}")

            # 如果走到這裡，代表控制流程完成（不管 stVal 有沒有更新）
            self.logger.info(
                f"[CONTROL] {base} ({ctl_model}) operate success, value={bool(value)}"
            )

        finally:
            # 回收 ControlObjectClient
            if ctrl:
                try:
                    self._lib.ControlObjectClient_destroy(ctrl)
                except Exception:
                    pass

            # 回收一般 boolean mms_val
            if mms_val and hasattr(self._lib, "MmsValue_delete"):
                try:
                    self._lib.MmsValue_delete(mms_val)
                except Exception:
                    pass

            # 回收 enhanced structure
            if enhanced_val and hasattr(self._lib, "MmsValue_delete"):
                try:
                    self._lib.MmsValue_delete(enhanced_val)
                except Exception:
                    pass

    # -------------------------------------------------------------------------
    # CLOSE
    # -------------------------------------------------------------------------
    def close(self):
        if self._conn:
            self.logger.info("關閉 IEC61850 連線")
            try:
                self._lib.IedConnection_close(self._conn)
                self._lib.IedConnection_destroy(self._conn)
            except Exception as e:
                self.logger.error(f"IedConnection_destroy 失敗: {e}")
            self._conn = None
