from abc import ABC

from dashboard_lib.filesystem.file_system_dao import FileSystemDao
from dashboard_lib.interface.abstract_factory import AbstractDaoFactory


class FileSystemDaoFactory(AbstractDaoFactory, ABC):
    def __init__(self, config):
        super().__init__(config)

    def get_dao(self):
        return FileSystemDao(self.config)
