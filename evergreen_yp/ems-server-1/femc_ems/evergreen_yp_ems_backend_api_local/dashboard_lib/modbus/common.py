import pyModbusTCP
from pyModbusTCP.client import ModbusClient

from dashboard_lib.constant import ConfigConstant


class Modbus:
    STORAGE = ConfigConstant.MODBUS.value

    def __init__(self, config):
        self.slave_id = 1
        self.config = config

    def connect(self):
        try:
            db_config = self.config[ConfigConstant.STORAGE.value][ConfigConstant.DATABASE.value][self.STORAGE]
            conn_ip = db_config[ConfigConstant.URI.value]
            conn_port = int(db_config[ConfigConstant.PORT.value])
            self.slave_id = int(db_config[ConfigConstant.SLAVE_ID.value])
            client = ModbusClient(
                host=conn_ip, port=conn_port, unit_id=self.slave_id, timeout=0.3, auto_open=True, auto_close=True)
        except KeyError as e:
            raise KeyError(e)
        except Exception as e:
            raise Exception(e)
        return client
