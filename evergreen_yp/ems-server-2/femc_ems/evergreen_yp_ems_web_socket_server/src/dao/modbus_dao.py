import os
from distutils.util import strtobool

from pyModbusTCP.client import ModbusClient

from .abstract_dao import AbstractDao
from ..constants.config_const import SourceConfigConst
from ..constants.foler_and_file_const import FolderAndFileConst
from ..utility.logger import MyLogger


class ModbusDao(AbstractDao):

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, value):
        self._logger = value

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, value):
        self._config = value

    def __init__(self, config):
        log_to_file = bool(strtobool(os.environ.get('LOG_TO_FILE', 'False')))
        my_logger = MyLogger(self.__class__.__name__)
        if log_to_file:
            my_logger.add_file_handler(FolderAndFileConst.LOG_DIR.value)
        self.logger = my_logger.get()
        self.config = config
        self.__init_connect()
        self.__init_template()

    def __init_template(self):
        pass

    def __init_connect(self):
        try:
            self.logger.info('Create modbus client')
            conn_ip = self.config[SourceConfigConst.HOST.value]
            conn_port = int(self.config[SourceConfigConst.PORT.value])
            unit_id = int(self.config[SourceConfigConst.UNIT_ID.value]) \
                if SourceConfigConst.UNIT_ID.value in self.config.keys() else 1
            client = ModbusClient(
                host=conn_ip, port=conn_port, unit_id=unit_id, timeout=1, auto_open=True, auto_close=False)
            self.client = client
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.error('Exception happened when connect to mongodb.')
            self.logger.exception(repr(e))
            raise Exception

    def create(self, **args):
        raise NotImplementedError

    def read(self, **args):
        # self.logger.info('read modbus data ...')
        client = self.client

        func_code = args.get('function_code')
        start_address = args.get('start_address')
        quantity = args.get('quantity')
        field_id = args.get('field_id')
        time = args.get('time')
        resource_id = args.get('resource_id')
        parent_id = args.get('parent_id')
        equipment_id = args.get('equipment_id')
        env_controller = args.get('env_controller')

        if func_code is not None:
            try:
                if not client.is_open:
                    client.open()
                if func_code == 1:
                    message = client.read_coils(start_address, quantity)
                elif func_code == 2:
                    message = client.read_discrete_inputs(start_address, quantity)
                elif func_code == 3:
                    message = client.read_holding_registers(start_address, quantity)
                elif func_code == 4:
                    message = client.read_input_registers(start_address, quantity)
                else:
                    raise KeyError(f'function code: {func_code} is not allow.')
            except KeyError as e:
                self.logger.exception(repr(e))
                if client.is_open:
                    client.close()
                return Exception(e)
            except Exception as e:
                self.logger.exception(repr(e))
                if client.is_open:
                    client.close()
                return Exception(e)
        else:
            try:
                message = self.template.read_all_data(time, field_id, resource_id, parent_id, equipment_id,
                                                      env_controller=env_controller)
            except Exception as e:
                if client.is_open:
                    client.close()
                return e
        return message

    def update(self, func_code: int, start_address: int, data, **args):
        message = None
        client = self.client
        try:
            if not client.is_open:
                client.open()
            if func_code == 5:
                message = client.write_single_coil(start_address, data)
            elif func_code == 15:
                message = client.write_multiple_coils(start_address, data)
            elif func_code == 6:
                message = client.write_single_register(start_address, data)
            elif func_code == 16:
                message = client.write_multiple_registers(start_address, data)
            else:
                raise KeyError(f'function code: {func_code} is not allow.')
        except KeyError as e:
            self.logger.exception(repr(e))
            raise KeyError
        except Exception as e:
            self.logger.exception(repr(e))
            raise Exception
        finally:
            # if client.is_open:
            #     client.close()
            return message

    def delete(self, **args):
        raise NotImplementedError

    def set_heartbeat(self, set_value):
        client = self.client
        if not client.is_open:
            client.open()
        return self.template.set_heartbeat(set_value)
