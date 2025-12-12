from abc import ABC, abstractmethod


class AbstractDao(ABC):
    @property
    @abstractmethod
    def logger(self):
        return self._logger

    @logger.setter
    @abstractmethod
    def logger(self, value):
        self._logger = value

    @property
    @abstractmethod
    def config(self):
        return self._config

    @config.setter
    @abstractmethod
    def config(self, value):
        self._config = value

    @abstractmethod
    def __init__(self, config):
        self.logger = None
        self.config = config

    @abstractmethod
    def create(self, data, **kwargs):
        pass

    @abstractmethod
    def read(self, **kwargs):
        pass

    @abstractmethod
    def update(self, **kwargs):
        pass

    @abstractmethod
    def delete(self, **kwargs):
        pass
