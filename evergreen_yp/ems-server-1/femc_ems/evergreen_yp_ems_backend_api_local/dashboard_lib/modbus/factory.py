from abc import ABC

from dashboard_lib.interface.abstract_factory import AbstractDaoFactory
from dashboard_lib.modbus.general.modbus_dao import ModbusDao


class ModbusDaoFactory(AbstractDaoFactory, ABC):
    def __init__(self, config):
        super().__init__(config)

    def get_dao(self):
        return ModbusDao(self.config)
