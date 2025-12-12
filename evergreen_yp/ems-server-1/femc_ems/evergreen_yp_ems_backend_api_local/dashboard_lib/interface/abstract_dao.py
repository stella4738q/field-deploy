from abc import ABCMeta, abstractmethod


class AbstractGenericDao(metaclass=ABCMeta):
    @property
    @abstractmethod
    def config(self):
        pass
