from abc import ABC

from src.dao.interface.abstract_factory import AbstractDaoFactory
from src.dao.mongo.general.mongodao import MongoDao


class MongoDaoFactory(AbstractDaoFactory, ABC):
    def __init__(self, config):
        super().__init__(config)

    def get_dao(self):
        return MongoDao(self.config)
