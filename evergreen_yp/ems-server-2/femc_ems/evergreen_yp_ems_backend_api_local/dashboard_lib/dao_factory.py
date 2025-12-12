from dashboard_lib.constant import ConfigConstant
from dashboard_lib.filesystem.factory import FileSystemDaoFactory
from dashboard_lib.iec61850.factory import IEC61850DaoFactory
from dashboard_lib.modbus.factory import ModbusDaoFactory
from dashboard_lib.mongo.factory import MongoDaoFactory


class StorageFactory:
    def __init__(self, config):
        self.config = config

    def __mssql_dao_factory(self):
        raise NotImplementedError

    def __postgresql_dao_factory(self):
        raise NotImplementedError

    def __mongo_dao_factory(self):
        return MongoDaoFactory(self.config)

    def __modbus_dao_factory(self):
        return ModbusDaoFactory(self.config)

    def __filesystem_dao_factory(self):
        return FileSystemDaoFactory(self.config)

    def __iec61850_dao_factory(self):
        return IEC61850DaoFactory(self.config)

    def get_dao_factory(self, using_db=None):
        if using_db is None:
            using_db = self.config[ConfigConstant.STORAGE.value][ConfigConstant.USING.value]
        if using_db == ConfigConstant.POSTGRES.value:
            return self.__postgresql_dao_factory()
        elif using_db == ConfigConstant.MONGODB.value:
            return self.__mongo_dao_factory()
        elif using_db == ConfigConstant.MSSQL.value:
            return self.__mssql_dao_factory()
        elif using_db == ConfigConstant.MODBUS.value:
            return self.__modbus_dao_factory()
        elif using_db == ConfigConstant.FILESYSTEM.value:
            return self.__filesystem_dao_factory()
        elif using_db == ConfigConstant.IEC61850.value:
            return self.__iec61850_dao_factory()
        else:
            raise NotImplementedError
