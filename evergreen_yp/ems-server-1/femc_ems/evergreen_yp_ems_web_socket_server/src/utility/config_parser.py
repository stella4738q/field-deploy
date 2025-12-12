import configparser
import json
import os
import re
from enum import Enum

import yaml
from dotenv import load_dotenv

from .exceptions import LogicError
from .logger import MyLogger
from .utils import check_file_exist
from ..constants.foler_and_file_const import FolderAndFileConst


class ConfigType(Enum):
    YML = 'yml'
    YAML = 'yaml'
    JSON = 'json'
    INI = 'ini'


def ini_parser(file):
    config = configparser.ConfigParser()
    config.read(file)
    config = config._sections
    return config


def json_parser(file):
    with open(file, 'r', encoding='utf8') as json_file:
        config = json.load(json_file)
    return config


def yaml_parser(file):
    with open(file, 'r', encoding='utf8') as yaml_file:
        doc = list(yaml.load_all(yaml_file, Loader=yaml.FullLoader))
    config = doc[0]
    return config


class LoadEnv:
    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = value

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, value):
        self._logger = value

    def __init__(self, file_path, log_to_file=False):
        """
        Load env file to get environment variable.

        file_path: abs file path
        log_to_file: logging to file
        """
        self.file_path = file_path
        my_logger = MyLogger(self.__class__.__name__)
        if log_to_file:
            my_logger.add_file_handler(FolderAndFileConst.LOG_DIR.value)
        self.logger = my_logger.get()

    def load(self):
        self.logger.info('check env file exist or not.')
        check_file_exist(self.logger, self.file_path)

        try:
            self.logger.info('Load env file')
            load_dotenv(self.file_path, override=True)
        except OSError as e:
            self.logger.error(f'OS error occurred trying to load {self.file_path}.')
            self.logger.error(repr(e))
            raise OSError
        except Exception as e:
            self.logger.error(f'Unexpected exception when trying to load {self.file_path}')
            self.logger.error(repr(e))
            raise Exception('Load env file')


class ConfigParser:
    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, value):
        self._logger = value

    def __init__(self, env_file_path=None, log_to_file=False):
        my_logger = MyLogger(self.__class__.__name__)
        if log_to_file:
            my_logger.add_file_handler(FolderAndFileConst.LOG_DIR.value)
        self.logger = my_logger.get()
        if env_file_path is not None:
            self.logger.info(f'env file is not None, load env file from {env_file_path}')
            LoadEnv(env_file_path, log_to_file=log_to_file).load()

    def expand_vars(self, config):
        for k, value in config.items():
            self.logger.debug(f'Get values stored in {k}')
            if isinstance(value, dict):
                config[k] = self.expand_vars(config[k])
            else:
                config[k] = os.path.expandvars(value)
        return config

    def parse(self, config_file_path, expend_vars=True):
        self.logger.info('Read to parse config file')

        is_yaml = re.search('.y(a|A?)ml$', config_file_path)
        is_json = re.search('.json$', config_file_path)
        is_ini = re.search('.ini$', config_file_path)
        if is_yaml is not None and is_json is not None and is_ini is not None:
            self.logger.error('File name error or regular expression issue.')
            self.logger.debug(f'config file name: {config_file_path}')
            raise LogicError

        if is_yaml is not None:
            self.logger.info('Using yaml parser')
            parser = yaml_parser
        elif is_json is not None:
            self.logger.info('Using json parser')
            parser = json_parser
        elif is_ini is not None:
            self.logger.info('Using ini parser')
            parser = ini_parser
        else:
            self.logger.debug(f'Config file name: {config_file_path}')
            self.logger.error('Not implemented parser for this file extension.')
            raise NotImplementedError

        self.logger.info('check config file exist or not.')
        check_file_exist(self.logger, config_file_path)

        try:
            self.logger.info('parse config file')
            config = parser(config_file_path)
        except OSError as e:
            self.logger.error(f'OS error occurred when trying to open {config_file_path}.')
            self.logger.error(repr(e))
            raise OSError
        except Exception as e:
            self.logger.error(f'Unexpected error occurred when trying to open {config_file_path}.')
            self.logger.error(repr(e))
            raise Exception

        if expend_vars:
            self.logger.info('expand vars from config using value in environment')
            config = self.expand_vars(config)
        return config
