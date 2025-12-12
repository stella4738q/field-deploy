
from abc import ABC

import modbus_tk
import pyModbusTCP

from dashboard_lib.interface.abstract_dao import AbstractGenericDao
from dashboard_lib.modbus.common import Modbus


class ModbusDao(AbstractGenericDao, ABC):
    @property
    def client(self):
        return self._client

    @client.setter
    def client(self, value):
        self._client = value

    @property
    def slave_id(self):
        return self._slave_id

    @slave_id.setter
    def slave_id(self, value):
        self._slave_id = value

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    def __init__(self, config):
        self.config = config
        modbus_obj = Modbus(config)
        self.client: pyModbusTCP.client = modbus_obj.connect()
        self.slave_id = modbus_obj.slave_id

    def update_operate_mode(self, mode):
        self.client.write_single_register(self.slave_id, 3, 1, output_value=mode)
