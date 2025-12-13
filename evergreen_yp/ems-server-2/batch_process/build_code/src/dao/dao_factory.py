from src.constants.config_const import DataBaseConfigConst, DBType
from src.dao.filesystem.factory import FileSystemDaoFactory
from src.dao.mongo.factory import MongoDaoFactory


class StorageFactory:
    def __init__(self, config):
        self.config = config

    def __mongo_dao_factory(self):
        return MongoDaoFactory(self.config).get_dao()

    def __filesystem_dao_factory(self):
        return FileSystemDaoFactory(self.config).get_dao()

    def get_dao(self):
        db_type = self.config[DataBaseConfigConst.DB_TYPE.value]
        if db_type.lower() == DBType.MONGO.value:
            return self.__mongo_dao_factory()
        elif db_type.lower() == DBType.FILESYSTEM.value:
            return self.__filesystem_dao_factory()
        else:
            raise NotImplementedError
