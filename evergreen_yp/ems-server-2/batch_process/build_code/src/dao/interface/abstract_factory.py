from abc import ABCMeta, abstractmethod


class AbstractDaoFactory(metaclass=ABCMeta):
    def __init__(self, config):
        self.config = config

    @abstractmethod
    def get_dao(self):
        ...
