import json
import os
import yaml
from enum import Enum

from dotenv import load_dotenv


def ini_parser(file):
    raise NotImplementedError


def json_parser(file):
    extfile = r".json"
    if file.endswith(extfile):
        pass
    else:
        raise TypeError
    with open(file, 'r', encoding='utf8') as json_file:
        config = json.load(json_file)
    return config


def yaml_parser(file):

    extfile = r".yml"
    if file.endswith(extfile):
        pass
    else:
        raise TypeError

    with open(file, 'r', encoding='utf8') as yaml_file:
        doc = list(yaml.load_all(yaml_file, Loader=yaml.FullLoader))
    config = doc[0]
    return config


def find_project_root(root_folder_name):
    current_cwd = os.getcwd()
    cwd = current_cwd
    while not cwd.endswith(root_folder_name):
        os.chdir('..')
        cwd = os.getcwd()
        if cwd == '/':
            break
    project_root = cwd
    os.chdir(current_cwd)
    return project_root


class FileTypeConst(Enum):
    YAML = 'yaml'
    INI = 'ini'
    JSON = 'json'


class ConfigParser:
    def __init__(self, config_type):
        if config_type == FileTypeConst.INI.value:
            self.parser = ini_parser
        elif config_type == FileTypeConst.JSON.value:
            self.parser = json_parser
        elif config_type == FileTypeConst.YAML.value:
            self.parser = yaml_parser
        else:
            raise NotImplementedError()

    def expand_vars(self, config):
        for k, value in config.items():
            if isinstance(value, dict):
                config[k] = self.expand_vars(config[k])
            else:
                config[k] = os.path.expandvars(value)
        return config

    def parse(self, file, expend_vars=False):
        config = self.parser(file)
        if expend_vars:
            config = self.expand_vars(config)
        return config


def convenient_parser(project_root, config_file_path, env_file_path=None, config_type='yaml'):
    """
    Parse configs file

    :param project_root: project root folder name
    :param config_file_path: configs file path relative to project root
    :param env_file_path: env file path relative to project root
    :param config_type: confie file type, currently, support json and yaml
    :return: configs object
    """
    prj_root = find_project_root(project_root)
    config_file = os.path.join(prj_root, config_file_path)
    print(config_file)
    if env_file_path is not None:
        env_file = os.path.join(prj_root, env_file_path)
        env_file = os.path.abspath(env_file)
        load_dotenv(env_file)
    expend_vars = True
    conf_parser = ConfigParser(config_type)
    config = conf_parser.parse(config_file, expend_vars=expend_vars)
    return config
