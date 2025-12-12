from abc import ABC

from dashboard_lib.iec61850.iec61850_dao import IEC61850Dao
from dashboard_lib.interface.abstract_factory import AbstractDaoFactory


class IEC61850DaoFactory(AbstractDaoFactory, ABC):
    def __init__(self, config):
        super().__init__(config)

    def get_dao(self):
        return IEC61850Dao(self.config)
