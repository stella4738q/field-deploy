from abc import ABC

from src.dao.file_system_dao import FileSystemDao
from src.dao.interface.abstract_factory import AbstractDaoFactory


class FileSystemDaoFactory(AbstractDaoFactory, ABC):
    def __init__(self, config):
        super().__init__(config)

    def get_dao(self):
        return FileSystemDao(self.config)
