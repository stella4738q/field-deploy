from abc import ABCMeta, abstractmethod


class AbstractDaoFactory(metaclass=ABCMeta):
    def __init__(self, config, key=None):
        self.config = config
        self.key = key

    @abstractmethod
    def get_dao(self):
        ...
