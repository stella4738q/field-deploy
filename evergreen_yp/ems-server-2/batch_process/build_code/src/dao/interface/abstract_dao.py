from abc import ABCMeta, abstractmethod

from src.components.batch_result import BatchResult


class AbstractGenericDao(metaclass=ABCMeta):
    @property
    @abstractmethod
    def config(self):
        pass

    def execute(self, **kwargs):
        ...

    def update(self, **kwargs):
        ...
    
    def write_log(self, result: BatchResult):
        ...
